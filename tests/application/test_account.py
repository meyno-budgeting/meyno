import re

import pytest

from meyno.application.account import (
    create_account,
    delete_account,
    get_account_by_id,
    get_account_by_name,
    update_account_name,
)
from meyno.database.models import Account


def test_create_account(session):
    account = create_account(session, "Checking")

    stored_account = session.get(Account, account.account_id)

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

    assert account.name == "Checking"

    session.expire_all()

    stored_account = session.get(Account, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Checking"


def test_get_account_by_id(session):
    account = create_account(session, "Checking")

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

    updated_account = update_account_name(session, account.account_id, "Savings")

    assert updated_account is account
    assert updated_account.name == "Savings"

    session.expire_all()

    stored_account = session.get(Account, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Savings"


def test_update_account_name_not_found(session):
    with pytest.raises(
        ValueError,
        match=re.escape("Cannot find Account with id 999"),
    ):
        update_account_name(session, 999, "Checking")


def test_update_account_name_empty_name(session):
    account = create_account(session, "Checking")

    with pytest.raises(
        ValueError,
        match=re.escape("Account name cannot be empty."),
    ):
        update_account_name(session, account.account_id, "  ")


def test_update_account_name_same_name(session):
    account = create_account(session, "Checking")

    result = update_account_name(session, account.account_id, "Checking")

    assert result is account
    assert result.name == "Checking"


def test_update_account_name_duplicate(session):
    create_account(session, "Checking")
    savings = create_account(session, "Savings")

    with pytest.raises(
        ValueError,
        match=re.escape("Account already exists: Checking"),
    ):
        update_account_name(session, savings.account_id, "Checking")

    assert savings.name == "Savings"


def test_update_account_name_strips_name(session):
    account = create_account(session, "Checking")

    result = update_account_name(
        session,
        account.account_id,
        "  Savings  ",
    )

    assert result.name == "Savings"

    session.expire_all()

    stored_account = session.get(Account, account.account_id)

    assert stored_account is not None
    assert stored_account.name == "Savings"


def test_delete_account(session):
    account = create_account(session, "Checking")
    account_id = account.account_id

    assert delete_account(session, account_id) is None

    session.expire_all()

    assert session.get(Account, account_id) is None


def test_delete_account_not_found(session):
    with pytest.raises(
        ValueError,
        match=re.escape("Cannot find Account with id 999"),
    ):
        delete_account(session, 999)
