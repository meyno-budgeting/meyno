import datetime

from sqlalchemy.orm import Session

from meyno.controller.account import add_account
from meyno.controller.payee import add_payee
from meyno.controller.transaction import add_transaction, get_transaction_by_id
from meyno.schemas.transaction import (
    TransactionCreate,
    TransactionSplitCreate,
    TransactionUpdate,
)
from meyno.utils import get_local_todays_date


def test_add_transaction(session: Session):
    account = add_account(session, "Checking")
    payee = add_payee(session, "Walmart")

    transaction_data = TransactionCreate(
        date=datetime.date(2026, 8, 25),
        account_id=account.account_id,
        amount=-5000,
        payee_id=payee.payee_id,
        notes="Groceries",
    )

    transaction = add_transaction(session, transaction_data)

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.transaction_id is not None
    assert stored_transaction.date == transaction_data.date
    assert stored_transaction.account_id == transaction_data.account_id
    assert stored_transaction.amount == transaction_data.amount
    assert stored_transaction.payee_id == transaction_data.payee_id
    assert stored_transaction.notes == transaction_data.notes


def test_add_transaction_defaults(session: Session):
    account = add_account(session, "Checking")
    today = get_local_todays_date()

    default_transaction_data = TransactionCreate(
        account_id=account.account_id,
    )

    transaction = add_transaction(session, default_transaction_data)

    assert transaction.date == default_transaction_data.date
    assert transaction.date == today
    assert transaction.amount == 0
    assert transaction.payee_id is None
    assert transaction.notes is None


def test_add_transaction_with_valid_splits(session: Session):
    account = add_account(session, "Checking")

    splits = [TransactionSplitCreate(amount=3000), TransactionSplitCreate(amount=5000)]

    transaction_data = TransactionCreate(
        account_id=account.account_id,
        amount=8000,
        splits=splits,
    )

    transaction = add_transaction(session, transaction_data)

    assert len(transaction.splits) == 2
    assert transaction.splits[0].amount == 3000
    assert transaction.splits[1].amount == 5000
    assert sum(split.amount for split in transaction.splits)


def test_get_transaction_by_id(session: Session):
    account = add_account(session, "Checking")

    transaction = add_transaction(
        session, TransactionCreate(account_id=account.account_id)
    )

    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.transaction_id == transaction.transaction_id
