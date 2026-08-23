import re

import pytest

from meyno.application.payee import (
    create_payee,
    delete_payee,
    get_payee_by_id,
    get_payee_by_name,
    update_payee_name,
)
from meyno.database.models import Payee


def test_create_payee(session):
    payee = create_payee(session, "Walmart")

    stored_payee = session.get(Payee, payee.payee_id)

    assert stored_payee is not None
    assert stored_payee.name == "Walmart"
    assert stored_payee.payee_id is not None


def test_create_payee_empty_name(session):
    with pytest.raises(ValueError, match=re.escape("Payee name cannot be empty.")):
        create_payee(session, "  ")


def test_create_duplicate_payee(session):
    create_payee(session, "Walmart")

    with pytest.raises(ValueError, match="Payee already exists: Walmart"):
        create_payee(session, "Walmart")


def test_create_payee_strips_name(session):
    payee = create_payee(session, "  Walmart    ")

    assert payee.name == "Walmart"

    session.expire_all()

    stored_payee = session.get(Payee, payee.payee_id)

    assert stored_payee is not None
    assert stored_payee.name == "Walmart"


def test_get_payee_by_id(session):
    payee = create_payee(session, "Walmart")

    result = get_payee_by_id(session, payee.payee_id)

    assert result is not None
    assert result.payee_id == payee.payee_id
    assert result.name == "Walmart"


def test_get_payee_by_name(session):
    payee = create_payee(session, "Walmart")

    result = get_payee_by_name(session, "Walmart")

    assert result is not None
    assert result.payee_id == payee.payee_id
    assert result.name == "Walmart"


def test_get_payee_by_id_not_found(session):
    result = get_payee_by_id(session, 999)

    assert result is None


def test_get_payee_by_name_not_found(session):
    result = get_payee_by_name(session, "Does Not Exist")

    assert result is None


def test_update_payee_name(session):
    payee = create_payee(session, "Walmart")

    updated_payee = update_payee_name(session, payee, "GameStop")

    assert updated_payee is payee
    assert updated_payee.name == "GameStop"

    session.expire_all()

    stored_payee = session.get(Payee, payee.payee_id)

    assert stored_payee is not None
    assert stored_payee.name == "GameStop"


def test_update_payee_name_empty_name(session):
    payee = create_payee(session, "Walmart")

    with pytest.raises(
        ValueError,
        match=re.escape("Payee name cannot be empty."),
    ):
        update_payee_name(session, payee, "  ")


def test_update_payee_name_same_name(session):
    payee = create_payee(session, "Walmart")

    result = update_payee_name(session, payee, "Walmart")

    assert result is payee
    assert result.name == "Walmart"


def test_update_payee_name_duplicate(session):
    create_payee(session, "Walmart")
    gamestop = create_payee(session, "GameStop")

    with pytest.raises(ValueError, match=re.escape("Payee already exists: Walmart")):
        update_payee_name(session, gamestop, "Walmart")

    assert gamestop.name == "GameStop"


def test_update_payee_name_strips_name(session):
    payee = create_payee(session, "Walmart")

    result = update_payee_name(session, payee, "  GameStop  ")

    assert result.name == "GameStop"

    session.expire_all()

    stored_payee = session.get(Payee, payee.payee_id)

    assert stored_payee is not None
    assert stored_payee.name == "GameStop"


def test_delete_payee(session):
    payee = create_payee(session, "Walmart")

    assert delete_payee(session, payee) is None

    session.expire_all()

    assert session.get(Payee, payee.payee_id) is None
