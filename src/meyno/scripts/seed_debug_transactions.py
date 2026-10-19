from datetime import date

from sqlalchemy.orm import Session

from meyno.controller.account import add_account, get_all_accounts
from meyno.controller.category import add_category, get_all_categories
from meyno.controller.payee import add_payee, get_all_payees
from meyno.controller.transaction import add_transaction, get_all_transactions
from meyno.database.connection import SessionLocal
from meyno.database.models import Account, Category, Payee
from meyno.schemas.transaction import TransactionCreate, TransactionSplitCreate


def get_or_create_account(session: Session, name: str) -> Account:
    for account in get_all_accounts(session):
        if account.name == name:
            return account

    return add_account(session, name)


def get_or_create_category(session: Session, name: str) -> Category:
    for category in get_all_categories(session):
        if category.name == name:
            return category

    return add_category(session, name)


def get_or_create_payee(session: Session, name: str) -> Payee:
    for payee in get_all_payees(session):
        if payee.name == name:
            return payee

    return add_payee(session, name)


def main() -> None:
    with SessionLocal() as session:
        account = get_or_create_account(session, "GUI Debug Checking")

        income_category = get_or_create_category(session, "GUI Debug Income")
        grocery_category = get_or_create_category(session, "GUI Debug Groceries")
        utility_category = get_or_create_category(session, "GUI Debug Utilities")

        employer = get_or_create_payee(session, "GUI Debug Employer")
        grocery_store = get_or_create_payee(session, "GUI Debug Grocery Store")
        utility_company = get_or_create_payee(session, "GUI Debug Electric Company")

        existing_notes = {
            transaction.notes for transaction in get_all_transactions(session)
        }

        examples = [
            (
                "GUI debug: paycheck",
                date(2026, 10, 1),
                employer,
                250000,
                income_category,
            ),
            (
                "GUI debug: groceries",
                date(2026, 10, 2),
                grocery_store,
                -8542,
                grocery_category,
            ),
            (
                "GUI debug: utilities",
                date(2026, 10, 3),
                utility_company,
                -12500,
                utility_category,
            ),
        ]

        for notes, transaction_date, payee, amount, category in examples:
            if notes in existing_notes:
                continue

            add_transaction(
                session,
                TransactionCreate(
                    date=transaction_date,
                    account_id=account.account_id,
                    payee_id=payee.payee_id,
                    amount=amount,
                    notes=notes,
                    splits=[
                        TransactionSplitCreate(
                            amount=amount,
                            category_id=category.category_id,
                        )
                    ],
                ),
            )

        print("Debug transactions are ready.")  # noqa: T201
        print(f"Account: {account.name}")  # noqa: T201
        print(f"Transactions in database: {len(get_all_transactions(session))}")  # noqa: T201


if __name__ == "__main__":
    main()
