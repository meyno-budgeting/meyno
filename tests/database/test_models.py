from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from meyno.database.models import (
    Account,
    Category,
    Payee,
    Transaction,
    TransactionSplit,
)


# Persistence
def test_insert_and_query(session):
    account = Account(name="Test Account")
    category = Category(name="Groceries")
    payee = Payee(name="Supermarket")

    session.add_all([account, category, payee])
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=payee.payee_id,
        date=date(2026, 8, 17),
        amount=5000,
        notes="Grocery shopping",
    )

    session.add(transaction)
    session.commit()

    splits = [
        TransactionSplit(
            transaction_id=transaction.transaction_id,
            category_id=category.category_id,
            amount=3000,
        ),
        TransactionSplit(
            transaction_id=transaction.transaction_id,
            category_id=None,
            amount=2000,
        ),
    ]

    session.add_all(splits)
    session.commit()

    session.expire_all()

    queried_transaction = session.get(
        Transaction,
        transaction.transaction_id,
    )

    assert queried_transaction is not None
    assert queried_transaction.amount == 5000
    assert queried_transaction.notes == "Grocery shopping"
    assert len(queried_transaction.splits) == 2

    queried_splits = {split.amount: split for split in queried_transaction.splits}

    assert queried_splits[3000].category_id == category.category_id
    assert queried_splits[2000].category_id is None


def test_multiple_splits_same_category(session):
    account = Account(name="Checking")
    category_savings = Category(name="Savings")
    category_groceries = Category(name="Groceries")
    payee = Payee(name="Test Payee")

    session.add_all(
        [
            account,
            category_savings,
            category_groceries,
            payee,
        ]
    )
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=payee.payee_id,
        date=date(2026, 8, 18),
        amount=14000,
    )

    session.add(transaction)
    session.commit()

    splits = [
        TransactionSplit(
            transaction_id=transaction.transaction_id,
            category_id=category_savings.category_id,
            amount=10000,
        ),
        TransactionSplit(
            transaction_id=transaction.transaction_id,
            category_id=category_groceries.category_id,
            amount=3000,
        ),
        TransactionSplit(
            transaction_id=transaction.transaction_id,
            category_id=category_savings.category_id,
            amount=1000,
        ),
    ]

    session.add_all(splits)
    session.commit()

    session.expire_all()

    queried_transaction = session.get(
        Transaction,
        transaction.transaction_id,
    )

    assert queried_transaction is not None
    assert len(queried_transaction.splits) == 3

    savings_splits = [
        split
        for split in queried_transaction.splits
        if split.category_id == category_savings.category_id
    ]

    assert len(savings_splits) == 2
    assert sorted(split.amount for split in savings_splits) == [1000, 10000]


def test_uncategorized_split(session):
    account = Account(name="Checking")
    payee = Payee(name="Unknown Payee")

    session.add_all([account, payee])
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=payee.payee_id,
        date=date(2026, 8, 18),
        amount=5000,
    )

    session.add(transaction)
    session.commit()

    split = TransactionSplit(
        transaction_id=transaction.transaction_id,
        category_id=None,
        amount=5000,
    )

    session.add(split)
    session.commit()

    session.expire_all()

    queried_transaction = session.get(
        Transaction,
        transaction.transaction_id,
    )

    assert queried_transaction is not None
    assert len(queried_transaction.splits) == 1

    queried_split = queried_transaction.splits[0]

    assert queried_split.category_id is None
    assert queried_split.category is None
    assert queried_split.amount == 5000


# Relationships
def test_relationships_work_in_both_directions(session):
    account = Account(name="Checking")
    category = Category(name="Groceries")
    payee = Payee(name="Walmart")

    transaction = Transaction(
        account=account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=5000,
    )

    split = TransactionSplit(
        transaction=transaction,
        category=category,
        amount=5000,
    )

    session.add(transaction)
    session.commit()
    session.expire_all()

    queried_transaction = session.get(
        Transaction,
        transaction.transaction_id,
    )
    queried_account = session.get(
        Account,
        account.account_id,
    )
    queried_payee = session.get(
        Payee,
        payee.payee_id,
    )
    queried_split = session.get(
        TransactionSplit,
        split.transaction_split_id,
    )
    queried_category = session.get(
        Category,
        category.category_id,
    )

    assert queried_transaction is not None
    assert queried_account is not None
    assert queried_payee is not None
    assert queried_split is not None
    assert queried_category is not None

    assert queried_transaction.account is queried_account
    assert queried_transaction in queried_account.transactions

    assert queried_transaction.payee is queried_payee
    assert queried_transaction in queried_payee.transactions

    assert queried_split.transaction is queried_transaction
    assert queried_split in queried_transaction.splits

    assert queried_split.category is queried_category
    assert queried_split in queried_category.transaction_splits


