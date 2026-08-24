import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Account, Payee, Transaction, TransactionSplit


def get_transaction_by_id(session: Session, transaction_id: int) -> Transaction | None:
    return session.get(Transaction, transaction_id)


# TODO(ChaoticDefense): Wishlist: Possibly make a TransactionData dataclass
# to pass arguments to this function that is validated before created
def create_transaction(  # noqa: PLR0913, PLR0917
    session: Session,
    account: Account,
    transaction_date: datetime.date | None = None,
    payee: Payee | None = None,
    amount: int = 0,
    notes: str | None = None,
) -> Transaction:

    # Default to today's date
    if transaction_date is None:
        transaction_date = datetime.datetime.now().astimezone().date()

    transaction = Transaction(
        account=account, payee=payee, date=transaction_date, amount=amount, notes=notes
    )

    session.add(transaction)
    session.flush()

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
            session.flush()
            return

        # This transaction is the incoming side.
        incoming = transaction

    # Break the transfer relationship before deleting either transaction.
    outgoing.transfer_transaction = None
    session.flush()

    # Delete both sides of the transfer.
    session.delete(outgoing)
    session.delete(incoming)
    session.flush()
