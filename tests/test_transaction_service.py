from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services import transaction as transaction_service


@pytest.mark.asyncio
async def test_list_transactions_returns_all(
    mock_db: AsyncMock, sample_transaction: Transaction
) -> None:
    with patch(
        "app.services.transaction.transaction_repo.get_all", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = ([sample_transaction], 1)

        result = await transaction_service.list_transactions(mock_db, user_id=1)

    assert result.total == 1
    assert len(result.data) == 1
    assert result.data[0].amount == Decimal("1000000")


@pytest.mark.asyncio
async def test_list_transactions_passes_filters(mock_db: AsyncMock) -> None:
    with patch(
        "app.services.transaction.transaction_repo.get_all", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = ([], 0)

        await transaction_service.list_transactions(
            mock_db,
            user_id=1,
            category_id=2,
            type=TransactionType.expense,
            date_from=date(2024, 3, 1),
            date_to=date(2024, 3, 31),
        )

        mock_get.assert_called_once_with(
            mock_db,
            1,
            category_id=2,
            type=TransactionType.expense,
            date_from=date(2024, 3, 1),
            date_to=date(2024, 3, 31),
            limit=20,
            offset=0,
        )


@pytest.mark.asyncio
async def test_get_transaction_not_found_raises_404(mock_db: AsyncMock) -> None:
    with patch(
        "app.services.transaction.transaction_repo.get_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None

        with pytest.raises(HTTPException) as exc:
            await transaction_service.get_transaction(mock_db, transaction_id=99, user_id=1)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_create_transaction_mismatched_type_raises_400(
    mock_db: AsyncMock, sample_category: Category
) -> None:
    body = TransactionCreate(
        amount=Decimal("500"),
        type=TransactionType.expense,
        date=date(2024, 3, 1),
        category_id=1,
    )

    with patch(
        "app.services.transaction.category_repo.get_by_id", new_callable=AsyncMock
    ) as mock_cat:
        mock_cat.return_value = sample_category

        with pytest.raises(HTTPException) as exc:
            await transaction_service.create_transaction(mock_db, user_id=1, body=body)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_transaction_invalid_category_raises_404(mock_db: AsyncMock) -> None:
    body = TransactionCreate(
        amount=Decimal("500"),
        type=TransactionType.income,
        date=date(2024, 3, 1),
        category_id=99,
    )

    with patch(
        "app.services.transaction.category_repo.get_by_id", new_callable=AsyncMock
    ) as mock_cat:
        mock_cat.return_value = None

        with pytest.raises(HTTPException) as exc:
            await transaction_service.create_transaction(mock_db, user_id=1, body=body)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_create_transaction_success(
    mock_db: AsyncMock, sample_category: Category, sample_transaction: Transaction
) -> None:
    body = TransactionCreate(
        amount=Decimal("1000000"),
        type=TransactionType.income,
        date=date(2024, 3, 1),
        category_id=1,
    )

    with (
        patch(
            "app.services.transaction.category_repo.get_by_id", new_callable=AsyncMock
        ) as mock_cat,
        patch(
            "app.services.transaction.transaction_repo.create", new_callable=AsyncMock
        ) as mock_create,
    ):
        mock_cat.return_value = sample_category
        mock_create.return_value = sample_transaction

        result = await transaction_service.create_transaction(mock_db, user_id=1, body=body)

    assert result.amount == Decimal("1000000")
    assert result.type == TransactionType.income


@pytest.mark.asyncio
async def test_update_transaction_type_mismatch_raises_400(
    mock_db: AsyncMock, sample_transaction: Transaction, sample_category: Category
) -> None:
    body = TransactionUpdate(type=TransactionType.expense)

    with (
        patch(
            "app.services.transaction.transaction_repo.get_by_id", new_callable=AsyncMock
        ) as mock_tx,
        patch(
            "app.services.transaction.category_repo.get_by_id", new_callable=AsyncMock
        ) as mock_cat,
    ):
        mock_tx.return_value = sample_transaction
        mock_cat.return_value = sample_category

        with pytest.raises(HTTPException) as exc:
            await transaction_service.update_transaction(
                mock_db, transaction_id=1, user_id=1, body=body
            )

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_delete_transaction_not_found_raises_404(mock_db: AsyncMock) -> None:
    with patch(
        "app.services.transaction.transaction_repo.get_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None

        with pytest.raises(HTTPException) as exc:
            await transaction_service.delete_transaction(mock_db, transaction_id=99, user_id=1)

    assert exc.value.status_code == 404
