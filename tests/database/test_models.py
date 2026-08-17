from datetime import date

from meyno.database.models import (
    Account,
    Category,
    Payee,
    Transaction,
    TransactionSplit,
)


def test_insert_and_query(session):
    account = Account(name="Test Account")
    category = Category(name="Groceries")
    payee = Payee(name="Supermarket")

    session.add_all([account, category, payee])
    session.commit()

    transaction = Transaction(
        account_id=account.account_id,
        payee_id=payee.payee_id,
        date=date(2026, 8, 17),
        amount=5000,
        notes="Grocery shopping",
    )
    session.add(transaction)
    session.commit()

    split = TransactionSplit(
        transaction_id=transaction.transaction_id,
        category_id=category.category_id,
        amount=3000,
    )
    session.add(split)
    session.commit()

    queried_transaction = session.get(
        Transaction,
        transaction.transaction_id,
    )

    assert queried_transaction is not None
    assert queried_transaction.amount == 5000
    assert len(queried_transaction.splits) == 1
    assert queried_transaction.splits[0].amount == 3000