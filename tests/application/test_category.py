import re

import pytest

from meyno.application.category import (
    create_category,
    delete_category,
    get_category_by_id,
    get_category_by_name,
    update_category_name,
)
from meyno.database.models import Category


def test_create_category(session):
    category = create_category(session, "Groceries")

    stored_category = session.get(Category, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Groceries"
    assert stored_category.category_id is not None


def test_create_category_empty_name(session):
    with pytest.raises(ValueError, match=re.escape("Category name cannot be empty.")):
        create_category(session, "  ")


def test_create_duplicate_category(session):
    create_category(session, "Groceries")

    with pytest.raises(ValueError, match="Category already exists: Groceries"):
        create_category(session, "Groceries")


def test_create_category_strips_name(session):
    category = create_category(session, "  Groceries    ")

    assert category.name == "Groceries"

    session.expire_all()

    stored_category = session.get(Category, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Groceries"


def test_get_category_by_id(session):
    category = create_category(session, "Groceries")

    result = get_category_by_id(session, category.category_id)

    assert result is not None
    assert result.category_id == category.category_id
    assert result.name == "Groceries"


def test_get_category_by_name(session):
    category = create_category(session, "Groceries")

    result = get_category_by_name(session, "Groceries")

    assert result is not None
    assert result.category_id == category.category_id
    assert result.name == "Groceries"


def test_get_category_by_id_not_found(session):
    result = get_category_by_id(session, 999)

    assert result is None


def test_get_category_by_name_not_found(session):
    result = get_category_by_name(session, "Does Not Exist")

    assert result is None


def test_update_category_name(session):
    category = create_category(session, "Groceries")

    updated_category = update_category_name(session, category, "Fun")

    assert updated_category is category
    assert updated_category.name == "Fun"

    session.expire_all()

    stored_category = session.get(Category, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Fun"


def test_update_category_name_empty_name(session):
    category = create_category(session, "Groceries")

    with pytest.raises(
        ValueError,
        match=re.escape("Category name cannot be empty."),
    ):
        update_category_name(session, category.category_id, "  ")


def test_update_category_name_same_name(session):
    category = create_category(session, "Groceries")

    result = update_category_name(session, category, "Groceries")

    assert result is category
    assert result.name == "Groceries"


def test_update_category_name_duplicate(session):
    create_category(session, "Groceries")
    fun = create_category(session, "Fun")

    with pytest.raises(
        ValueError, match=re.escape("Category already exists: Groceries")
    ):
        update_category_name(session, fun, "Groceries")

    assert fun.name == "Fun"


def test_update_category_name_strips_name(session):
    category = create_category(session, "Groceries")

    result = update_category_name(session, category, "  Fun  ")

    assert result.name == "Fun"

    session.expire_all()

    stored_category = session.get(Category, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Fun"


def test_delete_category(session):
    category = create_category(session, "Groceries")

    assert delete_category(session, category) is None

    session.expire_all()

    assert session.get(Category, category.category_id) is None
