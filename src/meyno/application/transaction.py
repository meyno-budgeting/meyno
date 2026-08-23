import datetime

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
