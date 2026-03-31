from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.repositories import category as category_repo
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import PaginatedResponse


async def list_categories(
    db: AsyncSession,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedResponse[CategoryResponse]:
    categories, total = await category_repo.get_all(db, user_id, limit=limit, offset=offset)
    return PaginatedResponse(
        data=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_category(db: AsyncSession, category_id: int, user_id: int) -> CategoryResponse:
    category = await category_repo.get_by_id(db, category_id, user_id)
    if not category:
        raise NotFoundException("Category not found")
    return CategoryResponse.model_validate(category)


async def create_category(db: AsyncSession, user_id: int, body: CategoryCreate) -> CategoryResponse:
    category = await category_repo.create(db, user_id=user_id, name=body.name, type=body.type)
    return CategoryResponse.model_validate(category)


async def update_category(
    db: AsyncSession, category_id: int, user_id: int, body: CategoryUpdate
) -> CategoryResponse:
    category = await category_repo.get_by_id(db, category_id, user_id)
    if not category:
        raise NotFoundException("Category not found")
    updated = await category_repo.update(db, category, name=body.name, type=body.type)
    return CategoryResponse.model_validate(updated)


async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> None:
    category = await category_repo.get_by_id(db, category_id, user_id)
    if not category:
        raise NotFoundException("Category not found")
    try:
        await category_repo.delete(db, category)
    except IntegrityError:
        await db.rollback()
        raise ConflictException("Category has existing transactions and cannot be deleted")
