from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.application.transaction import (
    add_split_to_transaction_in_database,
    add_transaction_to_database,
    delete_transaction_from_database,
    get_all_transactions_from_database,
    update_split_amount_in_database,
    update_transaction_in_database,
    update_transaction_splits_in_database,
)
from meyno.database.models import Account, Category, Transaction, TransactionSplit
from meyno.exceptions.transaction import (
    TransactionConversionError,
    TransactionNotFoundError,
    TransferConversionError,
)
from meyno.schemas.transaction import (
    TransactionCreate,
    TransactionSplitCreate,
    TransactionUpdate,
)


def create_default_transaction(session: Session, account: Account) -> Transaction:
    with session.begin():
        transaction_data = TransactionCreate(account_id=account.account_id)

        transaction = add_transaction_to_database(
            session=session, transaction_data=transaction_data
        )

        split_data = TransactionSplitCreate()

        add_split_to_transaction_in_database(
            session, transaction, split_data=split_data
        )

        return transaction


def get_all_transactions(session: Session) -> list[Transaction]:
    return get_all_transactions_from_database(session)


def update_transaction(
    session: Session, transaction: Transaction, update: TransactionUpdate
) -> Transaction:

    with session.begin():
        if update.amount is not None:
            _update_transaction_amount(session, transaction, update.amount)

        return update_transaction_in_database(transaction, update)


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
            outgoing = _find_outgoing_side_of_transfer(session, transaction)

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
            raise TransactionConversionError

        # Check if this not incoming side of a transfer
        outgoing = _find_outgoing_side_of_transfer(transaction)

        if outgoing is not None:
            raise TransactionConversionError

        # Create a transaction in other account with opposite amount
        transfer_transaction = add_transaction_to_database(
            session,
            TransactionCreate(
                account_id=transfer_account.account_id, amount=-1 * transaction.amount
            ),
        )

        # Set splits to empty for input transaction
        update_transaction_splits_in_database(transaction, [])

        transaction.transfer_transaction = transfer_transaction

        return transaction


def convert_transfer_to_transaction(
    session: Session, transaction: Transaction
) -> Transaction:

    with session.begin():
        if transaction.transfer_transaction is not None:
            # Input is the outgoing side of the transfer.
            other_side = transaction.transfer_transaction

            # Break the transfer relationship.
            transaction.transfer_transaction = None

        else:
            # Input may be the incoming side of the transfer.
            other_side = _find_outgoing_side_of_transfer(session, transaction)

            if other_side is None:
                raise TransferConversionError

            # Break the transfer relationship from the outgoing side.
            other_side.transfer_transaction = None

        # Make the input transaction a normal transaction
        # by giving it a single uncategorized split.
        add_split_to_transaction_in_database(
            session,
            transaction=transaction,
            split_data=TransactionSplitCreate(
                amount=transaction.amount,
                category_id=None,
            ),
        )

        # Delete the other side of the transfer.
        delete_transaction_from_database(session, other_side)

        return transaction


def add_split_to_transaction(
    session: Session,
    transaction: Transaction,
    amount: int = 0,
    category: Category | None = None,
) -> TransactionSplit:

    with session.begin():
        split_data = TransactionSplitCreate(amount=amount)

        if category is not None:
            split_data.category_id = category.category_id

        return add_split_to_transaction_in_database(session, transaction, split_data)


def _update_transaction_amount(
    session: Session, transaction: Transaction, new_amount: int
) -> None:

    if len(transaction.splits) == 1:
        # "Normal" non-transfer transaction
        # Update the only split amount as well
        update_split_amount_in_database(transaction.splits[0], new_amount)
    elif len(transaction.splits) > 1:
        split_total = _get_split_amount_total(transaction)

        diff = new_amount - split_total

        if diff != 0:
            add_split_to_transaction_in_database(
                session,
                transaction,
                TransactionSplitCreate(amount=diff, category_id=None),
            )
    elif len(transaction.splits) == 0:
        # Transfer
        # Update other side of transaction
        if transaction.transfer_transaction is not None:
            # Input transaction is outgoing side
            update_transaction_in_database(
                transaction.transfer_transaction,
                TransactionUpdate(amount=-1 * new_amount),
            )
        else:
            # Input transaction is incoming side
            # Find outgoing side
            outgoing = _find_outgoing_side_of_transfer(session, transaction)

            if outgoing is None:
                raise TransactionNotFoundError(
                    "Could not find outgoing side of transfer"
                )

            update_transaction_in_database(
                outgoing, TransactionUpdate(amount=-1 * new_amount)
            )


def _get_split_amount_total(transaction: Transaction) -> int:
    total = 0
    for split in transaction.splits:
        total += split.amount

    return total


def _find_outgoing_side_of_transfer(
    session: Session, transaction: Transaction
) -> Transaction | None:

    outgoing = session.scalars(
        select(Transaction).where(
            Transaction.transfer_transaction_id == transaction.transaction_id
        )
    ).first()

    return outgoing
