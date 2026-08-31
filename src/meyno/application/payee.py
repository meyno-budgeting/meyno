from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Payee


def get_payee_by_id_from_database(session: Session, payee_id: int) -> Payee | None:
    return session.get(Payee, payee_id)


def get_payee_by_name_from_database(session: Session, name: str) -> Payee | None:
    statement = select(Payee).where(Payee.name == name)

    return session.scalars(statement).first()


def get_all_payees_from_database(session: Session) -> list[Payee]:
    return list(session.scalars(select(Payee)))


def add_payee_to_database(session: Session, name: str) -> Payee:

    payee = Payee(name=name)

    session.add(payee)

    return payee


def update_payee_name_in_database(payee: Payee, new_name: str) -> Payee:

    payee.name = new_name

    return payee


def delete_payee_from_database(session: Session, payee: Payee) -> None:
    session.delete(payee)
