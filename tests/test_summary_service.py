from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import summary as summary_service


@pytest.mark.asyncio
async def test_get_summary_returns_monthly_totals(mock_db: AsyncMock) -> None:
    mock_row = MagicMock()
    mock_row.month = "2024-03"
    mock_row.total_income = Decimal("15000000")
    mock_row.total_expense = Decimal("500000")

    with patch(
        "app.services.summary.summary_repo.get_monthly_summaries", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [mock_row]

        result = await summary_service.get_summary(mock_db, user_id=1)

    assert len(result) == 1
    assert result[0].month == "2024-03"
    assert result[0].total_income == Decimal("15000000")
    assert result[0].total_expense == Decimal("500000")
    assert result[0].net_balance == Decimal("14500000")


@pytest.mark.asyncio
async def test_get_summary_with_month_filter(mock_db: AsyncMock) -> None:
    mock_row = MagicMock()
    mock_row.month = "2024-03"
    mock_row.total_income = Decimal("5000000")
    mock_row.total_expense = Decimal("2000000")

    with patch(
        "app.services.summary.summary_repo.get_monthly_summaries", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [mock_row]

        result = await summary_service.get_summary(mock_db, user_id=1, month="2024-03")

        mock_get.assert_called_once_with(mock_db, 1, "2024-03")

    assert result[0].net_balance == Decimal("3000000")


@pytest.mark.asyncio
async def test_get_summary_empty_returns_empty_list(mock_db: AsyncMock) -> None:
    with patch(
        "app.services.summary.summary_repo.get_monthly_summaries", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = []

        result = await summary_service.get_summary(mock_db, user_id=1)

    assert result == []


@pytest.mark.asyncio
async def test_get_summary_handles_none_totals(mock_db: AsyncMock) -> None:
    mock_row = MagicMock()
    mock_row.month = "2024-03"
    mock_row.total_income = None
    mock_row.total_expense = None

    with patch(
        "app.services.summary.summary_repo.get_monthly_summaries", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [mock_row]

        result = await summary_service.get_summary(mock_db, user_id=1)

    assert result[0].total_income == Decimal(0)
    assert result[0].total_expense == Decimal(0)
    assert result[0].net_balance == Decimal(0)
