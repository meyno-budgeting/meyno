import datetime

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    date: datetime.date = Field(
        default_factory=lambda: datetime.datetime.now().astimezone().date()
    )
    account_id: int
    amount: int = 0
    payee_id: int | None = None
    notes: str | None = None
    splits: list[TransactionSplitCreate] | None = None


class TransactionUpdate(BaseModel):
    date: datetime.date | None = None
    account_id: int | None = None
    payee_id: int | None = None
    amount: int | None = None
    notes: str | None = None
    splits: list[TransactionSplitCreate] | None = None


class TransactionSplitCreate(BaseModel):
    amount: int = 0
    category_id: int | None = None
