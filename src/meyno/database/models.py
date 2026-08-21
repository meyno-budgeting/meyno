from datetime import date as datetype

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from meyno.database.base import Base


class Account(Base):
    __tablename__ = "account"

    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    transactions: Mapped[list[Transaction]] = relationship(back_populates="account")

    def __repr__(self) -> str:
        return f"Account(account_id={self.account_id!r}, name={self.name!r})"


class Category(Base):
    __tablename__ = "category"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    transaction_splits: Mapped[list[TransactionSplit]] = relationship(
        back_populates="category"
    )

    def __repr__(self) -> str:
        return f"Category(category_id={self.category_id!r}, name={self.name!r})"


class Payee(Base):
    __tablename__ = "payee"

    payee_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    transactions: Mapped[list[Transaction]] = relationship(back_populates="payee")

    def __repr__(self) -> str:
        return f"Payee(payee_id={self.payee_id!r}, name={self.name!r})"


class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey(column="account.account_id"),
        nullable=False,
    )

    payee_id: Mapped[int] = mapped_column(
        ForeignKey(column="payee.payee_id"),
        nullable=False,
    )

    date: Mapped[datetype] = mapped_column(Date, nullable=False)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    notes: Mapped[str | None] = mapped_column(String(75), nullable=True)

    transfer_transaction_id: Mapped[int | None] = mapped_column(
        ForeignKey(column="transaction.transaction_id"), nullable=True
    )

    account: Mapped[Account] = relationship(back_populates="transactions")

    payee: Mapped[Payee] = relationship(back_populates="transactions")

    splits: Mapped[list[TransactionSplit]] = relationship(
        back_populates="transaction",
        cascade="all, delete-orphan",
    )

    transfer_transaction: Mapped[Transaction | None] = relationship(
        remote_side="Transaction.transaction_id",
        foreign_keys=[transfer_transaction_id],
        post_update=True,
    )

    def __repr__(self) -> str:
        return (
            f"Transaction("
            f"transaction_id={self.transaction_id!r}, "
            f"account_id={self.account_id!r}, "
            f"payee_id={self.payee_id!r}, "
            f"date={self.date!r}, "
            f"amount={self.amount!r}, "
            f"notes={self.notes!r}, "
            f"transfer_transaction_id={self.transfer_transaction_id!r}"
            f")"
        )


class TransactionSplit(Base):
    __tablename__ = "transaction_split"

    ## Columns
    transaction_split_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transaction.transaction_id"), nullable=False
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("category.category_id"), nullable=True
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    ## Relationships
    transaction: Mapped[Transaction] = relationship(back_populates="splits")

    category: Mapped[Category | None] = relationship(
        back_populates="transaction_splits"
    )

    def __repr__(self) -> str:
        return (
            f"TransactionSplit("
            f"transaction_split_id={self.transaction_split_id!r}, "
            f"transaction_id={self.transaction_id!r}, "
            f"category_id={self.category_id!r}, "
            f"amount={self.amount!r} "
            f")"
        )
