from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Account


def get_account_by_id_from_database(
    session: Session, account_id: int
) -> Account | None:
    return session.get(Account, account_id)


def get_account_by_name_from_database(session: Session, name: str) -> Account | None:
    statement = select(Account).where(Account.name == name)

    return session.scalars(statement).first()


def add_account_to_database(session: Session, name: str) -> Account:
    account = Account(name=name)
    session.add(account)

    return account


def update_account_name_in_database(account: Account, new_name: str) -> Account:
    account.name = new_name

    return account


def delete_account_from_database(session: Session, account: Account) -> None:
    session.delete(account)
