from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def get_all(
    db: AsyncSession,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Category], int]:
    conditions = [Category.user_id == user_id]

    total_result = await db.execute(select(func.count(Category.id)).where(*conditions))
    total = total_result.scalar_one()

    data_result = await db.execute(select(Category).where(*conditions).limit(limit).offset(offset))
    return list(data_result.scalars().all()), total


async def get_by_id(db: AsyncSession, category_id: int, user_id: int) -> Category | None:
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user_id: int, **kwargs: object) -> Category:
    category = Category(user_id=user_id, **kwargs)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update(db: AsyncSession, category: Category, **kwargs: object) -> Category:
    for key, value in kwargs.items():
        if value is not None:
            setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.commit()
