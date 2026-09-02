from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from meyno.database.models import Account, Category, Transaction, TransactionSplit

if TYPE_CHECKING:
    from meyno.schemas.transaction import (
        TransactionCreate,
        TransactionSplitCreate,
        TransactionUpdate,
    )


def get_transaction_by_id_from_database(
    session: Session, transaction_id: int
) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def get_all_transactions_from_database(session: Session) -> list[Transaction]:
    return list(session.scalars(select(Transaction)))


def get_all_transactions_for_account_from_database(
    account: Account,
) -> list[Transaction]:

    return list(account.transactions)


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


def update_transaction_in_database(
    transaction: Transaction,
    update: TransactionUpdate,
) -> Transaction:

    if update.date is not None:
        transaction.date = update.date

    if update.account_id is not None:
        transaction.account_id = update.account_id

    if update.payee_id is not None:
        transaction.payee_id = update.payee_id

    if update.amount is not None:
        transaction.amount = update.amount

    if update.notes is not None:
        transaction.notes = update.notes

    return transaction


def update_transaction_splits_in_database(
    transaction: Transaction,
    new_splits: list[TransactionSplit],
) -> Transaction:

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


def update_split_category_in_database(
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
