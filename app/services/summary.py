from __future__ import annotations

from decimal import Decimal

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import summary as summary_repo
from app.schemas.summary import MonthlySummary

logger = structlog.get_logger(__name__)


async def get_summary(
    db: AsyncSession,
    user_id: int,
    month: str | None = None,
) -> list[MonthlySummary]:
    logger.info("summary_requested", user_id=user_id, month=month)
    rows = await summary_repo.get_monthly_summaries(db, user_id, month)
    return [
        MonthlySummary(
            month=row.month,
            total_income=row.total_income or Decimal(0),
            total_expense=row.total_expense or Decimal(0),
            net_balance=(row.total_income or Decimal(0)) - (row.total_expense or Decimal(0)),
        )
        for row in rows
    ]