# Transfers
def test_transfer_transaction(session):
    checking_account = Account(name="Checking")
    savings_account = Account(name="Savings")
    payee = Payee(name="Chase")

    session.add_all(
        [
            checking_account,
            savings_account,
            payee,
        ]
    )
    session.commit()

    outgoing_transaction = Transaction(
        account=checking_account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=-10000,
        notes="Moving some savings over",
    )

    incoming_transaction = Transaction(
        account=savings_account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=10000,
        notes="Moving some savings over",
    )

    session.add_all(
        [
            outgoing_transaction,
            incoming_transaction,
        ]
    )
    session.commit()

    outgoing_transaction.transfer_transaction = incoming_transaction
    incoming_transaction.transfer_transaction = outgoing_transaction

    session.commit()
    session.expire_all()

    queried_outgoing = session.get(
        Transaction,
        outgoing_transaction.transaction_id,
    )
    queried_incoming = session.get(
        Transaction,
        incoming_transaction.transaction_id,
    )

    assert queried_outgoing is not None
    assert queried_incoming is not None

    assert queried_outgoing.transfer_transaction_id == queried_incoming.transaction_id
    assert queried_incoming.transfer_transaction_id == queried_outgoing.transaction_id

    assert queried_outgoing.transfer_transaction is queried_incoming
    assert queried_incoming.transfer_transaction is queried_outgoing

    assert queried_outgoing.payee_id == queried_incoming.payee_id
    assert queried_outgoing.payee.name == "Chase"
    assert queried_incoming.payee.name == "Chase"

    assert queried_outgoing.amount == -10000
    assert queried_incoming.amount == 10000


def test_transfer_linked_before_flush(session):
    checking_account = Account(name="Checking")
    savings_account = Account(name="Savings")
    payee = Payee(name="Chase")

    session.add_all(
        [
            checking_account,
            savings_account,
            payee,
        ]
    )
    session.commit()

    outgoing_transaction = Transaction(
        account=checking_account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=-10000,
    )

    incoming_transaction = Transaction(
        account=savings_account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=10000,
    )

    outgoing_transaction.transfer_transaction = incoming_transaction
    incoming_transaction.transfer_transaction = outgoing_transaction

    session.add_all(
        [
            outgoing_transaction,
            incoming_transaction,
        ]
    )

    session.flush()

    assert outgoing_transaction.transaction_id is not None
    assert incoming_transaction.transaction_id is not None
    assert (
        outgoing_transaction.transfer_transaction_id
        == incoming_transaction.transaction_id
    )
    assert (
        incoming_transaction.transfer_transaction_id
        == outgoing_transaction.transaction_id
    )


def test_transaction_cannot_transfer_to_itself(session):
    account = Account(name="Checking")
    payee = Payee(name="Test Payee")

    session.add_all([account, payee])
    session.commit()

    transaction = Transaction(
        account=account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=5000,
    )

    session.add(transaction)
    session.flush()

    transaction.transfer_transaction = transaction

    with pytest.raises(IntegrityError):
        session.flush()


def test_delete_outgoing_transfer_deletes_incoming(session):
    checking_account = Account(name="Checking")
    savings_account = Account(name="Savings")
    payee = Payee(name="Chase")

    outgoing_transaction = Transaction(
        account=checking_account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=-10000,
    )

    incoming_transaction = Transaction(
        account=savings_account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=10000,
    )

    outgoing_transaction.transfer_transaction = incoming_transaction
    incoming_transaction.transfer_transaction = outgoing_transaction

    session.add_all([outgoing_transaction, incoming_transaction])
    session.commit()

    outgoing_id = outgoing_transaction.transaction_id
    incoming_id = incoming_transaction.transaction_id

    session.delete(outgoing_transaction)
    session.commit()
    session.expire_all()

    assert session.get(Transaction, outgoing_id) is None
    assert session.get(Transaction, incoming_id) is None


def test_delete_incoming_transfer_deletes_outgoing(session):
    checking_account = Account(name="Checking")
    savings_account = Account(name="Savings")
    payee = Payee(name="Chase")

    outgoing_transaction = Transaction(
        account=checking_account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=-10000,
    )

    incoming_transaction = Transaction(
        account=savings_account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=10000,
    )

    outgoing_transaction.transfer_transaction = incoming_transaction
    incoming_transaction.transfer_transaction = outgoing_transaction

    session.add_all(
        [
            outgoing_transaction,
            incoming_transaction,
        ]
    )
    session.commit()

    outgoing_id = outgoing_transaction.transaction_id
    incoming_id = incoming_transaction.transaction_id

    session.delete(incoming_transaction)
    session.commit()
    session.expire_all()

    assert session.get(Transaction, outgoing_id) is None
    assert session.get(Transaction, incoming_id) is None


