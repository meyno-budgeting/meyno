from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Account


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
    existing_account = get_account_by_id(session, name)
    if existing_account is not None:
        raise ValueError(f"Account already exists: {name}")
    
    account = Account(name = name)
    
    session.add(account)
    session.flush()

    return account