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


def _check_account_exists(session: Session, account_name: str) -> None:
    # Check if account already exists
    existing_account = get_account_by_name(session, account_name)
    if existing_account is not None:
        msg = f"Account already exists: {account_name}"
        raise ValueError(msg)


def _validate_account_name(name: str) -> str:
    name = name.strip()

    if not name:
        raise ValueError("Account name cannot be empty.")

    return name


def add_account(session: Session, name: str) -> Account:
    with session.begin():
        name = _validate_account_name(name)

        _check_account_exists(session, name)

        account = add_account_to_database(session, name)

        return account


def update_account_name(session: Session, account: Account, new_name: str) -> Account:
    with session.begin():
        new_name = _validate_account_name(new_name)

        if new_name == account.name:
            return account

        _check_account_exists(session, new_name)

        account = update_account_name_in_database(account, new_name)

        return account


def delete_account(session: Session, account: Account) -> None:
    # Deletion logic: deleting explicitly a transaction that is part of a transfer
    # will also delete the other part of the transfer.
    # Deleting a whole account will instead break the chain and delete all transactions
    # in the account, while keeping the other side in tact.

    with session.begin():
        for transaction in account.transactions:
            # Transaction is the outgoing side.
            if transaction.transfer_transaction is not None:
                transaction.transfer_transaction = None

            # Transaction may be the incoming side.
            else:
                outgoing = session.scalars(
                    select(Transaction).where(
                        Transaction.transfer_transaction_id
                        == transaction.transaction_id
                    )
                ).first()

                if outgoing is not None:
                    outgoing.transfer_transaction = None

        delete_account_from_database(session, account)
