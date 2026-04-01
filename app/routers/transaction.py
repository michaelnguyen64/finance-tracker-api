from __future__ import annotations

from datetime import date as Date

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.tasks import LARGE_TRANSACTION_THRESHOLD, alert_large_transaction
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.services import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=PaginatedResponse[TransactionResponse])
async def list_transactions(
    category_id: int | None = Query(default=None),
    type: TransactionType | None = Query(default=None),
    date_from: Date | None = Query(default=None),
    date_to: Date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[TransactionResponse]:
    return await transaction_service.list_transactions(
        db,
        current_user.id,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    return await transaction_service.get_transaction(db, transaction_id, current_user.id)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    body: TransactionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    result = await transaction_service.create_transaction(db, current_user.id, body)
    if result.amount >= LARGE_TRANSACTION_THRESHOLD:
        background_tasks.add_task(
            alert_large_transaction,
            transaction_id=result.id,
            amount=result.amount,
            user_id=current_user.id,
        )
    return result


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    body: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    return await transaction_service.update_transaction(db, transaction_id, current_user.id, body)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await transaction_service.delete_transaction(db, transaction_id, current_user.id)
