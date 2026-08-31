import re

import pytest

from meyno.application.category import (
    add_category_to_database,
    delete_category,
    get_category_by_id_from_database,
    get_category_by_name_from_database,
    update_category_name_in_database,
)


def test_create_category(session):
    category = add_category_to_database(session, "Groceries")

    session.flush()

    stored_category = get_category_by_id_from_database(session, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Groceries"
    assert stored_category.category_id is not None


def test_create_category_empty_name(session):
    with pytest.raises(ValueError, match=re.escape("Category name cannot be empty.")):
        add_category_to_database(session, "  ")


def test_create_duplicate_category(session):
    add_category_to_database(session, "Groceries")

    session.flush()

    with pytest.raises(ValueError, match="Category already exists: Groceries"):
        add_category_to_database(session, "Groceries")


def test_create_category_strips_name(session):
    category = add_category_to_database(session, "  Groceries    ")

    assert category.name == "Groceries"

    session.commit()
    session.expire_all()

    stored_category = get_category_by_id_from_database(session, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Groceries"


def test_get_category_by_id(session):
    category = add_category_to_database(session, "Groceries")

    session.flush()

    result = get_category_by_id_from_database(session, category.category_id)

    assert result is not None
    assert result.category_id == category.category_id
    assert result.name == "Groceries"


def test_get_category_by_name(session):
    category = add_category_to_database(session, "Groceries")

    session.flush()

    result = get_category_by_name_from_database(session, "Groceries")

    assert result is not None
    assert result.category_id == category.category_id
    assert result.name == "Groceries"


def test_get_category_by_id_not_found(session):
    result = get_category_by_id_from_database(session, 999)

    assert result is None


def test_get_category_by_name_not_found(session):
    result = get_category_by_name_from_database(session, "Does Not Exist")

    assert result is None


def test_update_category_name(session):
    category = add_category_to_database(session, "Groceries")

    updated_category = update_category_name_in_database(session, category, "Fun")

    assert updated_category is category
    assert updated_category.name == "Fun"

    session.commit()
    session.expire_all()

    stored_category = get_category_by_id_from_database(session, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Fun"


def test_update_category_name_empty_name(session):
    category = add_category_to_database(session, "Groceries")

    with pytest.raises(
        ValueError,
        match=re.escape("Category name cannot be empty."),
    ):
        update_category_name_in_database(session, category, "  ")


def test_update_category_name_same_name(session):
    category = add_category_to_database(session, "Groceries")

    result = update_category_name_in_database(session, category, "Groceries")

    assert result is category
    assert result.name == "Groceries"


def test_update_category_name_duplicate(session):
    add_category_to_database(session, "Groceries")
    fun = add_category_to_database(session, "Fun")

    with pytest.raises(
        ValueError, match=re.escape("Category already exists: Groceries")
    ):
        update_category_name_in_database(session, fun, "Groceries")

    assert fun.name == "Fun"


def test_update_category_name_strips_name(session):
    category = add_category_to_database(session, "Groceries")

    result = update_category_name_in_database(session, category, "  Fun  ")

    assert result.name == "Fun"

    session.commit()
    session.expire_all()

    stored_category = get_category_by_id_from_database(session, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Fun"


def test_delete_category(session):
    category = add_category_to_database(session, "Groceries")
    session.flush()

    assert delete_category(session, category) is None

    session.commit()
    session.expire_all()

    assert get_category_by_id_from_database(session, category.category_id) is None
