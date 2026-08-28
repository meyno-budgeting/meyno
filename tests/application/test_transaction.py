import datetime

from sqlalchemy.orm import Session

from meyno.application.account import add_account_to_database
from meyno.application.category import create_category
from meyno.application.payee import create_payee
from meyno.application.transaction import (
    create_default_transaction,
    create_default_transaction_split,
    delete_transaction,
    delete_transaction_split,
    get_transaction_by_id,
    get_transaction_split_by_id,
    update_transaction_account,
    update_transaction_amount,
    update_transaction_date,
    update_transaction_notes,
    update_transaction_payee,
    update_transaction_split_amount,
    update_transaction_split_category,
    update_transaction_splits,
)
from meyno.database.models import TransactionSplit


def test_create_default_transaction(session: Session):
    expected_date = datetime.datetime.now().astimezone().date()

    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(session, transaction.transaction_id)

    assert stored_transaction is not None
    assert stored_transaction.account is account
    assert stored_transaction.payee is None
    assert stored_transaction.date == expected_date
    assert stored_transaction.amount == 0
    assert stored_transaction.notes is None
    assert stored_transaction.transaction_id is not None

    assert len(stored_transaction.splits) == 1
    assert stored_transaction.splits[0].transaction is stored_transaction
    assert stored_transaction.splits[0].category is None
    assert stored_transaction.splits[0].amount == stored_transaction.amount
    assert stored_transaction.splits[0].transaction_split_id is not None


