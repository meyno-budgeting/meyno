from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from meyno.application.payee import (
    add_payee_to_database,
    delete_payee_from_database,
    get_all_payees_from_database,
    get_payee_by_id_from_database,
    get_payee_by_name_from_database,
    update_payee_name_in_database,
)
from meyno.exceptions.payee import (
    PayeeAlreadyExistsError,
    PayeeNameEmptyError,
    PayeeNotFoundError,
)

if TYPE_CHECKING:
    from meyno.database.models import Payee


def _check_payee_exists(session: Session, payee_name: str) -> None:
    # Check if payee already exists
    if get_payee_by_name_from_database(session, payee_name) is not None:
        raise PayeeAlreadyExistsError(payee_name)


def _validate_payee_name(name: str) -> str:
    name = name.strip()

    if not name:
        raise PayeeNameEmptyError

    return name


def add_payee(session: Session, name: str) -> Payee:
    with session.begin():
        name = _validate_payee_name(name)

        _check_payee_exists(session, name)

        payee = add_payee_to_database(session, name)

        return payee


def get_payee_by_id(session: Session, payee_id: int) -> Payee:
    payee = get_payee_by_id_from_database(session, payee_id)

    if payee is None:
        raise PayeeNotFoundError(payee_id)

    return payee


def get_payee_by_name(session: Session, payee_name: str) -> Payee:
    payee_name = _validate_payee_name(payee_name)

    payee = get_payee_by_name_from_database(session, payee_name)

    if payee is None:
        raise PayeeNotFoundError(payee_name)

    return payee


def get_all_payees(session: Session) -> list[Payee]:
    return get_all_payees_from_database(session)


def update_payee_name(session: Session, payee: Payee, new_name: str) -> Payee:
    with session.begin():
        new_name = _validate_payee_name(new_name)

        if new_name == payee.name:
            return payee

        _check_payee_exists(session, new_name)

        payee = update_payee_name_in_database(payee, new_name)

        return payee


def delete_payee(session: Session, payee: Payee) -> None:
    with session.begin():
        delete_payee_from_database(session, payee)
