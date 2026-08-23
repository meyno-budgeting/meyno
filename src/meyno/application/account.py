from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Account

# TODO(ChaoticDefense): Wishlist: Add custom Errors related to Account
# AccountNotFoundError - For not finding the requested account
# AccountExistsError - For when an Account already exists with that name
# AccountNameEmptyError - For when Account name is empty


def get_account_by_id(session: Session, account_id: int) -> Account | None:
    return session.get(Account, account_id)


def get_account_by_name(session: Session, name: str) -> Account | None:
    statement = select(Account).where(Account.name == name)

    return session.scalars(statement).first()


def create_account(session: Session, name: str) -> Account:
    name = name.strip()

    if not name:
        raise ValueError("Account name cannot be empty.")

    # Check if account already exists
    existing_account = get_account_by_name(session, name)
    if existing_account is not None:
        msg = f"Account already exists: {name}"
        raise ValueError(msg)

    account = Account(name=name)

    session.add(account)
    session.flush()

    return account


def update_account_name(session: Session, account: Account, new_name: str) -> Account:
    new_name = new_name.strip()

    if not new_name:
        raise ValueError("Account name cannot be empty.")

    if new_name == account.name:
        return account

    existing_account = get_account_by_name(session, new_name)

    if existing_account is not None:
        msg = f"Account already exists: {new_name}"
        raise ValueError(msg)

    account.name = new_name
    session.flush()

    return account


def delete_account(session: Session, account: Account) -> None:
    session.delete(account)
    session.flush()
