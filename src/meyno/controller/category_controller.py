from sqlalchemy.orm import Session

from meyno.application.category import (
    add_category_to_database,
    delete_category_from_database,
    get_all_categories_from_database,
    get_category_by_id_from_database,
    get_category_by_name_from_database,
    update_category_name_in_database,
)
from meyno.database.models import Category
from meyno.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNameEmptyError,
    CategoryNotFoundError,
)


def _check_category_exists(session: Session, category_name: str) -> None:
    # Check if category already exists
    if get_category_by_name_from_database(session, category_name) is not None:
        raise CategoryAlreadyExistsError(category_name)


def _validate_category_name(name: str) -> str:
    name = name.strip()

    if not name:
        raise CategoryNameEmptyError

    return name


def add_category(session: Session, name: str) -> Category:
    with session.begin():
        name = _validate_category_name(name)

        _check_category_exists(session, name)

        category = add_category_to_database(session, name)

        return category


def get_category_by_id(session: Session, category_id: int) -> Category:
    category = get_category_by_id_from_database(session, category_id)

    if category is None:
        raise CategoryNotFoundError(category_id)

    return category


def get_category_by_name(session: Session, category_name: str) -> Category:
    category_name = _validate_category_name(category_name)

    category = get_category_by_name_from_database(session, category_name)

    if category is None:
        raise CategoryNotFoundError(category_name)

    return category


def get_all_categories(session: Session) -> list[Category]:
    return get_all_categories_from_database(session)


def update_category_name(
    session: Session, category: Category, new_name: str
) -> Category:
    with session.begin():
        new_name = _validate_category_name(new_name)

        if new_name == category.name:
            return category

        _check_category_exists(session, new_name)

        category = update_category_name_in_database(category, new_name)

        return category


def delete_category(session: Session, category: Category) -> None:
    with session.begin():
        delete_category_from_database(session, category)
