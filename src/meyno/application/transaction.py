import datetime

from sqlalchemy.orm import Session

from meyno.database.models import (
    Account,
    Category,
    Payee,
    Transaction,
    TransactionSplit,
)


def get_transaction_by_id_from_database(
    session: Session, transaction_id: int
) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def add_transaction_to_database(
    session: Session,
    date: datetime.date,
    account: Account,
    amount: int,
    payee: Payee | None = None,
    notes: str | None = None,
) -> Transaction:

    transaction = Transaction(
        date=date,
        account=account,
        amount=amount,
        payee=payee,
        notes=notes,
    )

    session.add(transaction)

    return transaction


def update_transaction_date_in_database(
    transaction: Transaction, new_date: datetime.date
) -> Transaction:

    transaction.date = new_date

    return transaction


def update_transaction_account_in_database(
    transaction: Transaction, new_account: Account
) -> Transaction:

    transaction.account = new_account

    return transaction


def update_transaction_payee_in_database(
    transaction: Transaction, new_payee: Payee | None
) -> Transaction:

    transaction.payee = new_payee

    return transaction


def update_transaction_amount_in_database(
    transaction: Transaction, new_amount: int
) -> Transaction:

    transaction.amount = new_amount

    return transaction


def update_transaction_notes_in_database(
    transaction: Transaction, new_notes: str | None
) -> Transaction:

    transaction.notes = new_notes

    return transaction


def update_transaction_splits_in_database(
    transaction: Transaction, new_splits: list[TransactionSplit] | None
) -> Transaction:

    if new_splits is None:
        new_splits = []

    transaction.splits = new_splits

    return transaction


def delete_transaction_from_database(
    session: Session, transaction: Transaction
) -> None:
    session.delete(transaction)


def add_split_to_transaction(
    session: Session,
    transaction: Transaction,
    amount: int,
    category: Category | None = None,
) -> TransactionSplit:

    split = TransactionSplit(transaction=transaction, category=category, amount=amount)

    session.add(split)
    return split


def get_split_by_id_from_database(
    session: Session, split_id: int
) -> TransactionSplit | None:
    return session.get(TransactionSplit, split_id)


def update_split_category(
    split: TransactionSplit, new_category: Category
) -> TransactionSplit:

    split.category = new_category

    return split


def update_split_amount_in_database(
    split: TransactionSplit, new_amount: int
) -> TransactionSplit:

    split.amount = new_amount
    return split


def delete_split_from_transaction(session: Session, split: TransactionSplit) -> None:
    session.delete(split)
