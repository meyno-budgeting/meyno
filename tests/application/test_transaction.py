import datetime

from sqlalchemy.orm import Session

from meyno.application.account import create_account
from meyno.application.payee import create_payee
from meyno.application.transaction import (
    create_default_transaction,
    delete_transaction,
    get_transaction_by_id,
    update_transaction_account,
    update_transaction_date,
    update_transaction_payee,
)
from meyno.database.models import Transaction


def test_create_default_transaction(session: Session):
    expected_date = datetime.datetime.now().astimezone().date()

    account = create_account(session, "Checking")
    transaction = create_default_transaction(session, account)

    session.expire_all()

    stored_transaction = session.get(Transaction, transaction.transaction_id)

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
    account = create_account(session, "Checking")
    transaction = create_default_transaction(session, account)

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
    account = create_account(session, "Checking")
    transaction = create_default_transaction(session, account)

    new_date = datetime.date(2026, 8, 25)

    update_transaction_date(session, transaction, new_date)

    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.date == new_date


def test_update_transaction_account(session: Session):
    checking_account = create_account(session, "Checking")
    savings_account = create_account(session, "Savings")

    transaction = create_default_transaction(session, checking_account)

    update_transaction_account(session, transaction, savings_account)

    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.account is savings_account


def test_update_transaction_payee(session: Session):
    checking_account = create_account(session, "Checking")
    new_payee = create_payee(session, "Walmart")

    transaction = create_default_transaction(session, checking_account)

    update_transaction_payee(session, transaction, new_payee)

    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.payee is new_payee


def test_delete_transaction(session):
    account = create_account(session, "Checking")

    transaction = Transaction(
        date=datetime.date(2026, 8, 24),
        account=account,
        amount=-500,
    )

    session.add(transaction)
    session.flush()

    transaction_id = transaction.transaction_id

    delete_transaction(session, transaction)

    session.expire_all()

    assert session.get(Transaction, transaction_id) is None


def test_delete_transaction_deletes_transfer_transaction(session):
    checking = create_account(session, "Checking")
    savings = create_account(session, "Savings")

    checking_transaction = Transaction(
        account=checking,
        date=datetime.date(2026, 8, 24),
        amount=-500,
    )

    savings_transaction = Transaction(
        account=savings,
        date=datetime.date(2026, 8, 24),
        amount=500,
    )

    checking_transaction.transfer_transaction = savings_transaction

    session.add_all([checking_transaction, savings_transaction])
    session.flush()

    checking_transaction_id = checking_transaction.transaction_id
    savings_transaction_id = savings_transaction.transaction_id

    delete_transaction(session, checking_transaction)

    session.expire_all()

    assert session.get(Transaction, checking_transaction_id) is None
    assert session.get(Transaction, savings_transaction_id) is None
