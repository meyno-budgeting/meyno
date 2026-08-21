import pytest

from meyno.application.account import (
    create_account,
    get_account_by_id,
    get_account_by_name,
)
from meyno.database.models import Account


def test_create_account(session):
    account = create_account(session, "Checking")

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


def test_create_account_empty_name(session):
    with pytest.raises(ValueError, match="Account name cannot be empty."):
        create_account(session, "  ")


def test_create_duplicate_account(session):
    create_account(session, "Checking")

    with pytest.raises(ValueError, match="Account already exists: Checking"):
        create_account(session, "Checking")


def test_get_account_by_id_not_found(session):
    result = get_account_by_id(session, 999)

    assert result is None


def test_get_account_by_name_not_found(session):
    result = get_account_by_name(session, "Does Not Exist")

    assert result is None
