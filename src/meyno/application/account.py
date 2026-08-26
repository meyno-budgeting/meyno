from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Account, Transaction

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

    return account


def delete_account(session: Session, account: Account) -> None:
    # Deletion logic: deleting explicitly a transaction that is part of a transfer
    # will also delete the other part of the transfer.
    # Deleting a whole account will instead break the chain and delete all transactions
    # in the account, while keeping the other side in tact.

    for transaction in account.transactions:
        # Transaction is the outgoing side.
        if transaction.transfer_transaction is not None:
            transaction.transfer_transaction = None

        # Transaction may be the incoming side.
        else:
            outgoing = session.scalars(
                select(Transaction).where(
                    Transaction.transfer_transaction_id == transaction.transaction_id
                )
            ).first()

            if outgoing is not None:
                outgoing.transfer_transaction = None

    # session.flush()

    session.delete(account)
    # session.flush()
