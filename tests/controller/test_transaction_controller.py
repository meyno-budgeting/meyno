import datetime

import pytest
from sqlalchemy.orm import Session

from meyno.controller.account import add_account
from meyno.controller.payee import add_payee
from meyno.controller.transaction import (
    add_transaction,
    add_transfer,
    convert_transaction_to_transfer,
    get_all_transactions,
    get_all_transactions_for_account,
    get_transaction_by_id,
    update_transaction,
)
from meyno.exceptions.transaction import (
    InvalidTransactionError,
    InvalidTransferCreateError,
)
from meyno.schemas.transaction import (
    TransactionCreate,
    TransactionSplitCreate,
    TransactionUpdate,
    TransferCreate,
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

    session.expire_all()

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

    session.expire_all()

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

    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transaction.transaction_id,
    )

    assert len(stored_transaction.splits) == 2
    assert stored_transaction.splits[0].amount == 3000
    assert stored_transaction.splits[1].amount == 5000
    assert (
        sum(split.amount for split in stored_transaction.splits)
        == stored_transaction.amount
    )


def test_add_transaction_invalid_empty_splits(session: Session):
    account = add_account(session, "Checking")
    splits = []

    transaction_data = TransactionCreate(
        account_id=account.account_id,
        amount=8000,
        splits=splits,
    )

    with pytest.raises(
        InvalidTransactionError,
        match="Transaction is not part of a valid transfer!",
    ):
        add_transaction(session, transaction_data)

    transactions = get_all_transactions(session)

    assert len(transactions) == 0


def test_add_transaction_invalid_splits_amount(session: Session):
    account = add_account(session, "Checking")
    splits = [TransactionSplitCreate(amount=1000), TransactionSplitCreate(amount=500)]

    transaction_data = TransactionCreate(
        account_id=account.account_id,
        amount=8000,
        splits=splits,
    )

    with pytest.raises(
        InvalidTransactionError,
        match="Splits total does not match Transaction amount!",
    ):
        add_transaction(session, transaction_data)

    transactions = get_all_transactions(session)

    assert len(transactions) == 0


def test_add_transfer(session: Session):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")

    transfer_data = TransferCreate(
        outgoing_account_id=checking.account_id,
        incoming_account_id=savings.account_id,
        amount=500,
    )

    transfer = add_transfer(session, transfer_data)

    session.expire_all()

    stored_transaction = get_transaction_by_id(
        session,
        transfer.transaction_id,
    )

    assert stored_transaction is transfer
    assert len(stored_transaction.splits) == 0
    assert stored_transaction.account is checking
    assert stored_transaction.amount == -500

    assert stored_transaction.transfer_transaction is not None
    assert len(stored_transaction.transfer_transaction.splits) == 0
    assert stored_transaction.transfer_transaction.account is savings
    assert stored_transaction.transfer_transaction.amount == 500


def test_add_transaction_same_account(session: Session):
    checking = add_account(session, "Checking")

    with pytest.raises(
        InvalidTransferCreateError,
        match="Outgoing and incoming accounts must be different",
    ):
        TransferCreate(
            outgoing_account_id=checking.account_id,
            incoming_account_id=checking.account_id,
            amount=500,
        )


def test_updating_transfer_with_splits(session: Session):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")

    transfer_data = TransferCreate(
        outgoing_account_id=checking.account_id,
        incoming_account_id=savings.account_id,
        amount=500,
    )

    transfer = add_transfer(session, transfer_data)

    with pytest.raises(
        InvalidTransactionError,
        match="A transfer cannot have splits!",
    ):
        update_transaction(
            session,
            transfer,
            TransactionUpdate(
                splits=[TransactionSplitCreate(amount=-500)],
            ),
        )


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


def test_get_all_transactions(session: Session):
    result = get_all_transactions(session)

    assert len(result) == 0

    account = add_account(session, "Checking")

    transaction_1 = add_transaction(
        session, TransactionCreate(account_id=account.account_id)
    )

    transaction_2 = add_transaction(
        session, TransactionCreate(account_id=account.account_id)
    )

    result = get_all_transactions(session)

    assert len(result) == 2
    assert result[0] is transaction_1
    assert result[1] is transaction_2


def test_get_all_transactions_for_account(session: Session):
    account = add_account(session, "Checking")

    result = get_all_transactions_for_account(session, account)

    assert len(result) == 0

    transaction_1 = add_transaction(
        session, TransactionCreate(account_id=account.account_id)
    )

    transaction_2 = add_transaction(
        session, TransactionCreate(account_id=account.account_id)
    )

    result = get_all_transactions_for_account(session, account)

    assert len(result) == 2
    assert result[0] is transaction_1
    assert result[1] is transaction_2