# Cascade behavior
def test_delete_transaction_cascades_to_splits(session):
    account = Account(name="Checking")
    category = Category(name="Groceries")
    payee = Payee(name="Walmart")

    transaction = Transaction(
        account=account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=5000,
    )

    split = TransactionSplit(
        transaction=transaction,
        category=category,
        amount=5000,
    )

    session.add(transaction)
    session.commit()

    transaction_id = transaction.transaction_id
    split_id = split.transaction_split_id

    session.delete(transaction)
    session.commit()
    session.expire_all()

    assert session.get(Transaction, transaction_id) is None
    assert session.get(TransactionSplit, split_id) is None


def test_removing_split_from_collection_orphans_it(session):
    account = Account(name="Checking")
    category = Category(name="Groceries")
    payee = Payee(name="Walmart")

    transaction = Transaction(
        account=account,
        payee=payee,
        date=date(2026, 8, 18),
        amount=5000,
    )

    split = TransactionSplit(
        transaction=transaction,
        category=category,
        amount=5000,
    )

    session.add(transaction)
    session.commit()

    split_id = split.transaction_split_id

    transaction.splits.remove(split)

    session.commit()
    session.expire_all()

    assert session.get(TransactionSplit, split_id) is None


# Foreign-key constraints
def test_foreign_key_violation_for_account(session):
    payee = Payee(name="Test Payee")
    session.add(payee)
    session.commit()

    transaction = Transaction(
        account_id=999,
        payee_id=payee.payee_id,
        date=date(2026, 8, 18),
        amount=5000,
    )

    session.add(transaction)

    with pytest.raises(IntegrityError):
        session.flush()


def test_foreign_key_violation_for_payee(session):
    account = Account(name="Checking")
    session.add(account)
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=999,
        date=date(2026, 8, 18),
        amount=5000,
    )

    session.add(transaction)

    with pytest.raises(IntegrityError):
        session.flush()


def test_foreign_key_violation_for_category(session):
    account = Account(name="Checking")
    payee = Payee(name="Test Payee")

    session.add_all([account, payee])
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=payee.payee_id,
        date=date(2026, 8, 18),
        amount=5000,
    )

    session.add(transaction)
    session.commit()

    split = TransactionSplit(
        transaction_id=transaction.transaction_id,
        category_id=999,
        amount=5000,
    )

    session.add(split)

    with pytest.raises(IntegrityError):
        session.flush()


# NOT NULL constraints
def test_account_name_not_null(session):
    account = Account(name=None)

    session.add(account)

    with pytest.raises(IntegrityError):
        session.flush()


def test_payee_name_not_null(session):
    payee = Payee(name=None)

    session.add(payee)

    with pytest.raises(IntegrityError):
        session.flush()


def test_category_name_not_null(session):
    category = Category(name=None)

    session.add(category)

    with pytest.raises(IntegrityError):
        session.flush()


def test_transaction_split_id_not_null(session):
    split = TransactionSplit(transaction_id=None)

    session.add(split)

    with pytest.raises(IntegrityError):
        session.flush()


def test_transaction_date_not_null(session):
    account = Account(name="Checking")
    payee = Payee(name="Test Payee")

    session.add_all([account, payee])
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=payee.payee_id,
        date=None,
        amount=5000,
    )

    session.add(transaction)

    with pytest.raises(IntegrityError):
        session.flush()


def test_transaction_amount_not_null(session):
    account = Account(name="Checking")
    payee = Payee(name="Test Payee")

    session.add_all([account, payee])
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=payee.payee_id,
        date=date(2026, 8, 18),
        amount=None,
    )

    session.add(transaction)

    with pytest.raises(IntegrityError):
        session.flush()


def test_transaction_split_amount_not_null(session):
    account = Account(name="Checking")
    payee = Payee(name="Test Payee")

    session.add_all([account, payee])
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=payee.payee_id,
        date=date(2026, 8, 18),
        amount=5000,
    )

    session.add(transaction)
    session.commit()

    split = TransactionSplit(
        transaction_id=transaction.transaction_id,
        amount=None,
    )

    session.add(split)

    with pytest.raises(IntegrityError):
        session.flush()


# UNIQUE constraints
def test_account_name_unique(session):
    session.add(Account(name="Checking"))
    session.commit()

    session.add(Account(name="Checking"))

    with pytest.raises(IntegrityError):
        session.flush()


def test_payee_name_unique(session):
    session.add(Payee(name="Walmart"))
    session.commit()

    session.add(Payee(name="Walmart"))

    with pytest.raises(IntegrityError):
        session.flush()


def test_category_name_unique(session):
    session.add(Category(name="Walmart"))
    session.commit()

    session.add(Category(name="Walmart"))

    with pytest.raises(IntegrityError):
        session.flush()
