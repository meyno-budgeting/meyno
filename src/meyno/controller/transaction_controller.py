import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.application.transaction import (
    add_split_to_transaction_in_database,
    add_transaction_to_database,
    delete_transaction_from_database,
    get_all_transactions_from_database,
    update_split_amount_in_database,
    update_transaction_amount_in_database,
    update_transaction_date_in_database,
    update_transaction_notes_in_database,
    update_transaction_payee_in_database,
    update_transaction_splits_in_database,
)
from meyno.database.models import (
    Account,
    Category,
    Payee,
    Transaction,
    TransactionSplit,
)


def create_default_transaction(session: Session, account: Account) -> Transaction:
    with session.begin():
        default_transaction_date = datetime.datetime.now().astimezone().date()
        default_amount = 0

        transaction = add_transaction_to_database(
            session=session,
            date=default_transaction_date,
            account=account,
            amount=default_amount,
        )

        add_split_to_transaction_in_database(
            session, transaction, default_amount, category=None
        )

        return transaction


def get_all_transactions(session: Session) -> list[Transaction]:
    return get_all_transactions_from_database(session)


def update_transaction_date(
    session: Session, transaction: Transaction, new_date: datetime.date
) -> Transaction:

    with session.begin():
        return update_transaction_date_in_database(transaction, new_date)


def update_transaction_payee(
    session: Session, transaction: Transaction, new_payee: Payee | None
) -> Transaction:

    with session.begin():
        return update_transaction_payee_in_database(transaction, new_payee)


def update_transaction_amount(
    session: Session, transaction: Transaction, new_amount: int
) -> Transaction:

    with session.begin():
        if len(transaction.splits) == 1:
            # "Normal" non-transfer transaction
            # Update the only split amount as well
            update_split_amount_in_database(transaction.splits[0], new_amount)
        elif len(transaction.splits) > 1:
            split_total = _get_split_amount_total(transaction)

            diff = new_amount - split_total

            if diff != 0:
                add_split_to_transaction_in_database(
                    session, transaction, diff, category=None
                )
        elif len(transaction.splits) == 0:
            # Transfer
            # Update other side of transaction
            if transaction.transfer_transaction is not None:
                # Input transaction is outgoing side
                update_transaction_amount_in_database(
                    transaction.transfer_transaction, new_amount
                )
            else:
                # Input transaction is incoming side
                # Find outgoing side
                outgoing = find_outgoing_side_of_transfer(session, transaction)

                if outgoing is None:
                    # TODO(ChaoticDefense): Make this custom exception
                    raise ValueError("Could not find outgoing side of transfer")

                update_transaction_amount_in_database(outgoing, new_amount)

        # Update transaction amount
        transaction = update_transaction_amount_in_database(transaction, new_amount)

        return transaction


def update_transaction_notes(
    session: Session, transaction: Transaction, new_notes: str | None
) -> Transaction:

    with session.begin():
        return update_transaction_notes_in_database(transaction, new_notes)


def delete_transaction(session: Session, transaction: Transaction) -> None:
    # Deletion logic: deleting explicitly a transaction that is part of a transfer
    # will also delete the other part of the transfer.
    # Deleting a whole account will instead break the chain and delete all transactions
    # in the account, while keeping the other side in tact.

    with session.begin():
        # Check if transaction was part of a transfer
        if transaction.transfer_transaction is not None:
            # This transaction is the outgoing side.
            outgoing = transaction
            incoming = transaction.transfer_transaction
        else:
            # Check whether this transaction is the incoming side.
            outgoing = find_outgoing_side_of_transfer(session, transaction)

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


def convert_transaction_to_transfer(
    session: Session, transaction: Transaction, transfer_account: Account
) -> Transaction:

    with session.begin():
        if transaction.transfer_transaction is not None:
            raise ValueError("Transaction is already a transfer.")

        # Create a transaction in other account
        transfer_transaction = create_default_transaction(session, transfer_account)

        # Set amount of transfer side to equal and opposite
        update_transaction_amount_in_database(
            transfer_transaction, -1 * transaction.amount
        )

        # Set splits to empty for both sides
        update_transaction_splits_in_database(transaction, [])
        update_transaction_splits_in_database(transfer_transaction, [])

        transaction.transfer_transaction = transfer_transaction

        return transaction


def convert_transfer_to_transaction(
    session: Session, transaction: Transaction
) -> Transaction:

    with session.begin():
        if transaction.transfer_transaction is None:
            raise ValueError("Transaction is already not a transfer.")

        # Get incoming side of transfer
        transfer_transaction = transaction.transfer_transaction

        # Unlink outgoing transfer
        transaction.transfer_transaction = None

        # Make single split for transaction and set amount to transaction amount
        add_split_to_transaction_in_database(
            session, transaction=transaction, amount=transaction.amount, category=None
        )

        # Delete incoming side of transfer
        delete_transaction_from_database(transfer_transaction)

        return transaction


def add_split_to_transaction(
    session: Session,
    transaction: Transaction,
    amount: int = 0,
    category: Category | None = None,
) -> TransactionSplit:

    with session.begin():
        return add_split_to_transaction_in_database(
            session, transaction, amount, category
        )


def _get_split_amount_total(transaction: Transaction) -> int:
    total = 0
    for split in transaction.splits:
        total += split.amount

    return total


def find_outgoing_side_of_transfer(
    session: Session, transaction: Transaction
) -> Transaction | None:

    outgoing = session.scalars(
        select(Transaction).where(
            Transaction.transfer_transaction_id == transaction.transaction_id
        )
    ).first()

    return outgoing
