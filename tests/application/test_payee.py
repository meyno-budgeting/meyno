import re

import pytest

from meyno.application.payee import (
    add_payee_to_database,
    delete_payee_from_database,
    get_payee_by_id_from_database,
    get_payee_by_name_from_database,
    update_payee_name_in_database,
)


def test_create_payee(session):
    payee = add_payee_to_database(session, "Walmart")

    session.flush()

    stored_payee = get_payee_by_id_from_database(session, payee.payee_id)

    assert stored_payee is not None
    assert stored_payee.name == "Walmart"
    assert stored_payee.payee_id is not None


# def test_create_payee_empty_name(session):
#     with pytest.raises(ValueError, match=re.escape("Payee name cannot be empty.")):
#         add_payee_to_database(session, "  ")


# def test_create_duplicate_payee(session):
#     add_payee_to_database(session, "Walmart")

#     with pytest.raises(ValueError, match="Payee already exists: Walmart"):
#         add_payee_to_database(session, "Walmart")


# def test_create_payee_strips_name(session):
#     payee = add_payee_to_database(session, "  Walmart    ")

#     session.flush()

#     assert payee.name == "Walmart"

#     session.expire_all()

#     stored_payee = get_payee_by_id_from_database(session, payee.payee_id)

#     assert stored_payee is not None
#     assert stored_payee.name == "Walmart"


def test_get_payee_by_id(session):
    payee = add_payee_to_database(session, "Walmart")

    session.flush()

    result = get_payee_by_id_from_database(session, payee.payee_id)

    assert result is not None
    assert result.payee_id == payee.payee_id
    assert result.name == "Walmart"


def test_get_payee_by_name(session):
    payee = add_payee_to_database(session, "Walmart")

    session.flush()

    result = get_payee_by_name_from_database(session, "Walmart")

    assert result is not None
    assert result.payee_id == payee.payee_id
    assert result.name == "Walmart"


def test_get_payee_by_id_not_found(session):
    result = get_payee_by_id_from_database(session, 999)

    assert result is None


def test_get_payee_by_name_not_found(session):
    result = get_payee_by_name_from_database(session, "Does Not Exist")

    assert result is None


def test_update_payee_name(session):
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


# def test_update_payee_name_empty_name(session):
#     payee = add_payee_to_database(session, "Walmart")

#     with pytest.raises(
#         ValueError,
#         match=re.escape("Payee name cannot be empty."),
#     ):
#         update_payee_name_in_database(session, payee, "  ")


# def test_update_payee_name_same_name(session):
#     payee = add_payee_to_database(session, "Walmart")

#     result = update_payee_name_in_database(session, payee, "Walmart")

#     assert result is payee
#     assert result.name == "Walmart"


# def test_update_payee_name_duplicate(session):
#     add_payee_to_database(session, "Walmart")
#     gamestop = add_payee_to_database(session, "GameStop")

#     with pytest.raises(ValueError, match=re.escape("Payee already exists: Walmart")):
#         update_payee_name_in_database(session, gamestop, "Walmart")

#     assert gamestop.name == "GameStop"


# def test_update_payee_name_strips_name(session):
#     payee = add_payee_to_database(session, "Walmart")

#     session.flush()

#     result = update_payee_name_in_database(session, payee, "  GameStop  ")

#     assert result.name == "GameStop"

#     session.commit()
#     session.expire_all()

#     stored_payee = get_payee_by_id_from_database(session, payee.payee_id)

#     assert stored_payee is not None
#     assert stored_payee.name == "GameStop"


def test_delete_payee(session):
    payee = add_payee_to_database(session, "Walmart")

    session.flush()

    assert delete_payee_from_database(session, payee) is None

    session.commit()
    session.expire_all()

    assert get_payee_by_id_from_database(session, payee.payee_id) is None
