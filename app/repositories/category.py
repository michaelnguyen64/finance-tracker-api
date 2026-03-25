from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def get_all(db: AsyncSession, user_id: int) -> list[Category]:
    result = await db.execute(select(Category).where(Category.user_id == user_id))
    return list(result.scalars().all())


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
