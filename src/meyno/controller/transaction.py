from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from meyno.application.transaction import (
    add_split_to_transaction_in_database,
    add_transaction_to_database,
    delete_transaction_from_database,
    get_all_transactions_for_account_from_database,
    get_all_transactions_from_database,
    get_transaction_by_id_from_database,
    update_split_amount_in_database,
    update_transaction_in_database,
)
from meyno.exceptions.transaction import (
    InvalidTransactionError,
    TransactionConversionError,
    TransactionNotFoundError,
    TransferConversionError,
    TransferOtherSideNotFoundError,
)
from meyno.schemas.transaction import (
    TransactionCreate,
    TransactionSplitCreate,
    TransactionUpdate,
    TransferCreate,
)
from meyno.utils import controller_write

if TYPE_CHECKING:
    from meyno.database.models import Account, Transaction, TransactionSplit


def add_transaction(
    session: Session, transaction_data: TransactionCreate
) -> Transaction:
    with controller_write(session):
        transaction = add_transaction_to_database(session, transaction_data)

        session.flush()

        splits = transaction_data.splits
        if splits is None:
            splits = [TransactionSplitCreate(amount=transaction.amount)]

        for split_data in splits:
            add_split_to_transaction_in_database(session, transaction, split_data)

        _validate_transaction(transaction)

        return transaction


def add_transfer(session: Session, transfer_data: TransferCreate) -> Transaction:
    with controller_write(session):
        left_side = add_transaction_to_database(
            session,
            TransactionCreate(
                date=transfer_data.date,
                account_id=transfer_data.left_side_account_id,
                amount=transfer_data.amount,
                splits=[],
                notes=transfer_data.notes,
            ),
        )

        right_side = add_transaction_to_database(
            session,
            TransactionCreate(
                date=transfer_data.date,
                account_id=transfer_data.right_side_account_id,
                amount=-transfer_data.amount,
                splits=[],
                notes=transfer_data.notes,
            ),
        )

        left_side.transfer_right_side = right_side

        session.flush()

        _validate_transaction(left_side)
        _validate_transaction(right_side)

        return left_side


def get_transaction_by_id(session: Session, transaction_id: int) -> Transaction | None:
    transaction = get_transaction_by_id_from_database(session, transaction_id)

    if transaction is None:
        raise (TransactionNotFoundError(transaction_id))

    return transaction


def get_all_transactions(session: Session) -> list[Transaction]:
    return get_all_transactions_from_database(session)


def get_all_transactions_for_account(
    session: Session, account: Account
) -> list[Transaction]:

    return get_all_transactions_for_account_from_database(session, account)


def update_transaction(
    session: Session, transaction: Transaction, update: TransactionUpdate
) -> Transaction:

    with controller_write(session):
        if update.amount is not None:
            _handle_transaction_amount_update(session, transaction, update.amount)

        update_transaction_in_database(transaction, update)

        _validate_transaction(transaction)

        return transaction


def delete_transaction(session: Session, transaction: Transaction) -> None:
    # Deletion logic: deleting explicitly a transaction that is part of a transfer
    # will also delete the other part of the transfer.
    # Deleting a whole account will instead break the chain and delete all transactions
    # in the account, while keeping the other side in tact.

    with controller_write(session):
        other_side = transaction.transfer_other_side

        if other_side is None:
            # This transaction is not part of a transfer.
            session.delete(transaction)
            return

        # Break the transfer relationship from whichever side owns it.
        if transaction.transfer_right_side is not None:
            transaction.transfer_right_side = None
        else:
            other_side.transfer_right_side = None

        # Delete both sides of the transfer.
        session.delete(transaction)
        session.delete(other_side)


def convert_transaction_to_transfer(
    session: Session, transaction: Transaction, transfer_account: Account
) -> Transaction:

    with controller_write(session):
        if transaction.transfer_other_side is not None:
            raise TransactionConversionError

        # Create a transaction in other account with opposite amount
        transfer_transaction = add_transaction_to_database(
            session,
            TransactionCreate(
                account_id=transfer_account.account_id,
                amount=-1 * transaction.amount,
            ),
        )

        # Set splits to empty for input transaction
        update_transaction_in_database(
            transaction,
            TransactionUpdate(splits=[]),
        )

        # Set splits to empty for input transaction
        update_transaction_in_database(
            transfer_transaction,
            TransactionUpdate(splits=[]),
        )

        transaction.transfer_right_side = transfer_transaction

        session.flush()

        _validate_transaction(transaction)
        _validate_transaction(transfer_transaction)

        return transaction


def convert_transfer_to_transaction(
    session: Session, transaction: Transaction
) -> Transaction:

    with controller_write(session):
        other_side = transaction.transfer_other_side

        if other_side is None:
            raise TransferConversionError

        # Break the transfer relationship from whichever side owns it.
        if transaction.transfer_right_side is not None:
            transaction.transfer_right_side = None
        else:
            other_side.transfer_right_side = None

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

        _validate_transaction(transaction)

        return transaction


def add_split_to_transaction(
    session: Session, transaction: Transaction, split_data: TransactionSplitCreate
) -> TransactionSplit:

    with controller_write(session):
        split = add_split_to_transaction_in_database(session, transaction, split_data)

        session.flush()

        # Update transaction total to be the new split total
        new_total = _get_split_amount_total(transaction)
        update_transaction_in_database(
            transaction,
            TransactionUpdate(amount=new_total),
        )
        return split


def _handle_transaction_amount_update(
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
        other_side = transaction.transfer_other_side

        if other_side is None:
            raise TransferOtherSideNotFoundError(
                "Could not find other side of transfer"
            )

        update_transaction_in_database(
            other_side,
            TransactionUpdate(amount=-1 * new_amount),
        )


def _get_split_amount_total(transaction: Transaction) -> int:
    total = 0
    for split in transaction.splits:
        total += split.amount

    return total


def _validate_transaction(transaction: Transaction) -> None:
    if len(transaction.splits) > 0:
        if transaction.transfer_right_side is not None:
            raise InvalidTransactionError("A transfer cannot have splits!")

        if _get_split_amount_total(transaction) != transaction.amount:
            raise InvalidTransactionError(
                "Splits total does not match Transaction amount!"
            )

        return

    # No splits means this must be a transfer.
    other_side = transaction.transfer_other_side

    if other_side is None:
        raise InvalidTransactionError("Transaction is not part of a valid transfer!")

    if other_side.amount != -transaction.amount:
        raise InvalidTransactionError("Transfer amounts do not match!")
