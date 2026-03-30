from __future__ import annotations

from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType


async def get_monthly_summaries(
    db: AsyncSession,
    user_id: int,
    month: str | None = None,
) -> list[Any]:
    month_expr = func.to_char(Transaction.date, "YYYY-MM")

    conditions = [Transaction.user_id == user_id]
    if month is not None:
        conditions.append(month_expr == month)

    query = (
        select(
            month_expr.label("month"),
            func.sum(
                case((Transaction.type == TransactionType.income, Transaction.amount), else_=0)
            ).label("total_income"),
            func.sum(
                case((Transaction.type == TransactionType.expense, Transaction.amount), else_=0)
            ).label("total_expense"),
        )
        .where(*conditions)
        .group_by(month_expr)
        .order_by(month_expr)
    )

    result = await db.execute(query)
    return list(result.all())
