from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from structlog.testing import capture_logs

from app.core.tasks import LARGE_TRANSACTION_THRESHOLD, alert_large_transaction

# ---------------------------------------------------------------------------
# alert_large_transaction — unit tests
# ---------------------------------------------------------------------------


def test_alert_logs_warning_with_correct_fields() -> None:
    with capture_logs() as logs:
        alert_large_transaction(transaction_id=42, amount=Decimal("15000"), user_id=7)

    assert len(logs) == 1
    entry = logs[0]
    assert entry["log_level"] == "warning"
    assert entry["event"] == "large_transaction_detected"
    assert entry["transaction_id"] == 42
    assert entry["amount"] == "15000"
    assert entry["user_id"] == 7
    assert entry["threshold"] == str(LARGE_TRANSACTION_THRESHOLD)


def test_alert_does_not_raise() -> None:
    # Smoke test: function completes without exception
    alert_large_transaction(transaction_id=1, amount=Decimal("99999"), user_id=1)


# ---------------------------------------------------------------------------
# Threshold boundary
# ---------------------------------------------------------------------------


def test_threshold_is_correct_usd_value() -> None:
    assert LARGE_TRANSACTION_THRESHOLD == Decimal("10000")


def test_amount_at_threshold_triggers_alert() -> None:
    with capture_logs() as logs:
        alert_large_transaction(transaction_id=1, amount=LARGE_TRANSACTION_THRESHOLD, user_id=1)
    assert len(logs) == 1


# ---------------------------------------------------------------------------
# Router — background task is scheduled only when amount >= threshold
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_transaction_schedules_task_above_threshold(
    mock_db: AsyncMock,
) -> None:
    from unittest.mock import MagicMock

    from app.models.category import Category, CategoryType
    from app.models.transaction import Transaction, TransactionType
    from app.schemas.transaction import TransactionCreate

    sample_category = Category()
    sample_category.id = 1
    sample_category.type = CategoryType.income
    sample_category.user_id = 1

    sample_transaction = Transaction()
    sample_transaction.id = 1
    sample_transaction.amount = Decimal("15000")
    sample_transaction.type = TransactionType.income
    sample_transaction.category_id = 1
    sample_transaction.user_id = 1
    sample_transaction.category = sample_category

    body = TransactionCreate(
        amount=Decimal("15000"),
        type=TransactionType.income,
        date=__import__("datetime").date(2024, 3, 1),
        category_id=1,
    )

    background_tasks = MagicMock()

    with (
        patch(
            "app.routers.transaction.transaction_service.create_transaction",
            new_callable=AsyncMock,
        ) as mock_create,
    ):
        from app.schemas.transaction import TransactionResponse

        mock_create.return_value = TransactionResponse(
            id=1,
            amount=Decimal("15000"),
            type=TransactionType.income,
            note=None,
            date=__import__("datetime").date(2024, 3, 1),
            category_id=1,
            category_name="Salary",
            user_id=1,
        )

        from app.routers.transaction import create_transaction

        await create_transaction(
            body=body,
            background_tasks=background_tasks,
            db=mock_db,
            current_user=MagicMock(id=1),
        )

    background_tasks.add_task.assert_called_once()
    call_kwargs = background_tasks.add_task.call_args
    assert call_kwargs.kwargs["transaction_id"] == 1
    assert call_kwargs.kwargs["amount"] == Decimal("15000")


@pytest.mark.asyncio
async def test_create_transaction_skips_task_below_threshold(
    mock_db: AsyncMock,
) -> None:
    from unittest.mock import MagicMock

    from app.models.transaction import TransactionType
    from app.schemas.transaction import TransactionCreate, TransactionResponse

    body = TransactionCreate(
        amount=Decimal("50"),
        type=TransactionType.income,
        date=__import__("datetime").date(2024, 3, 1),
        category_id=1,
    )

    background_tasks = MagicMock()

    with patch(
        "app.routers.transaction.transaction_service.create_transaction",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.return_value = TransactionResponse(
            id=2,
            amount=Decimal("50"),
            type=TransactionType.income,
            note=None,
            date=__import__("datetime").date(2024, 3, 1),
            category_id=1,
            category_name="Salary",
            user_id=1,
        )

        from app.routers.transaction import create_transaction

        await create_transaction(
            body=body,
            background_tasks=background_tasks,
            db=mock_db,
            current_user=MagicMock(id=1),
        )

    background_tasks.add_task.assert_not_called()
