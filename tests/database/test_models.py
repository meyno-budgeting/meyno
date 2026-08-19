from datetime import date

from meyno.database.models import (
    Account,
    Category,
    Payee,
    Transaction,
    TransactionSplit,
)


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

    split = TransactionSplit(
        transaction_id=transaction.transaction_id,
        category_id=category.category_id,
        amount=3000,
    )
    session.add(split)
    session.commit()

    queried_transaction = session.get(
        Transaction,
        transaction.transaction_id,
    )

    assert queried_transaction is not None
    assert queried_transaction.amount == 5000
    assert len(queried_transaction.splits) == 1
    assert queried_transaction.splits[0].amount == 3000
    
def test_multiple_splits_same_category(session):
    account = Account(name="Checking")
    category_savings = Category(name="Savings")
    category_groceries = Category(name="Groceries")
    payee = Payee(name="Test Payee")

    session.add_all([
        account,
        category_savings,
        category_groceries,
        payee,
    ])
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

    queried_transaction = session.get(
        Transaction,
        transaction.transaction_id,
    )

    assert queried_transaction is not None
    assert len(queried_transaction.splits) == 1
    assert queried_transaction.splits[0].category_id is None
    assert queried_transaction.splits[0].category is None
    assert queried_transaction.splits[0].amount == 5000
    
def test_transfer_transaction(session):
    checking_account = Account(name="Checking")
    savings_account = Account(name="Savings")
    
    payee = Payee(name="Chase")
    
    session.add_all([checking_account, savings_account, payee])
    session.commit()
    
    outgoing_transaction = Transaction(
        account = checking_account,
        payee = payee,
        date = date(2026, 8, 18),
        amount = -10000,
        notes = 'Moving some savings over'
    )
    
    incoming_transaction = Transaction(
        account = savings_account,
        payee = payee,
        date = date(2026, 8, 18),
        amount = 10000,
        notes = 'Moving some savings over'
    )
    
    session.add_all([outgoing_transaction, incoming_transaction])
    session.commit()
    
    outgoing_transaction.transfer_transaction = incoming_transaction
    incoming_transaction.transfer_transaction = outgoing_transaction
    session.commit()
    
    queried_outgoing = session.get(
        Transaction,
        outgoing_transaction.transaction_id
    )
    
    queried_incoming = session.get(
        Transaction,
        incoming_transaction.transaction_id
    )
    
    assert queried_outgoing is not None
    assert queried_outgoing.transfer_transaction_id == incoming_transaction.transaction_id
    assert queried_outgoing.transfer_transaction is incoming_transaction
    assert queried_outgoing.payee.name == "Chase"
    assert queried_outgoing.notes == "Moving some savings over"
    
    assert queried_incoming is not None
    assert queried_incoming.transfer_transaction_id == outgoing_transaction.transaction_id
    assert queried_incoming.transfer_transaction is outgoing_transaction
    assert queried_incoming.payee.name == "Chase"
    assert queried_incoming.notes == "Moving some savings over"