import datetime

import pytest
import uuid6
from sqlalchemy.orm import Session

from meyno.application.account import add_account_to_database
from meyno.application.category import add_category_to_database
from meyno.application.payee import add_payee_to_database
from meyno.application.transaction import (
    add_split_to_transaction_in_database,
    add_transaction_to_database,
    delete_split_from_transaction_in_database,
    delete_transaction_from_database,
    get_all_transactions_from_database,
    get_split_by_id_from_database,
    get_transaction_by_id_from_database,
    update_split_in_database,
    update_transaction_in_database,
)
from meyno.schemas.transaction import (
    TransactionCreate,
    TransactionSplitCreate,
    TransactionSplitUpdate,
    TransactionUpdate,
)
from meyno.utils import get_local_todays_date


def test_add_transaction_to_database(session: Session):
    account = add_account_to_database(session, "Checking")
    payee = add_payee_to_database(session, "Walmart")

    session.commit()

    transaction_data = TransactionCreate(
        date=datetime.date(2026, 8, 25),
        account_id=account.account_id,
        amount=-5000,
        payee_id=payee.payee_id,
        notes="Groceries",
    )

    transaction = add_transaction_to_database(session, transaction_data)

    session.flush()
    session.expire_all()

    stored_transaction = get_transaction_by_id_from_database(
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


def test_add_transaction_to_database_defaults(session: Session):
    account = add_account_to_database(session, "Checking")
    today = get_local_todays_date()

    session.commit()

    transaction_data = TransactionCreate(
        account_id=account.account_id,
    )

    transaction = add_transaction_to_database(session, transaction_data)

    session.flush()

    assert transaction.date == transaction_data.date
    assert transaction.date == today
    assert transaction.amount == 0
    assert transaction.payee_id is None
    assert transaction.notes is None


def test_get_transaction_by_id(session: Session):
    account = add_account_to_database(session, "Checking")

    session.commit()

    transaction = add_transaction_to_database(
        session, TransactionCreate(account_id=account.account_id)
    )

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id_from_database(
        session,
        transaction.transaction_id,
    )

    assert stored_transaction is not None
    assert stored_transaction.transaction_id == transaction.transaction_id


def test_get_transaction_by_id_not_found(session):
    result = get_transaction_by_id_from_database(session, uuid6.uuid7())

    assert result is None


def test_get_all_transactions_from_database(session: Session):
    result = get_all_transactions_from_database(session)

    assert len(result) == 0

    account = add_account_to_database(session, "Checking")
    session.commit()

    dummy_create_data = TransactionCreate(account_id=account.account_id)

    transaction_1 = add_transaction_to_database(session, dummy_create_data)
    transaction_2 = add_transaction_to_database(session, dummy_create_data)

    session.commit()
    session.expire_all()

    result = get_all_transactions_from_database(session)

    assert len(result) == 2
    assert result[0] is transaction_1
    assert result[1] is transaction_2


def test_update_transaction_in_database(session: Session):
    checking_account = add_account_to_database(session, "Checking")
    savings_account = add_account_to_database(session, "Savings")
    old_payee = add_payee_to_database(session, "Walmart")
    new_payee = add_payee_to_database(session, "Target")

    session.commit()

    transaction_data = TransactionCreate(
        account_id=checking_account.account_id,
        amount=-5000,
        payee_id=old_payee.payee_id,
        notes="Old note",
    )
    transaction = add_transaction_to_database(session, transaction_data)

    session.flush()

    update = TransactionUpdate(
        date=datetime.date(2026, 8, 25),
        account_id=savings_account.account_id,
        amount=-7500,
        payee_id=new_payee.payee_id,
        notes="New note",
    )

    result = update_transaction_in_database(transaction, update)

    assert result is transaction
    assert transaction.date == update.date
    assert transaction.account_id == update.account_id
    assert transaction.amount == update.amount
    assert transaction.payee_id == update.payee_id
    assert transaction.notes == update.notes

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id_from_database(
        session, transaction.transaction_id
    )

    assert stored_transaction is not None
    assert stored_transaction.date == update.date
    assert stored_transaction.account_id == update.account_id
    assert stored_transaction.amount == update.amount
    assert stored_transaction.payee_id == update.payee_id
    assert stored_transaction.notes == update.notes


def test_delete_transaction_from_database(session: Session):
    account = add_account_to_database(session, "Checking")
    payee = add_payee_to_database(session, "Walmart")

    session.commit()

    transaction_data = TransactionCreate(
        date=datetime.date(2026, 8, 25),
        account_id=account.account_id,
        amount=-5000,
        payee_id=payee.payee_id,
        notes="Groceries",
    )

    transaction = add_transaction_to_database(session, transaction_data)

    session.flush()

    transaction_id = transaction.transaction_id

    delete_transaction_from_database(session, transaction)

    session.commit()
    session.expire_all()

    assert get_transaction_by_id_from_database(session, transaction_id) is None


def test_add_split_to_transaction_in_database(session: Session):
    account = add_account_to_database(session, "Checking")
    category = add_category_to_database(session, "Groceries")

    session.commit()

    transaction = add_transaction_to_database(
        session,
        TransactionCreate(
            account_id=account.account_id,
            amount=-5000,
        ),
    )

    split_data = TransactionSplitCreate(
        amount=-5000,
        category_id=category.category_id,
    )

    split = add_split_to_transaction_in_database(
        session,
        transaction,
        split_data,
    )

    session.flush()
    session.expire_all()

    stored_split = get_split_by_id_from_database(
        session,
        split.transaction_split_id,
    )

    assert stored_split is not None
    assert stored_split.amount == split_data.amount
    assert stored_split.category_id == split_data.category_id
    assert stored_split.transaction is transaction


def test_add_split_to_transaction_in_database_defaults(session: Session):
    account = add_account_to_database(session, "Checking")

    session.commit()

    transaction = add_transaction_to_database(
        session,
        TransactionCreate(account_id=account.account_id),
    )

    split = add_split_to_transaction_in_database(
        session,
        transaction,
        TransactionSplitCreate(),
    )

    session.flush()

    assert split.amount == 0
    assert split.category_id is None
    assert split.transaction is transaction


def test_get_transaction_split_by_id(session: Session):
    account = add_account_to_database(session, "Checking")

    session.commit()

    transaction = add_transaction_to_database(
        session,
        TransactionCreate(account_id=account.account_id),
    )

    split = add_split_to_transaction_in_database(
        session, transaction, TransactionSplitCreate()
    )

    session.commit()
    session.expire_all()

    split_id = split.transaction_split_id

    stored_transaction_split = get_split_by_id_from_database(
        session,
        split_id,
    )

    assert stored_transaction_split is not None
    assert stored_transaction_split.transaction is transaction
    assert stored_transaction_split.transaction_split_id == split_id


def test_get_transaction_split_by_id_not_found(session: Session):
    assert get_split_by_id_from_database(session, uuid6.uuid7()) is None


@pytest.mark.parametrize(
    ("new_splits", "expected_splits"),
    [
        ([], []),
        ([TransactionSplitCreate(amount=-3000)], [-3000]),
    ],
)
def test_update_transaction_splits_in_database(
    session: Session,
    new_splits: list[TransactionSplitCreate],
    expected_splits: list[int],
):
    account = add_account_to_database(session, "Checking")
    session.commit()

    transaction = add_transaction_to_database(
        session,
        TransactionCreate(account_id=account.account_id),
    )

    add_split_to_transaction_in_database(
        session,
        transaction,
        TransactionSplitCreate(amount=-5000),
    )

    session.flush()

    result = update_transaction_in_database(
        transaction,
        TransactionUpdate(splits=new_splits),
    )

    assert result is transaction
    assert [split.amount for split in transaction.splits] == expected_splits


def test_update_split_in_database(session: Session):
    account = add_account_to_database(session, "Checking")
    old_category = add_category_to_database(session, "Groceries")
    new_category = add_category_to_database(session, "Dining")

    session.commit()

    transaction = add_transaction_to_database(
        session,
        TransactionCreate(account_id=account.account_id),
    )

    split = add_split_to_transaction_in_database(
        session,
        transaction,
        TransactionSplitCreate(
            amount=-5000,
            category_id=old_category.category_id,
        ),
    )

    session.flush()

    result = update_split_in_database(
        split,
        TransactionSplitUpdate(
            category_id=new_category.category_id,
            amount=10000,
        ),
    )

    session.commit()
    session.expire_all()

    assert result is split
    assert split.category is new_category
    assert split.amount == 10000


def test_delete_transaction_split_from_database(session: Session):
    account = add_account_to_database(session, "Checking")

    session.commit()

    transaction = add_transaction_to_database(
        session,
        TransactionCreate(account_id=account.account_id),
    )

    split = add_split_to_transaction_in_database(
        session,
        transaction,
        TransactionSplitCreate(),
    )

    session.flush()

    split_id = split.transaction_split_id
    transaction_id = transaction.transaction_id

    delete_split_from_transaction_in_database(session, split)

    session.commit()
    session.expire_all()

    stored_transaction = get_transaction_by_id_from_database(
        session,
        transaction_id,
    )
    deleted_split = get_split_by_id_from_database(session, split_id)

    assert stored_transaction is not None
    assert deleted_split is None
    assert len(stored_transaction.splits) == 0
