from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from meyno.database.base import Base


class Account(Base):
    __tablename__ = "account"
    
    account_id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates = "account"
    )
    
class Category(Base):
    __tablename__ = "category"
    
    category_id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    
    transaction_splits: Mapped[list[TransactionSplit]] = relationship(
        back_populates = "category")
    
class Payee(Base):
    __tablename__ = "payee"

    payee_id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)

    transactions: Mapped[list[Transaction]] = relationship(
        back_populates = "payee"
    )

class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id: Mapped[int] = mapped_column(Integer, primary_key = True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.account_id"),
        nullable = False,
    )

    payee_id: Mapped[int] = mapped_column(
        ForeignKey("payee.payee_id"),
        nullable = False,
    )

    date: Mapped[date] = mapped_column(Date, nullable = False)

    amount: Mapped[int] = mapped_column(Integer, nullable = False)

    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    transfer_transaction_id: Mapped[int | None] = mapped_column(
        ForeignKey("transaction.transaction_id"),
        nullable = True,
    )

    account: Mapped[Account] = relationship(
        back_populates = "transactions"
    )

    payee: Mapped[Payee] = relationship(
        back_populates = "transactions"
    )

    splits: Mapped[list[TransactionSplit]] = relationship(
        back_populates = "transaction",
        cascade = "all, delete-orphan",
    )

    transfer_transaction: Mapped[Transaction | None] = relationship(
        remote_side = "Transaction.transaction_id",
        foreign_keys = [transfer_transaction_id],
    )

class TransactionSplit(Base):
    __tablename__ = "transaction_split"

    transaction_split_id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True,
    )

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transaction.transaction_id"),
        nullable=False,
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("category.category_id"),
        nullable = True,
    )

    amount: Mapped[int] = mapped_column(Integer, nullable = False)

    transaction: Mapped[Transaction] = relationship(
        back_populates = "splits"
    )

    category: Mapped[Category | None] = relationship(
        back_populates = "transaction_splits"
    )