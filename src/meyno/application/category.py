from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Category

# TODO(ChaoticDefense): Wishlist: Add custom Errors related to Category
# CategoryNotFoundError - For not finding the requested category
# CategoryExistsError - For when an Category already exists with that name
# CategoryNameEmptyError - For when Category name is empty


def get_category_by_id_from_database(
    session: Session, category_id: int
) -> Category | None:
    return session.get(Category, category_id)


def get_category_by_name_from_database(session: Session, name: str) -> Category | None:
    statement = select(Category).where(Category.name == name)

    return session.scalars(statement).first()


def get_all_categories_from_database(session: Session) -> list[Category]:
    return list(session.scalars(select(Category)))


def add_category_to_database(session: Session, name: str) -> Category:
    category = Category(name=name)

    session.add(category)

    return category


def update_category_name_in_database(category: Category, new_name: str) -> Category:
    category.name = new_name

    return category


def delete_category_from_database(session: Session, category: Category) -> None:
    session.delete(category)
