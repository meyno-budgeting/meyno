import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import (
    Account,
    Category,
    Payee,
    Transaction,
    TransactionSplit,
)


def get_transaction_by_id(session: Session, transaction_id: int) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def create_default_transaction(session: Session, account: Account) -> Transaction:
    transaction_date = datetime.datetime.now().astimezone().date()

    transaction = Transaction(
        date=transaction_date,
        account=account,
        payee=None,
        amount=0,
        notes=None,
    )

    session.add(transaction)

    create_default_transaction_split(session, transaction)

    return transaction


def update_transaction_date(
    transaction: Transaction, new_date: datetime.date
) -> Transaction:

    transaction.date = new_date

    return transaction


def update_transaction_account(
    transaction: Transaction, new_account: Account
) -> Transaction:

    transaction.account = new_account

    return transaction


def update_transaction_payee(
    transaction: Transaction, new_payee: Payee | None
) -> Transaction:

    transaction.payee = new_payee

    return transaction


def update_transaction_amount(transaction: Transaction, new_amount: int) -> Transaction:

    transaction.amount = new_amount

    if len(transaction.splits) == 1:
        # "Normal" non-transfer transaction
        # Update the only split amount as well
        transaction.splits[0].amount = new_amount
    elif len(transaction.splits) > 1:
        # "Split" non-transfer transaction
        # TODO: Logic for adding a split with appropiate positive or negative
        # amount to make sum of splits equal to transaction amount
        pass
    else:
        # Transfer transaction
        # TODO: Logic for modifying other side of transfer's amount
        pass

    return transaction


def update_transaction_notes(transaction: Transaction, new_notes: str) -> Transaction:
    transaction.notes = new_notes

    return transaction


def update_transaction_splits(
    transaction: Transaction, new_splits: list[TransactionSplit] | None
) -> Transaction:

    if new_splits is None:
        new_splits = []

    transaction.splits = new_splits

    return transaction


def convert_transaction_to_transfer(
    session: Session, transaction: Transaction, transfer_account: Account
) -> Transaction:

    if transaction.transfer_transaction is not None:
        raise ValueError("Transaction is already a transfer.")

    # Create a transaction in other account
    transfer_transaction = create_default_transaction(session, transfer_account)

    # Set amount of transfer side to equal and opposite
    transfer_transaction = update_transaction_amount(
        transfer_transaction, -1 * transaction.amount
    )

    # Set splits to empty for both sides
    transaction = update_transaction_splits(transaction, [])
    transfer_transaction = update_transaction_splits(transfer_transaction, [])

    transaction.transfer_transaction = transfer_transaction

    return transaction


def convert_transfer_to_transaction(
    session: Session, transaction: Transaction
) -> Transaction:

    if transaction.transfer_transaction is None:
        raise ValueError("Transaction is already not a transfer.")

    # Get incoming side of transfer
    transfer_transaction = transaction.transfer_transaction

    # Unlink outgoing transfer
    transaction.transfer_transaction = None

    # Make split for transaction and set amount to transaction amount
    split = create_default_transaction_split(session, transaction)
    split = update_transaction_split_amount(split, transaction.amount)

    # Delete incoming side of transfer
    delete_transaction(transfer_transaction)

    return transaction


def delete_transaction(session: Session, transaction: Transaction) -> None:
    # Deletion logic: deleting explicitly a transaction that is part of a transfer
    # will also delete the other part of the transfer.
    # Deleting a whole account will instead break the chain and delete all transactions
    # in the account, while keeping the other side in tact.

    # Check if transaction was part of a transfer
    if transaction.transfer_transaction is not None:
        # This transaction is the outgoing side.
        outgoing = transaction
        incoming = transaction.transfer_transaction
    else:
        # Check whether this transaction is the incoming side.
        outgoing = session.scalars(
            select(Transaction).where(
                Transaction.transfer_transaction_id == transaction.transaction_id
            )
        ).first()

        if outgoing is None:
            # This transaction is not part of a transfer.
            session.delete(transaction)
            return

        # This transaction is the incoming side.
        incoming = transaction

    # Break the transfer relationship before deleting either transaction.
    outgoing.transfer_transaction = None

    # Delete both sides of the transfer.
    session.delete(outgoing)
    session.delete(incoming)


def get_transaction_split_by_id(
    session: Session, split_id: int
) -> TransactionSplit | None:
    return session.get(TransactionSplit, split_id)


def create_default_transaction_split(
    session: Session, transaction: Transaction
) -> TransactionSplit:

    split = TransactionSplit(
        transaction=transaction,
        category=None,
        amount=0,
    )

    session.add(split)

    return split


def update_transaction_split_category(
    split: TransactionSplit, new_category: Category
) -> TransactionSplit:

    split.category = new_category

    return split


def update_transaction_split_amount(
    split: TransactionSplit, new_amount: int
) -> TransactionSplit:

    split.amount = new_amount
    return split


def delete_transaction_split(session: Session, split: TransactionSplit) -> None:
    session.delete(split)
