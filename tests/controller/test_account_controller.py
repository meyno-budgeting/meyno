from datetime import date

import pytest
from sqlalchemy.orm import Session

from meyno.controller.account import (
    add_account,
    delete_account,
    get_account_by_id,
    get_account_by_name,
    update_account_name,
)
from meyno.controller.transaction import create_transaction, get_transaction_by_id
from meyno.database.models import Transaction
from meyno.exceptions.account import (
    AccountAlreadyExistsError,
    AccountNameEmptyError,
    AccountNotFoundError,
)
from meyno.schemas.transaction import TransactionCreate


def test_add_account(session: Session):
    account = add_account(session, "Checking")

    assert account.name == "Checking"
    assert account.account_id is not None

    session.expire_all()

    stored_account = get_account_by_id(session, account.account_id)

    assert stored_account is account


def test_add_account_strips_name(session: Session):
    account = add_account(session, "   Checking ")

    assert account.name == "Checking"


@pytest.mark.parametrize("name", ["", "   "])
def test_add_account_empty_name(session: Session, name: str):
    with pytest.raises(AccountNameEmptyError):
        add_account(session, name)


@pytest.mark.parametrize("name", ["Checking", "    Checking   "])
def test_add_duplicate_account(session: Session, name: str):
    add_account(session, "Checking")

    with pytest.raises(AccountAlreadyExistsError):
        add_account(session, name)


def test_get_account_by_id(session: Session):
    account = add_account(session, "Checking")

    session.expire_all()

    result = get_account_by_id(session, account.account_id)

    assert result is account


def test_get_account_by_id_not_found(session: Session):
    with pytest.raises(AccountNotFoundError):
        get_account_by_id(session, 999)


def test_get_account_by_name(session: Session):
    account = add_account(session, "Checking")

    session.expire_all()

    result = get_account_by_name(session, "Checking")

    assert result is account


def test_get_account_by_name_not_found(session: Session):
    with pytest.raises(AccountNotFoundError):
        get_account_by_name(session, "Fycytviytviyuvik")


@pytest.mark.parametrize("name", ["", "    "])
def test_get_account_by_name_empty_name(session: Session, name: str):
    with pytest.raises(AccountNameEmptyError):
        get_account_by_name(session, name)


def test_get_account_by_name_strips_name(session: Session):
    account = add_account(session, "Checking")

    session.expire_all()

    result = get_account_by_name(session, "    Checking   ")

    assert result is account


def test_update_account_name(session: Session):
    account = add_account(session, "Checking")

    session.expire_all()

    result = update_account_name(session, account, "Savings")

    assert result is account
    assert account.name == "Savings"


@pytest.mark.parametrize("name", ["", "    "])
def test_update_account_name_empty_name(session: Session, name: str):
    account = add_account(session, "Checking")

    with pytest.raises(AccountNameEmptyError):
        update_account_name(session, account, name)


def test_update_account_name_duplicate(session: Session):
    account = add_account(session, "Checking")
    add_account(session, "Savings")

    with pytest.raises(AccountAlreadyExistsError):
        update_account_name(session, account, "Savings")


@pytest.mark.parametrize("name", ["Checking", "  Checking    "])
def test_update_account_name_same_name(session, name):
    account = add_account(session, "Checking")

    result = update_account_name(session, account, name)

    assert result is account
    assert account.name == "Checking"


def test_delete_account(session):
    account = add_account(session, "Checking")

    transaction = create_transaction(
        session,
        TransactionCreate(account_id=account.account_id, amount=1000),
    )

    delete_account(session, account)

    with pytest.raises(AccountNotFoundError):
        get_account_by_id(session, account.account_id)

    assert get_transaction_by_id(session, transaction.transaction_id) is None


def test_delete_account_preserves_incoming_transfer_transaction(
    session: Session,
):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")

    # TODO(ChaoticDefense): Make these use create_transaction
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

    session.add_all([checking_transaction, savings_transaction])
    checking_transaction.transfer_transaction = savings_transaction
    session.commit()

    savings_transaction_id = savings_transaction.transaction_id

    delete_account(session, checking)

    stored_savings_transaction = session.get(
        Transaction,
        savings_transaction_id,
    )

    assert stored_savings_transaction is not None
    assert stored_savings_transaction.transfer_transaction is None


def test_delete_account_preserves_outgoing_transfer_transaction(
    session: Session,
):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")

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

    session.add_all([checking_transaction, savings_transaction])
    checking_transaction.transfer_transaction = savings_transaction
    session.commit()

    checking_transaction_id = checking_transaction.transaction_id

    delete_account(session, savings)

    stored_checking_transaction = session.get(
        Transaction,
        checking_transaction_id,
    )

    assert stored_checking_transaction is not None
    assert stored_checking_transaction.transfer_transaction is None
