from __future__ import annotations

from datetime import date as Date

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType


async def get_all(
    db: AsyncSession,
    user_id: int,
    category_id: int | None = None,
    type: TransactionType | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
) -> list[Transaction]:
    query = select(Transaction).where(Transaction.user_id == user_id)

    if category_id is not None:
        query = query.where(Transaction.category_id == category_id)
    if type is not None:
        query = query.where(Transaction.type == type)
    if date_from is not None:
        query = query.where(Transaction.date >= date_from)
    if date_to is not None:
        query = query.where(Transaction.date <= date_to)

    query = query.order_by(desc(Transaction.date), desc(Transaction.id))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, transaction_id: int, user_id: int) -> Transaction | None:
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user_id: int, **kwargs: object) -> Transaction:
    transaction = Transaction(user_id=user_id, **kwargs)
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def update(db: AsyncSession, transaction: Transaction, **kwargs: object) -> Transaction:
    for key, value in kwargs.items():
        if value is not None:
            setattr(transaction, key, value)
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def delete(db: AsyncSession, transaction: Transaction) -> None:
    await db.delete(transaction)
    await db.commit()
