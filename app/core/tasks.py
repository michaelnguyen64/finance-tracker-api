from __future__ import annotations

from decimal import Decimal

import structlog

logger = structlog.get_logger(__name__)

LARGE_TRANSACTION_THRESHOLD = Decimal("10000")


def alert_large_transaction(transaction_id: int, amount: Decimal, user_id: int) -> None:
    logger.warning(
        "large_transaction_detected",
        transaction_id=transaction_id,
        amount=str(amount),
        user_id=user_id,
        threshold=str(LARGE_TRANSACTION_THRESHOLD),
    )
