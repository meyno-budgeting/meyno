from typing import List, Optional

from sqlalchemy import String, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String) # TODO: Make this a hashed value or something
    full_name: Mapped[Optional[str]] = mapped_column(String)
    
    accounts: Mapped[List["Account"]] = relationship(back_populates="owner")

    
class Account(Base):
    __tablename__ = "account"
    
    account_id: Mapped[int] = mapped_column(primary_key=True)
    account_name: Mapped[str] = mapped_column(String)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)
    
    owner: Mapped["User"] = relationship(back_populates="accounts")
    
engine = create_engine("sqlite:///:memory:", echo=True)

Base.metadata.create_all(engine)