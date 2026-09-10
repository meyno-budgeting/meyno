import datetime

import pytest
from sqlalchemy.orm import Session

from meyno.controller.account import add_account
from meyno.controller.category import add_category
from meyno.controller.payee import add_payee
from meyno.controller.transaction import (
    add_split_to_transaction,
    add_transaction,
    add_transfer,
    convert_transaction_to_transfer,
    convert_transfer_to_transaction,
    delete_transaction,
    get_all_transactions,
    get_all_transactions_for_account,
    get_transaction_by_id,
    update_transaction,
)
from meyno.exceptions.transaction import (
    InvalidTransactionError,
    InvalidTransferCreateError,
    TransactionConversionError,
    TransactionNotFoundError,
    TransferConversionError,
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
        left_side_account_id=checking.account_id,
        right_side_account_id=savings.account_id,
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
    assert stored_transaction.amount == 500

    assert stored_transaction.transfer_right_side is not None
    assert len(stored_transaction.transfer_right_side.splits) == 0
    assert stored_transaction.transfer_right_side.account is savings
    assert stored_transaction.transfer_right_side.amount == -500


def test_add_transfer_same_account(session: Session):
    checking = add_account(session, "Checking")

    with pytest.raises(
        InvalidTransferCreateError,
        match="Outgoing and incoming accounts must be different",
    ):
        TransferCreate(
            left_side_account_id=checking.account_id,
            right_side_account_id=checking.account_id,
            amount=500,
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


def test_updating_transfer_with_splits(session: Session):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")

    transfer_data = TransferCreate(
        left_side_account_id=checking.account_id,
        right_side_account_id=savings.account_id,
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


def test_update_transaction(session: Session):
    account = add_account(session, "Checking")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=account.account_id,
            amount=1000,
            notes="Original",
        ),
    )

    update = TransactionUpdate(
        notes="Updated",
        date=datetime.date(2026, 1, 15),
    )

    result = update_transaction(session, transaction, update)

    assert result is transaction
    assert transaction.notes == "Updated"
    assert transaction.date == datetime.date(2026, 1, 15)
    assert transaction.amount == 1000


def test_update_transaction_amount_single_split(session: Session):
    account = add_account(session, "Checking")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=account.account_id,
            amount=1000,
        ),
    )

    update_transaction(
        session,
        transaction,
        TransactionUpdate(amount=1500),
    )

    assert transaction.amount == 1500
    assert len(transaction.splits) == 1
    assert transaction.splits[0].amount == 1500


def test_update_transaction_amount_multiple_splits_increasing(session: Session):
    account = add_account(session, "Checking")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=account.account_id,
            amount=100,
            splits=[
                TransactionSplitCreate(amount=60),
                TransactionSplitCreate(amount=40),
            ],
        ),
    )

    update_transaction(
        session,
        transaction,
        TransactionUpdate(amount=125),
    )

    assert transaction.amount == 125
    assert [split.amount for split in transaction.splits] == [60, 40, 25]


def test_update_transaction_amount_multiple_splits_decreasing(session: Session):
    account = add_account(session, "Checking")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=account.account_id,
            amount=100,
            splits=[
                TransactionSplitCreate(amount=60),
                TransactionSplitCreate(amount=40),
            ],
        ),
    )

    update_transaction(
        session,
        transaction,
        TransactionUpdate(amount=75),
    )

    assert transaction.amount == 75
    assert [split.amount for split in transaction.splits] == [60, 40, -25]


def test_update_transfer_left_side_amount(session: Session):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")
    old_amount = 1000
    new_amount = 2000

    left_side = add_transfer(
        session,
        TransferCreate(
            left_side_account_id=checking.account_id,
            right_side_account_id=savings.account_id,
            amount=old_amount,
        ),
    )

    update_transaction(
        session,
        left_side,
        TransactionUpdate(amount=new_amount),
    )

    assert left_side.amount == 2000
    assert left_side.transfer_right_side.amount == -2000


def test_update_transfer_right_side_amount(session: Session):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")
    old_amount = 1000
    new_amount = 2000

    left_side = add_transfer(
        session,
        TransferCreate(
            left_side_account_id=checking.account_id,
            right_side_account_id=savings.account_id,
            amount=old_amount,
        ),
    )

    right_side = left_side.transfer_right_side

    update_transaction(
        session,
        right_side,
        TransactionUpdate(amount=new_amount),
    )

    assert left_side.amount == -2000
    assert left_side.transfer_right_side.amount == 2000


