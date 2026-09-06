import datetime

from pydantic import BaseModel, Field

from meyno.utils import get_local_todays_date


class TransactionSplitCreate(BaseModel):
    amount: int = 0
    category_id: int | None = None


class TransactionCreate(BaseModel):
    date: datetime.date = Field(default_factory=get_local_todays_date)
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