def test_get_transaction_by_id(session: Session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.transaction_id == transaction.transaction_id


def test_get_transaction_by_id_not_found(session):
    result = get_transaction_by_id(session, 999)

    assert result is None


def test_update_transaction_date(session: Session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)

    session.flush()

    new_date = datetime.date(2026, 8, 25)

    update_transaction_date(transaction, new_date)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.date == new_date


def test_update_transaction_account(session: Session):
    checking_account = add_account_to_database(session, "Checking")
    savings_account = add_account_to_database(session, "Savings")

    transaction = create_default_transaction(session, checking_account)

    session.flush()

    update_transaction_account(transaction, savings_account)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.account is savings_account


def test_update_transaction_payee(session: Session):
    checking_account = add_account_to_database(session, "Checking")
    new_payee = create_payee(session, "Walmart")

    transaction = create_default_transaction(session, checking_account)

    session.flush()

    update_transaction_payee(transaction, new_payee)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.payee is new_payee


def test_update_transaction_amount(session: Session):
    checking_account = add_account_to_database(session, "Checking")
    new_amount = 1000

    transaction = create_default_transaction(session, checking_account)

    session.flush()

    update_transaction_amount(transaction, new_amount)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.amount == new_amount


def test_update_transaction_notes(session: Session):
    checking_account = add_account_to_database(session, "Checking")
    new_notes = "This is a note"

    transaction = create_default_transaction(session, checking_account)

    session.flush()

    update_transaction_notes(transaction, new_notes)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.notes == new_notes


def test_update_transaction_splits(session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)

    update_transaction_splits(transaction, [])

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert len(stored_transaction.splits) == 0


def test_update_transaction_splits_none(session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)

    update_transaction_splits(transaction, None)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert len(stored_transaction.splits) == 0


# TODO(ChaoticDefense): Move this test to controller layer and make test for
# converting from transfer to transaction
# def test_convert_transaction_to_transfer(session):
#     checking_account = create_account(session, "Checking")
#     savings_account = create_account(session, "Savings")
#     amount = 500

#     transaction = create_default_transaction(session, checking_account)
#     transaction = update_transaction_amount(transaction, amount)

#     session.flush()

#     convert_transaction_to_transfer(session, transaction, savings_account)

#     session.commit()
#     session.expire_all()

#     stored_transaction = get_transaction_by_id(session, transaction.transaction_id)

#     assert stored_transaction is not None
#     assert stored_transaction.amount == 500
#     assert stored_transaction.account is checking_account
#     assert stored_transaction.transaction_id == transaction.transaction_id
#     assert len(stored_transaction.splits) == 0

#     assert stored_transaction.transfer_transaction is not None
#     assert stored_transaction.transfer_transaction.amount == -500
#     assert stored_transaction.transfer_transaction.account is savings_account
#     assert len(stored_transaction.transfer_transaction.splits) == 0


def test_delete_transaction(session: Session):
    account = add_account_to_database(session, "Checking")
    date = datetime.date(2026, 8, 24)
    amount = -500

    transaction = create_default_transaction(session, account)
    transaction = update_transaction_date(transaction, date)
    transaction = update_transaction_amount(transaction, amount)

    session.flush()

    transaction_id = transaction.transaction_id

    delete_transaction(session, transaction)

    session.commit()
    session.expire_all()

    assert get_transaction_by_id(session, transaction_id) is None


# TODO(ChaoticDefense): Move this test to controller layer
# def test_delete_transaction_deletes_transfer_transaction(session: Session):
#     checking = create_account(session, "Checking")
#     savings = create_account(session, "Savings")

#     checking_transaction = Transaction(
#         account=checking,
#         date=datetime.date(2026, 8, 24),
#         amount=-500,
#     )

#     savings_transaction = Transaction(
#         account=savings,
#         date=datetime.date(2026, 8, 24),
#         amount=500,
#     )

#     checking_transaction.transfer_transaction = savings_transaction

#     session.add_all([checking_transaction, savings_transaction])
#     session.flush()

#     checking_transaction_id = checking_transaction.transaction_id
#     savings_transaction_id = savings_transaction.transaction_id

#     delete_transaction(session, checking_transaction)

#     session.commit()
#     session.expire_all()

#     assert get_transaction_by_id(session, checking_transaction_id) is None
#     assert get_transaction_by_id(session, savings_transaction_id) is None


def test_create_default_transaction_split(session: Session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)
    update_transaction_amount(transaction, 1000)

    new_split = create_default_transaction_split(session, transaction)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(session, transaction.transaction_id)

    assert len(stored_transaction.splits) == 2
    assert stored_transaction.splits[1] is new_split
    assert stored_transaction.splits[1].transaction is stored_transaction
    assert stored_transaction.splits[1].category is None
    assert stored_transaction.splits[1].amount == 0
    assert stored_transaction.splits[1].transaction_split_id is not None


def test_get_transaction_split_by_id(session: Session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)

    session.commit()
    session.expire_all()

    split_id = transaction.splits[0].transaction_split_id

    stored_transaction_split = get_transaction_split_by_id(
        session,
        split_id,
    )

    assert stored_transaction_split is not None
    assert stored_transaction_split.transaction is transaction
    assert stored_transaction_split.transaction_split_id == split_id


def test_get_transaction_split_by_id_not_found(session: Session):
    assert get_transaction_split_by_id(session, 9999) is None


def test_update_transaction_split_category(session: Session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)
    new_category = create_category(session, "Groceries")

    session.flush()

    split = transaction.splits[0]

    update_transaction_split_category(split, new_category)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert len(stored_transaction.splits) == 1
    assert stored_transaction.splits[0].category is new_category


def test_update_transaction_split_amount(session: Session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)
    new_amount = 8000

    session.flush()

    split = transaction.splits[0]

    update_transaction_split_amount(split, new_amount)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert len(stored_transaction.splits) == 1
    assert stored_transaction.splits[0].amount == 8000

    assert stored_transaction.amount == 0


def test_delete_transaction_split(session: Session):
    account = add_account_to_database(session, "Checking")
    transaction = create_default_transaction(session, account)
    new_split = create_default_transaction_split(session, transaction)

    session.flush()

    default_split_id = transaction.splits[0].transaction_split_id
    new_split_id = new_split.transaction_split_id

    delete_transaction_split(session, new_split)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id(session, transaction.transaction_id)
    queried_split = session.get(TransactionSplit, new_split_id)
    remaining_split = session.get(TransactionSplit, default_split_id)

    assert stored_transaction is not None
    assert queried_split is None
    assert remaining_split is not None
    assert len(stored_transaction.splits) == 1
