from __future__ import annotations

from datetime import date as Date
from decimal import Decimal

from pydantic import AliasPath, BaseModel, Field, field_validator

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    amount: Decimal
    type: TransactionType
    note: str | None = None
    date: Date
    category_id: int

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class TransactionUpdate(BaseModel):
    amount: Decimal | None = None
    type: TransactionType | None = None
    note: str | None = None
    date: Date | None = None
    category_id: int | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Amount must be positive")
        return v


class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    type: TransactionType
    note: str | None
    date: Date
    category_id: int
    category_name: str = Field(validation_alias=AliasPath("category", "name"))
    user_id: int

    model_config = {"from_attributes": True, "populate_by_name": True}
