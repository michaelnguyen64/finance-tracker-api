from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


async def get_all(db: AsyncSession, user_id: int) -> list[Transaction]:
    result = await db.execute(select(Transaction).where(Transaction.user_id == user_id))
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
