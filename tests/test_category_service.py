from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import ConflictException, NotFoundException
from app.models.category import Category, CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services import category as category_service


@pytest.mark.asyncio
async def test_list_categories_returns_all(mock_db: AsyncMock, sample_category: Category) -> None:
    with patch("app.services.category.category_repo.get_all", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = ([sample_category], 1)

        result = await category_service.list_categories(mock_db, user_id=1)

    assert result.total == 1
    assert len(result.data) == 1
    assert result.data[0].name == "Salary"


@pytest.mark.asyncio
async def test_get_category_not_found_raises_404(mock_db: AsyncMock) -> None:
    with patch("app.services.category.category_repo.get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        with pytest.raises(NotFoundException) as exc:
            await category_service.get_category(mock_db, category_id=99, user_id=1)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_create_category_success(mock_db: AsyncMock, sample_category: Category) -> None:
    body = CategoryCreate(name="Salary", type=CategoryType.income)

    with patch("app.services.category.category_repo.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = sample_category

        result = await category_service.create_category(mock_db, user_id=1, body=body)

    assert result.name == "Salary"
    assert result.type == CategoryType.income


@pytest.mark.asyncio
async def test_update_category_not_found_raises_404(mock_db: AsyncMock) -> None:
    body = CategoryUpdate(name="Updated")

    with patch("app.services.category.category_repo.get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        with pytest.raises(NotFoundException) as exc:
            await category_service.update_category(mock_db, category_id=99, user_id=1, body=body)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_with_transactions_raises_409(
    mock_db: AsyncMock, sample_category: Category
) -> None:
    from sqlalchemy.exc import IntegrityError

    with (
        patch("app.services.category.category_repo.get_by_id", new_callable=AsyncMock) as mock_get,
        patch("app.services.category.category_repo.delete", new_callable=AsyncMock) as mock_delete,
    ):
        mock_get.return_value = sample_category
        mock_delete.side_effect = IntegrityError(None, None, Exception())

        with pytest.raises(ConflictException) as exc:
            await category_service.delete_category(mock_db, category_id=1, user_id=1)

    assert exc.value.status_code == 409
    assert "transactions" in exc.value.message.lower()
