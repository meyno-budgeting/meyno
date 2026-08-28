import re
from datetime import date

import pytest

from meyno.application.account import (
    create_account,
    delete_account,
    get_account_by_id,
    get_account_by_name,
    update_account_name,
)
from meyno.database.models import Account, Transaction


def test_create_account(session):
    account = create_account(session, "Checking")

    session.flush()

    stored_account = get_account_by_id(session, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Checking"
    assert stored_account.account_id is not None


def test_create_account_empty_name(session):
    with pytest.raises(ValueError, match=re.escape("Account name cannot be empty.")):
        create_account(session, "  ")


def test_create_duplicate_account(session):
    create_account(session, "Checking")

    with pytest.raises(ValueError, match="Account already exists: Checking"):
        create_account(session, "Checking")


def test_create_account_strips_name(session):
    account = create_account(session, "  Checking    ")

    session.flush()

    assert account.name == "Checking"

    session.expire_all()

    stored_account = get_account_by_id(session, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Checking"


def test_get_account_by_id(session):
    account = create_account(session, "Checking")

    session.flush()

    result = get_account_by_id(session, account.account_id)

    assert result is not None
    assert result.account_id == account.account_id
    assert result.name == "Checking"


def test_get_account_by_name(session):
    account = create_account(session, "Checking")

    result = get_account_by_name(session, "Checking")

    assert result is not None
    assert result.account_id == account.account_id
    assert result.name == "Checking"


def test_get_account_by_id_not_found(session):
    result = get_account_by_id(session, 999)

    assert result is None


def test_get_account_by_name_not_found(session):
    result = get_account_by_name(session, "Does Not Exist")

    assert result is None


def test_update_account_name(session):
    account = create_account(session, "Checking")

    session.flush()

    updated_account = update_account_name(session, account, "Savings")

    assert updated_account is account
    assert updated_account.name == "Savings"

    session.commit()
    session.expire_all()

    stored_account = get_account_by_id(session, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Savings"


def test_update_account_name_empty_name(session):
    account = create_account(session, "Checking")

    with pytest.raises(
        ValueError,
        match=re.escape("Account name cannot be empty."),
    ):
        update_account_name(session, account, "  ")


def test_update_account_name_same_name(session):
    account = create_account(session, "Checking")

    result = update_account_name(session, account, "Checking")

    assert result is account
    assert result.name == "Checking"


def test_update_account_name_duplicate(session):
    create_account(session, "Checking")
    savings = create_account(session, "Savings")

    with pytest.raises(ValueError, match=re.escape("Account already exists: Checking")):
        update_account_name(session, savings, "Checking")

    assert savings.name == "Savings"


def test_update_account_name_strips_name(session):
    account = create_account(session, "Checking")

    session.flush()

    result = update_account_name(session, account, "  Savings  ")

    assert result.name == "Savings"

    session.commit()
    session.expire_all()

    stored_account = get_account_by_id(session, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Savings"


def test_delete_account(session):
    account = create_account(session, "Checking")

    session.flush()

    assert delete_account(session, account) is None

    session.commit()
    session.expire_all()

    assert get_account_by_id(session, account.account_id) is None


def test_delete_account_deletes_transactions(session):
    account = create_account(session, "Checking")

    transaction_1 = Transaction(
        account=account,
        date=date(2026, 8, 23),
        amount=-10000,
    )
    transaction_2 = Transaction(
        account=account,
        date=date(2026, 8, 23),
        amount=50000,
    )

    session.add_all([transaction_1, transaction_2])
    session.flush()

    transaction_1_id = transaction_1.transaction_id
    transaction_2_id = transaction_2.transaction_id
    account_id = account.account_id

    delete_account(session, account)

    session.expire_all()

    assert session.get(Account, account_id) is None
    assert session.get(Transaction, transaction_1_id) is None
    assert session.get(Transaction, transaction_2_id) is None


def test_delete_account_preserves_incoming_transfer_transaction(session):
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

    session.add_all([checking_transaction, savings_transaction])

    checking_transaction.transfer_transaction = savings_transaction
    session.flush()

    savings_transaction_id = savings_transaction.transaction_id

    delete_account(session, checking)

    session.commit()
    session.expire_all()

    stored_savings_transaction = session.get(
        Transaction,
        savings_transaction_id,
    )

    assert stored_savings_transaction is not None
    assert stored_savings_transaction.transfer_transaction is None


## TODO(ChaoticDefense): Move this test to controller layer
# def test_delete_account_preserves_outgoing_transfer_transaction(session):
#     checking = create_account(session, "Checking")
#     savings = create_account(session, "Savings")

#     checking_transaction = Transaction(
#         account=checking,
#         date=date(2026, 8, 24),
#         amount=-500,
#     )

#     savings_transaction = Transaction(
#         account=savings,
#         date=date(2026, 8, 24),
#         amount=500,
#     )

#     session.add_all([checking_transaction, savings_transaction])

#     checking_transaction.transfer_transaction = savings_transaction
#     session.flush()

#     checking_transaction_id = checking_transaction.transaction_id

#     delete_account(session, savings)

#     session.commit()
#     session.expire_all()

#     stored_checking_transaction = session.get(
#         Transaction,
#         checking_transaction_id,
#     )

#     assert stored_checking_transaction is not None
#     assert stored_checking_transaction.transfer_transaction is None
