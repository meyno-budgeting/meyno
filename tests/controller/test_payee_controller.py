import pytest
from sqlalchemy.orm import Session

from meyno.controller.account import add_account
from meyno.controller.payee import (
    add_payee,
    delete_payee,
    get_all_payees,
    get_payee_by_id,
    get_payee_by_name,
    update_payee_name,
)
from meyno.controller.transaction import (
    create_transaction,
    get_transaction_by_id,
)
from meyno.exceptions.payee import (
    PayeeAlreadyExistsError,
    PayeeNameEmptyError,
    PayeeNotFoundError,
)
from meyno.schemas.transaction import TransactionCreate


def test_add_payee(session: Session):
    payee = add_payee(session, "Walmart")

    assert payee.name == "Walmart"
    assert payee.payee_id is not None

    session.expire_all()

    stored_payee = get_payee_by_id(session, payee.payee_id)

    assert stored_payee is payee


def test_add_payee_strips_name(session: Session):
    payee = add_payee(session, "   Walmart ")

    assert payee.name == "Walmart"


@pytest.mark.parametrize("name", ["", "   "])
def test_add_payee_empty_name(session: Session, name: str):
    with pytest.raises(PayeeNameEmptyError):
        add_payee(session, name)


@pytest.mark.parametrize("name", ["Walmart", "    Walmart   "])
def test_add_duplicate_payee(session: Session, name: str):
    add_payee(session, "Walmart")

    with pytest.raises(PayeeAlreadyExistsError):
        add_payee(session, name)

    payees = get_all_payees(session)

    assert len(payees) == 1
    assert payees[0].name == "Walmart"


def test_get_payee_by_id(session: Session):
    payee = add_payee(session, "Walmart")

    session.expire_all()

    result = get_payee_by_id(session, payee.payee_id)

    assert result is payee


def test_get_payee_by_id_not_found(session: Session):
    with pytest.raises(PayeeNotFoundError):
        get_payee_by_id(session, 999)


def test_get_payee_by_name(session: Session):
    payee = add_payee(session, "Walmart")

    session.expire_all()

    result = get_payee_by_name(session, "Walmart")

    assert result is payee


def test_get_payee_by_name_not_found(session: Session):
    with pytest.raises(PayeeNotFoundError):
        get_payee_by_name(session, "Fycytviytviyuvik")


@pytest.mark.parametrize("name", ["", "    "])
def test_get_payee_by_name_empty_name(session: Session, name: str):
    with pytest.raises(PayeeNameEmptyError):
        get_payee_by_name(session, name)


def test_get_payee_by_name_strips_name(session: Session):
    payee = add_payee(session, "Walmart")

    session.expire_all()

    result = get_payee_by_name(session, "    Walmart   ")

    assert result is payee


def test_get_all_payees(session: Session):
    result = get_all_payees(session)

    assert len(result) == 0

    walmart = add_payee(session, "Walmart")
    gamestop = add_payee(session, "GameStop")

    session.expire_all()

    result = get_all_payees(session)

    assert len(result) == 2
    assert result[0] is walmart
    assert result[1] is gamestop


def test_update_payee_name(session: Session):
    payee = add_payee(session, "Walmart")

    result = update_payee_name(session, payee, "GameStop")

    assert result is payee
    assert payee.name == "GameStop"

    session.expire_all()

    stored_payee = get_payee_by_id(session, payee.payee_id)

    assert stored_payee is payee
    assert stored_payee.name == "GameStop"


@pytest.mark.parametrize("name", ["", "    "])
def test_update_payee_name_empty_name(session: Session, name: str):
    payee = add_payee(session, "Walmart")

    with pytest.raises(PayeeNameEmptyError):
        update_payee_name(session, payee, name)

    assert payee.name == "Walmart"


def test_update_payee_name_duplicate(session: Session):
    payee = add_payee(session, "Walmart")
    add_payee(session, "GameStop")

    with pytest.raises(PayeeAlreadyExistsError):
        update_payee_name(session, payee, "GameStop")

    assert payee.name == "Walmart"


@pytest.mark.parametrize("name", ["Walmart", "  Walmart    "])
def test_update_payee_name_same_name(session: Session, name: str):
    payee = add_payee(session, "Walmart")

    result = update_payee_name(session, payee, name)

    assert result is payee
    assert payee.name == "Walmart"


def test_delete_payee(session: Session):
    payee = add_payee(session, "Walmart")
    account = add_account(session, "Checking")

    transaction = create_transaction(
        session,
        TransactionCreate(
            account_id=account.account_id, payee_id=payee.payee_id, amount=1000
        ),
    )

    delete_payee(session, payee)

    session.expire_all()

    with pytest.raises(PayeeNotFoundError):
        get_payee_by_id(session, payee.payee_id)

    stored_transaction = get_transaction_by_id(session, transaction.transaction_id)

    assert stored_transaction.payee is None
    assert stored_transaction.payee_id is None
