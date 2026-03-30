from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class MonthlySummary(BaseModel):
    month: str
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
