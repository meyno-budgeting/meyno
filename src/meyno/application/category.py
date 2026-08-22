from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Category

# TODO(ChaoticDefense): Wishlist: Add custom Errors related to Category
# CategoryNotFoundError - For not finding the requested category
# CategoryExistsError - For when an Category already exists with that name
# CategoryNameEmptyError - For when Category name is empty


def get_category_by_id(session: Session, category_id: int) -> Category | None:
    return session.get(Category, category_id)


def get_category_by_name(session: Session, name: str) -> Category | None:
    statement = select(Category).where(Category.name == name)

    return session.scalars(statement).first()


def create_category(session: Session, name: str) -> Category:
    name = name.strip()

    if not name:
        raise ValueError("Category name cannot be empty.")

    # Check if category already exists
    existing_category = get_category_by_name(session, name)
    if existing_category is not None:
        msg = f"Category already exists: {name}"
        raise ValueError(msg)

    category = Category(name=name)

    session.add(category)
    session.flush()

    return category


def update_category_name(session: Session, category_id: int, new_name: str) -> Category:
    found_category = get_category_by_id(session, category_id)
    if found_category is None:
        msg = f"Cannot find Category with id {category_id}"
        raise ValueError(msg)

    new_name = new_name.strip()

    if not new_name:
        raise ValueError("Category name cannot be empty.")

    if new_name == found_category.name:
        return found_category

    existing_category = get_category_by_name(session, new_name)

    if existing_category is not None:
        msg = f"Category already exists: {new_name}"
        raise ValueError(msg)

    found_category.name = new_name
    session.flush()

    return found_category


def delete_category(session: Session, category_id: int) -> None:
    found_category = get_category_by_id(session, category_id)
    if found_category is None:
        msg = f"Cannot find Category with id {category_id}"
        raise ValueError(msg)

    session.delete(found_category)
    session.flush()
