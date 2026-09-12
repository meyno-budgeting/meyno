import pytest
import uuid6
from sqlalchemy.orm import Session

from meyno.controller.account import add_account
from meyno.controller.category import (
    add_category,
    delete_category,
    get_all_categories,
    get_category_by_id,
    get_category_by_name,
    update_category_name,
)
from meyno.controller.transaction import (
    add_transaction,
    get_transaction_by_id,
)
from meyno.exceptions.category import (
    CategoryAlreadyExistsError,
    CategoryNameEmptyError,
    CategoryNotFoundError,
)
from meyno.schemas.transaction import TransactionCreate, TransactionSplitCreate


def test_add_category(session: Session):
    category = add_category(session, "Walmart")

    assert category.name == "Walmart"
    assert category.category_id is not None

    session.expire_all()

    stored_category = get_category_by_id(session, category.category_id)

    assert stored_category is category


def test_add_category_strips_name(session: Session):
    category = add_category(session, "   Walmart ")

    assert category.name == "Walmart"


@pytest.mark.parametrize("name", ["", "   "])
def test_add_category_empty_name(session: Session, name: str):
    with pytest.raises(CategoryNameEmptyError):
        add_category(session, name)


@pytest.mark.parametrize("name", ["Walmart", "    Walmart   "])
def test_add_duplicate_category(session: Session, name: str):
    add_category(session, "Walmart")

    with pytest.raises(CategoryAlreadyExistsError):
        add_category(session, name)

    categories = get_all_categories(session)

    assert len(categories) == 1
    assert categories[0].name == "Walmart"


def test_get_category_by_id(session: Session):
    category = add_category(session, "Walmart")

    session.expire_all()

    result = get_category_by_id(session, category.category_id)

    assert result is category


def test_get_category_by_id_not_found(session: Session):
    with pytest.raises(CategoryNotFoundError):
        get_category_by_id(session, uuid6.uuid7())


def test_get_category_by_name(session: Session):
    category = add_category(session, "Walmart")

    session.expire_all()

    result = get_category_by_name(session, "Walmart")

    assert result is category


def test_get_category_by_name_not_found(session: Session):
    with pytest.raises(CategoryNotFoundError):
        get_category_by_name(session, "Fycytviytviyuvik")


@pytest.mark.parametrize("name", ["", "    "])
def test_get_category_by_name_empty_name(session: Session, name: str):
    with pytest.raises(CategoryNameEmptyError):
        get_category_by_name(session, name)


def test_get_category_by_name_strips_name(session: Session):
    category = add_category(session, "Walmart")

    session.expire_all()

    result = get_category_by_name(session, "    Walmart   ")

    assert result is category


def test_get_all_categories(session: Session):
    result = get_all_categories(session)

    assert len(result) == 0

    groceries = add_category(session, "Groceries")
    fun = add_category(session, "Fun")

    session.expire_all()

    result = get_all_categories(session)

    assert len(result) == 2
    assert result[0] is groceries
    assert result[1] is fun


def test_update_category_name(session: Session):
    category = add_category(session, "Walmart")

    result = update_category_name(session, category, "GameStop")

    assert result is category
    assert category.name == "GameStop"

    session.expire_all()

    stored_category = get_category_by_id(session, category.category_id)

    assert stored_category is category
    assert stored_category.name == "GameStop"


@pytest.mark.parametrize("name", ["", "    "])
def test_update_category_name_empty_name(session: Session, name: str):
    category = add_category(session, "Walmart")

    with pytest.raises(CategoryNameEmptyError):
        update_category_name(session, category, name)

    assert category.name == "Walmart"


def test_update_category_name_duplicate(session: Session):
    category = add_category(session, "Walmart")
    add_category(session, "GameStop")

    with pytest.raises(CategoryAlreadyExistsError):
        update_category_name(session, category, "GameStop")

    assert category.name == "Walmart"


@pytest.mark.parametrize("name", ["Walmart", "  Walmart    "])
def test_update_category_name_same_name(session: Session, name: str):
    category = add_category(session, "Walmart")

    result = update_category_name(session, category, name)

    assert result is category
    assert category.name == "Walmart"


def test_delete_category(session: Session):
    category = add_category(session, "Walmart")
    account = add_account(session, "Checking")

    transaction = add_transaction(
        session,
        TransactionCreate(
            account_id=account.account_id,
            splits=[
                TransactionSplitCreate(
                    category_id=category.category_id,
                )
            ],
        ),
    )

    delete_category(session, category)

    session.expire_all()

    with pytest.raises(CategoryNotFoundError):
        get_category_by_id(session, category.category_id)

    stored_transaction = get_transaction_by_id(session, transaction.transaction_id)

    assert stored_transaction.splits[0] is not None
    assert stored_transaction.splits[0].category_id is None
