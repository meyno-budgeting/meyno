from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.application.account import (
    add_account_to_database,
    delete_account_from_database,
    get_account_by_name,
    update_account_name_in_database,
)
from meyno.database.models import Account, Transaction

# TODO(ChaoticDefense): Wishlist: Add custom Errors related to Account
# AccountNotFoundError - For not finding the requested account
# AccountExistsError - For when an Account already exists with that name
# AccountNameEmptyError - For when Account name is empty

## Deleting account logic
# TODO(ChaoticDefense): Move to contoller layer


def check_account_exists(session: Session, account_name: str) -> None:
    # Check if account already exists
    existing_account = get_account_by_name(session, account_name)
    if existing_account is not None:
        msg = f"Account already exists: {account_name}"
        raise ValueError(msg)


def add_account(session: Session, name: str) -> None:
    name = name.strip()

    if not name:
        raise ValueError("Account name cannot be empty.")

    check_account_exists(session, name)

    return add_account_to_database(session, name)


def update_account_name(session: Session, account: Account, new_name: str) -> Account:
    new_name = new_name.strip()

    if not new_name:
        raise ValueError("Account name cannot be empty.")

    if new_name == account.name:
        return account

    check_account_exists(session, new_name)

    return update_account_name_in_database(account, new_name)


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

    delete_account_from_database(session, account)
