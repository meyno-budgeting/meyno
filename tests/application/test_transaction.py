from datetime import date

import pytest

from meyno.application.account import create_account
from meyno.application.payee import create_payee
from meyno.application.transaction import (
    Transaction,
    TransactionSplit,
    create_transaction,
    delete_transaction,
    get_transaction_by_id,
)


# FIXME Actual test
def test_create_transaction(session):
    assert True


def test_get_transaction_by_id(session):
    payee = create_payee(session, "Walmart")
    account = create_account(session, "Checking")
    transaction_date = date(2026, 8, 23)
    amount = 10000

    transaction = create_transaction(
        session,
        account=account,
        payee=payee,
        transaction_date=transaction_date,
        amount=amount,
    )

    session.commit()
    session.expire_all()

    result = get_transaction_by_id(session, transaction.transaction_id)

    assert result is not None
    assert result.account_id == account.account_id
    assert result.amount == 10000


def test_delete_transaction(session):
    account = create_account(session, "Checking")

    transaction = create_transaction(
        session,
        account=account,
        amount=-500,
    )

    transaction_id = transaction.transaction_id

    delete_transaction(session, transaction)

    session.expire_all()

    assert session.get(Transaction, transaction_id) is None


def test_delete_transaction_deletes_transfer_transaction(session):
    checking = create_account(session, "Checking")
    savings = create_account(session, "Savings")

    checking_transaction = Transaction(
        account=checking,
        date=date(2026, 8, 24),
        amount=-500,
    )

    savings_transaction = Transaction(
        account=savings,
        date=date(2026, 8, 24),
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
