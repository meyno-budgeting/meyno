import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import (
    Account,
    Category,
    Payee,
    Transaction,
    TransactionSplit,
)

if TYPE_CHECKING:
    from meyno.schemas.transaction import TransactionCreate, TransactionSplitCreate


def get_transaction_by_id_from_database(
    session: Session, transaction_id: int
) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def get_all_transactions_from_database(session: Session) -> list[Transaction]:
    return session.scalars(select(Transaction))


def get_all_transactions_for_account_from_database(
    account: Account,
) -> list[Transaction]:

    return list(account.transactions)


def get_transactions_by_payee_from_database(
    session: Session,
    payee: Payee | None,
) -> list[Transaction]:

    if payee is None:
        statement = select(Transaction).where(Transaction.payee_id.is_(None))

        return list(session.scalars(statement))

    return list(payee.transactions)


def add_transaction_to_database(
    session: Session,
    transaction_data: TransactionCreate,
) -> Transaction:

    transaction = Transaction(
        date=transaction_data.date,
        account_id=transaction_data.account_id,
        amount=transaction_data.amount,
        payee_id=transaction_data.payee_id,
        notes=transaction_data.notes,
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


def add_split_to_transaction_in_database(
    session: Session, transaction: Transaction, split_data: TransactionSplitCreate
) -> TransactionSplit:

    split = TransactionSplit(
        transaction=transaction,
        category_id=split_data.category_id,
        amount=split_data.amount,
    )

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


def delete_split_from_transaction_in_database(
    session: Session, split: TransactionSplit
) -> None:
    session.delete(split)
