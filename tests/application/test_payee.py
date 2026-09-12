import uuid6
from sqlalchemy.orm import Session

from meyno.application.payee import (
    add_payee_to_database,
    delete_payee_from_database,
    get_all_payees_from_database,
    get_payee_by_id_from_database,
    get_payee_by_name_from_database,
    update_payee_name_in_database,
)


def test_create_payee(session: Session):
    payee = add_payee_to_database(session, "Walmart")

    session.commit()
    session.expire_all()

    stored_payee = get_payee_by_id_from_database(session, payee.payee_id)

    assert stored_payee is not None
    assert stored_payee.name == "Walmart"
    assert stored_payee.payee_id is not None


def test_get_payee_by_id(session: Session):
    payee = add_payee_to_database(session, "Walmart")

    session.flush()

    result = get_payee_by_id_from_database(session, payee.payee_id)

    assert result is not None
    assert result.payee_id == payee.payee_id
    assert result.name == "Walmart"


def test_get_payee_by_name(session: Session):
    payee = add_payee_to_database(session, "Walmart")

    result = get_payee_by_name_from_database(session, "Walmart")

    assert result is not None
    assert result.payee_id == payee.payee_id
    assert result.name == "Walmart"


def test_get_payee_by_id_not_found(session: Session):
    result = get_payee_by_id_from_database(session, uuid6.uuid7())

    assert result is None


def test_get_payee_by_name_not_found(session: Session):
    result = get_payee_by_name_from_database(session, "Does Not Exist")

    assert result is None


def test_get_all_payees_from_database(session: Session):
    result = get_all_payees_from_database(session)

    assert len(result) == 0

    checking = add_payee_to_database(session, "Walmart")
    savings = add_payee_to_database(session, "GameStop")

    session.commit()
    session.expire_all()

    result = get_all_payees_from_database(session)

    assert len(result) == 2
    assert result[0] is checking
    assert result[1] is savings


def test_update_payee_name(session: Session):
    payee = add_payee_to_database(session, "Walmart")

    session.flush()

    updated_payee = update_payee_name_in_database(payee, "GameStop")

    assert updated_payee is payee
    assert updated_payee.name == "GameStop"

    session.commit()
    session.expire_all()

    stored_payee = get_payee_by_id_from_database(session, payee.payee_id)

    assert stored_payee is not None
    assert stored_payee.name == "GameStop"


def test_delete_payee(session: Session):
    payee = add_payee_to_database(session, "Walmart")

    session.flush()

    assert delete_payee_from_database(session, payee) is None

    session.commit()
    session.expire_all()

    assert get_payee_by_id_from_database(session, payee.payee_id) is None
