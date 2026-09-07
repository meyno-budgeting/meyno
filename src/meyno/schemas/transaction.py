import datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from meyno.exceptions.transaction import InvalidTransferCreateError
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


class TransferCreate(BaseModel):
    date: datetime.date = Field(default_factory=get_local_todays_date)
    outgoing_account_id: int
    incoming_account_id: int
    amount: int = 0
    notes: str | None = None

    @model_validator(mode="after")
    def validate_accounts(self) -> Self:
        if self.outgoing_account_id == self.incoming_account_id:
            raise InvalidTransferCreateError(
                "Outgoing and incoming accounts must be different"
            )

        return self


class TransactionUpdate(BaseModel):
    date: datetime.date | None = None
    account_id: int | None = None
    payee_id: int | None = None
    amount: int | None = None
    notes: str | None = None
    splits: list[TransactionSplitCreate] | None = None
