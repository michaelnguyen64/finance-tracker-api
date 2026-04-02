from __future__ import annotations

from datetime import date as Date

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction, TransactionType


async def get_all(
    db: AsyncSession,
    user_id: int,
    category_id: int | None = None,
    type: TransactionType | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Transaction], int]:
    conditions = [Transaction.user_id == user_id]

    if category_id is not None:
        conditions.append(Transaction.category_id == category_id)
    if type is not None:
        conditions.append(Transaction.type == type)
    if date_from is not None:
        conditions.append(Transaction.date >= date_from)
    if date_to is not None:
        conditions.append(Transaction.date <= date_to)

    total_result = await db.execute(select(func.count(Transaction.id)).where(*conditions))
    total = total_result.scalar_one()

    data_result = await db.execute(
        select(Transaction)
        .where(*conditions)
        .options(selectinload(Transaction.category))
        .order_by(desc(Transaction.date), desc(Transaction.id))
        .limit(limit)
        .offset(offset)
    )
    return list(data_result.scalars().all()), total


async def get_by_id(db: AsyncSession, transaction_id: int, user_id: int) -> Transaction | None:
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id, Transaction.user_id == user_id)
        .options(selectinload(Transaction.category))
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user_id: int, **kwargs: object) -> Transaction:
    transaction = Transaction(user_id=user_id, **kwargs)
    db.add(transaction)
    await db.flush()
    transaction_id = transaction.id
    await db.commit()
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(selectinload(Transaction.category))
    )
    return result.scalar_one()


async def update(db: AsyncSession, transaction: Transaction, **kwargs: object) -> Transaction:
    for key, value in kwargs.items():
        if value is not None:
            setattr(transaction, key, value)
    transaction_id = transaction.id
    await db.commit()
    # Reload with category so callers can access transaction.category.name
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(selectinload(Transaction.category))
    )
    return result.scalar_one()


async def delete(db: AsyncSession, transaction: Transaction) -> None:
    await db.delete(transaction)
    await db.commit()
