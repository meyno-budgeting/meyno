import datetime
from unicodedata import category

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    date: datetime.date = Field(
        default_factory=lambda: datetime.datetime.now().astimezone().date()
    )
    account_id: int
    amount: int = 0
    payee_id: int | None = None
    notes: str | None = None


class TransactionSplitCreate(BaseModel):
    amount: int = 0
    category_id: int | None = None
