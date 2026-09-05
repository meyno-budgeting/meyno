from sqlalchemy.orm import Session

from meyno.application.category import (
    add_category_to_database,
    delete_category_from_database,
    get_all_categories_from_database,
    get_category_by_id_from_database,
    get_category_by_name_from_database,
    update_category_name_in_database,
)


def test_create_category(session: Session):
    category = add_category_to_database(session, "Groceries")

    session.flush()

    stored_category = get_category_by_id_from_database(session, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Groceries"
    assert stored_category.category_id is not None


def test_get_category_by_id(session: Session):
    category = add_category_to_database(session, "Groceries")

    session.flush()

    result = get_category_by_id_from_database(session, category.category_id)

    assert result is not None
    assert result.category_id == category.category_id
    assert result.name == "Groceries"


def test_get_category_by_name(session: Session):
    category = add_category_to_database(session, "Groceries")

    session.flush()

    result = get_category_by_name_from_database(session, "Groceries")

    assert result is not None
    assert result.category_id == category.category_id
    assert result.name == "Groceries"


def test_get_all_categories_from_database(session: Session):
    result = get_all_categories_from_database(session)

    assert len(result) == 0

    groceries = add_category_to_database(session, "Groceries")
    fun = add_category_to_database(session, "Fun")

    session.commit()
    session.expire_all()

    result = get_all_categories_from_database(session)

    assert len(result) == 2
    assert result[0] is groceries
    assert result[1] is fun


def test_get_category_by_id_not_found(session: Session):
    result = get_category_by_id_from_database(session, 999)

    assert result is None


def test_get_category_by_name_not_found(session: Session):
    result = get_category_by_name_from_database(session, "Does Not Exist")

    assert result is None


def test_update_category_name(session: Session):
    category = add_category_to_database(session, "Groceries")

    updated_category = update_category_name_in_database(category, "Fun")

    assert updated_category is category
    assert updated_category.name == "Fun"

    session.commit()
    session.expire_all()

    stored_category = get_category_by_id_from_database(session, category.category_id)

    assert stored_category is not None
    assert stored_category.name == "Fun"


def test_delete_category_from_database(session: Session):
    category = add_category_to_database(session, "Groceries")
    session.flush()

    assert delete_category_from_database(session, category) is None

    session.commit()
    session.expire_all()

    assert get_category_by_id_from_database(session, category.category_id) is None
