from turtle import back
from typing import List, Optional
from decimal import Decimal

from datetime import date
from sqlalchemy import String, Date, Numeric, ForeignKey, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String) # TODO: Make this a hashed value or something
    full_name: Mapped[Optional[str]] = mapped_column(String)
    
    accounts: Mapped[List["Account"]] = relationship(back_populates="owner")
    
class Account(Base):
    __tablename__ = "account"
    
    account_id: Mapped[int] = mapped_column(primary_key=True)
    account_name: Mapped[str] = mapped_column(String)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)
    
    owner: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="account")
    
class Payee(Base):
    __tablename__ = "payee"
    
    payee_id: Mapped[int] = mapped_column(primary_key=True)
    payee_name: Mapped[str] = mapped_column(String, unique=True)
    
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="payee")
    
class Category(Base):
    __tablename__ = "category"
    
    category_id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String, unique=True)
    
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="category")
    
class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date)
    payee_id: Mapped[int] = mapped_column(ForeignKey("payee.payee_id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.category_id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False, default=Decimal("0.00"), server_default=text("0.00"))

    account: Mapped["Account"] = relationship(back_populates="transactions")
    payee: Mapped["Payee"] = relationship(back_populates="transactions")
    category: Mapped["Category"] = relationship(back_populates="transactions")


engine = create_engine("sqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)

