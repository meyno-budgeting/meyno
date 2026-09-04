from datetime import date

from meyno.application.account import (
    add_account_to_database,
    delete_account_from_database,
    get_account_by_id_from_database,
    get_account_by_name_from_database,
    update_account_name_in_database,
)
from meyno.application.transaction import (
    add_transaction_to_database,
    get_transaction_by_id_from_database,
)
from meyno.schemas.transaction import TransactionCreate


def test_create_account(session):
    account = add_account_to_database(session, "Checking")

    session.commit()
    session.expire_all()

    stored_account = get_account_by_id_from_database(session, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Checking"
    assert stored_account.account_id is not None


def test_get_account_by_id(session):
    account = add_account_to_database(session, "Checking")

    session.flush()

    result = get_account_by_id_from_database(session, account.account_id)

    assert result is not None
    assert result.account_id == account.account_id
    assert result.name == "Checking"


def test_get_account_by_name(session):
    account = add_account_to_database(session, "Checking")

    result = get_account_by_name_from_database(session, "Checking")

    assert result is not None
    assert result.account_id == account.account_id
    assert result.name == "Checking"


def test_get_account_by_id_not_found(session):
    result = get_account_by_id_from_database(session, 999)

    assert result is None


def test_get_account_by_name_not_found(session):
    result = get_account_by_name_from_database(session, "Does Not Exist")

    assert result is None


def test_update_account_name(session):
    account = add_account_to_database(session, "Checking")

    session.flush()

    updated_account = update_account_name_in_database(account, "Savings")

    assert updated_account is account
    assert updated_account.name == "Savings"

    session.commit()
    session.expire_all()

    stored_account = get_account_by_id_from_database(session, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Savings"


def test_delete_account(session):
    account = add_account_to_database(session, "Checking")

    session.flush()

    assert delete_account_from_database(session, account) is None

    session.commit()
    session.expire_all()

    assert get_account_by_id_from_database(session, account.account_id) is None


def test_delete_account_deletes_transactions(session):
    account = add_account_to_database(session, "Checking")

    session.commit()

    account_id = account.account_id

    transaction_1 = add_transaction_to_database(
        session,
        TransactionCreate(
            account_id=account_id,
            date=date(2026, 8, 23),
            amount=-10000,
        ),
    )
    transaction_2 = add_transaction_to_database(
        session,
        TransactionCreate(
            account_id=account_id,
            date=date(2026, 8, 23),
            amount=-50000,
        ),
    )

    session.flush()

    transaction_1_id = transaction_1.transaction_id
    transaction_2_id = transaction_2.transaction_id

    delete_account_from_database(session, account)

    session.commit()
    session.expire_all()

    assert get_account_by_id_from_database(session, account_id) is None
    assert get_transaction_by_id_from_database(session, transaction_1_id) is None
    assert get_transaction_by_id_from_database(session, transaction_2_id) is None
