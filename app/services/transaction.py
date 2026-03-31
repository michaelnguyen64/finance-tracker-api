from __future__ import annotations

from datetime import date as Date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.transaction import TransactionType
from app.repositories import category as category_repo
from app.repositories import transaction as transaction_repo
from app.schemas.common import PaginatedResponse
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate


async def list_transactions(
    db: AsyncSession,
    user_id: int,
    category_id: int | None = None,
    type: TransactionType | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedResponse[TransactionResponse]:
    transactions, total = await transaction_repo.get_all(
        db,
        user_id,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return PaginatedResponse(
        data=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_transaction(
    db: AsyncSession, transaction_id: int, user_id: int
) -> TransactionResponse:
    transaction = await transaction_repo.get_by_id(db, transaction_id, user_id)
    if not transaction:
        raise NotFoundException("Transaction not found")
    return TransactionResponse.model_validate(transaction)


async def create_transaction(
    db: AsyncSession, user_id: int, body: TransactionCreate
) -> TransactionResponse:
    category = await category_repo.get_by_id(db, body.category_id, user_id)
    if not category:
        raise NotFoundException("Category not found")

    if body.type.value != category.type.value:
        raise BadRequestException(
            f"Transaction type '{body.type.value}' does not match"
            f" category type '{category.type.value}'"
        )

    transaction = await transaction_repo.create(
        db,
        user_id=user_id,
        amount=body.amount,
        type=body.type,
        note=body.note,
        date=body.date,
        category_id=body.category_id,
    )
    return TransactionResponse.model_validate(transaction)


async def update_transaction(
    db: AsyncSession, transaction_id: int, user_id: int, body: TransactionUpdate
) -> TransactionResponse:
    transaction = await transaction_repo.get_by_id(db, transaction_id, user_id)
    if not transaction:
        raise NotFoundException("Transaction not found")

    if body.category_id is not None or body.type is not None:
        effective_category_id = (
            body.category_id if body.category_id is not None else transaction.category_id
        )
        category = await category_repo.get_by_id(db, effective_category_id, user_id)
        if not category:
            raise NotFoundException("Category not found")
        effective_type = body.type if body.type is not None else transaction.type
        if effective_type.value != category.type.value:
            raise BadRequestException(
                f"Transaction type '{effective_type.value}' does not match"
                f" category type '{category.type.value}'"
            )

    updated = await transaction_repo.update(
        db,
        transaction,
        amount=body.amount,
        type=body.type,
        note=body.note,
        date=body.date,
        category_id=body.category_id,
    )
    return TransactionResponse.model_validate(updated)


async def delete_transaction(db: AsyncSession, transaction_id: int, user_id: int) -> None:
    transaction = await transaction_repo.get_by_id(db, transaction_id, user_id)
    if not transaction:
        raise NotFoundException("Transaction not found")
    await transaction_repo.delete(db, transaction)
