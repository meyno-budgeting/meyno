from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Payee

# TODO(ChaoticDefense): Wishlist: Add custom Errors related to Payee
# PayeeNotFoundError - For not finding the requested payee
# PayeeExistsError - For when an Payee already exists with that name
# PayeeNameEmptyError - For when Payee name is empty


def get_payee_by_id(session: Session, payee_id: int) -> Payee | None:
    return session.get(Payee, payee_id)


def get_payee_by_name(session: Session, name: str) -> Payee | None:
    statement = select(Payee).where(Payee.name == name)

    return session.scalars(statement).first()


def create_payee(session: Session, name: str) -> Payee:
    name = name.strip()

    if not name:
        raise ValueError("Payee name cannot be empty.")

    # Check if payee already exists
    existing_payee = get_payee_by_name(session, name)
    if existing_payee is not None:
        msg = f"Payee already exists: {name}"
        raise ValueError(msg)

    payee = Payee(name=name)

    session.add(payee)
    session.flush()

    return payee


def update_payee_name(session: Session, payee_id: int, new_name: str) -> Payee:
    found_payee = get_payee_by_id(session, payee_id)
    if found_payee is None:
        msg = f"Cannot find Payee with id {payee_id}"
        raise ValueError(msg)

    new_name = new_name.strip()

    if not new_name:
        raise ValueError("Payee name cannot be empty.")

    if new_name == found_payee.name:
        return found_payee

    existing_payee = get_payee_by_name(session, new_name)

    if existing_payee is not None:
        msg = f"Payee already exists: {new_name}"
        raise ValueError(msg)

    found_payee.name = new_name
    session.flush()

    return found_payee


def delete_payee(session: Session, payee_id: int) -> None:
    found_payee = get_payee_by_id(session, payee_id)
    if found_payee is None:
        msg = f"Cannot find Payee with id {payee_id}"
        raise ValueError(msg)

    session.delete(found_payee)
    session.flush()
