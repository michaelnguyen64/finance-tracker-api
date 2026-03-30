from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.summary import MonthlySummary
from app.services import summary as summary_service

router = APIRouter(tags=["summary"])


@router.get("/summary", response_model=list[MonthlySummary])
async def get_summary(
    month: str | None = Query(
        default=None, pattern=r"^\d{4}-\d{2}$", description="Filter by month (YYYY-MM)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MonthlySummary]:
    return await summary_service.get_summary(db, current_user.id, month)