def test_delete_transaction(session: Session):
    account = add_account(session, "Checking")
    transaction = add_transaction(
        session,
        TransactionCreate(account_id=account.account_id, amount=10000),
    )

    transaction_id = transaction.transaction_id

    delete_transaction(session, transaction)

    session.expire_all()

    with pytest.raises(TransactionNotFoundError):
        get_transaction_by_id(session, transaction_id)


def test_delete_transfer_left_side(session: Session):
    left_account = add_account(session, "Checking")
    right_account = add_account(session, "Savings")

    left_side = add_transfer(
        session,
        TransferCreate(
            left_side_account_id=left_account.account_id,
            right_side_account_id=right_account.account_id,
            amount=10000,
        ),
    )

    left_transaction_id = left_side.transaction_id
    other_transaction_id = left_side.transfer_other_side.transaction_id

    delete_transaction(session, left_side)

    session.expire_all()

    with pytest.raises(TransactionNotFoundError):
        get_transaction_by_id(session, left_transaction_id)

    with pytest.raises(TransactionNotFoundError):
        get_transaction_by_id(session, other_transaction_id)


def test_delete_transfer_right_side(session: Session):
    left_account = add_account(session, "Checking")
    right_account = add_account(session, "Savings")

    left_side = add_transfer(
        session,
        TransferCreate(
            left_side_account_id=left_account.account_id,
            right_side_account_id=right_account.account_id,
            amount=10000,
        ),
    )

    other_side = left_side.transfer_other_side

    left_transaction_id = left_side.transaction_id
    other_transaction_id = other_side.transaction_id

    delete_transaction(session, other_side)

    session.expire_all()

    with pytest.raises(TransactionNotFoundError):
        get_transaction_by_id(session, left_transaction_id)

    with pytest.raises(TransactionNotFoundError):
        get_transaction_by_id(session, other_transaction_id)


def test_convert_transaction_to_transfer(session: Session):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=checking.account_id,
            amount=-500,
        ),
    )

    convert_transaction_to_transfer(session, transaction, savings)

    assert transaction.transfer_other_side is not None
    assert transaction.transfer_other_side.amount == 500
    assert transaction.transfer_other_side.transfer_other_side is transaction


def test_convert_transfer_to_transaction(session):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")

    transfer = add_transfer(
        session,
        TransferCreate(
            left_side_account_id=checking.account_id,
            right_side_account_id=savings.account_id,
            amount=-5000,
        ),
    )

    other_side_transaction_id = transfer.transfer_other_side.transaction_id

    convert_transfer_to_transaction(session, transfer)

    assert transfer.transfer_other_side is None

    with pytest.raises(TransactionNotFoundError):
        get_transaction_by_id(session, other_side_transaction_id)


def test_convert_already_transfer(session: Session):
    checking = add_account(session, "Checking")
    savings = add_account(session, "Savings")

    transfer = add_transfer(
        session,
        TransferCreate(
            left_side_account_id=checking.account_id,
            right_side_account_id=savings.account_id,
            amount=-5000,
        ),
    )

    with pytest.raises(TransactionConversionError):
        convert_transaction_to_transfer(session, transfer, checking)

    with pytest.raises(TransactionConversionError):
        convert_transaction_to_transfer(session, transfer, savings)


def test_convert_already_transaction(session: Session):
    checking = add_account(session, "Checking")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=checking.account_id,
            amount=-500,
        ),
    )

    with pytest.raises(TransferConversionError):
        convert_transfer_to_transaction(session, transaction)


def test_add_split_to_transaction_defaults(session: Session):
    checking = add_account(session, "Checking")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=checking.account_id,
            amount=-500,
        ),
    )

    new_split = add_split_to_transaction(session, transaction, TransactionSplitCreate())

    assert len(transaction.splits) == 2
    assert transaction.splits[1] is new_split
    assert transaction.splits[1].amount == 0
    assert transaction.splits[1].category is None
    assert transaction.amount == -500


def test_add_split_to_transaction(session: Session):
    checking = add_account(session, "Checking")
    category = add_category(session, "Groceries")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=checking.account_id,
            amount=-500,
        ),
    )

    new_split = add_split_to_transaction(
        session,
        transaction,
        TransactionSplitCreate(
            category_id=category.category_id,
            amount=-100,
        ),
    )

    assert len(transaction.splits) == 2
    assert transaction.splits[1] is new_split
    assert transaction.splits[1].amount == -100
    assert transaction.splits[1].category is category
    assert transaction.amount == -600
