import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Account, Payee, Transaction, TransactionSplit


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

    transaction.splits = [
        TransactionSplit(
            category=None,
            amount=0,
        ),
    ]

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
