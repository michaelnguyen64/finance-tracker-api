from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.transaction import TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.schemas.user import UserRegister


def test_transaction_create_rejects_negative_amount() -> None:
    with pytest.raises(ValidationError) as exc:
        TransactionCreate(
            amount=Decimal("-100"),
            type=TransactionType.income,
            date=date(2024, 3, 1),
            category_id=1,
        )
    assert "Amount must be positive" in str(exc.value)


def test_transaction_create_rejects_zero_amount() -> None:
    with pytest.raises(ValidationError) as exc:
        TransactionCreate(
            amount=Decimal("0"),
            type=TransactionType.income,
            date=date(2024, 3, 1),
            category_id=1,
        )
    assert "Amount must be positive" in str(exc.value)


def test_transaction_create_rejects_invalid_date_string() -> None:
    with pytest.raises(ValidationError):
        TransactionCreate(
            amount=Decimal("500"),
            type=TransactionType.income,
            date="not-a-date",  # type: ignore[arg-type]
            category_id=1,
        )


def test_transaction_create_rejects_missing_fields() -> None:
    with pytest.raises(ValidationError):
        TransactionCreate(amount=Decimal("500"))  # type: ignore[call-arg]


def test_transaction_create_valid_passes() -> None:
    tx = TransactionCreate(
        amount=Decimal("500000"),
        type=TransactionType.income,
        date=date(2024, 3, 1),
        category_id=1,
    )
    assert tx.amount == Decimal("500000")


def test_transaction_update_rejects_negative_amount() -> None:
    with pytest.raises(ValidationError) as exc:
        TransactionUpdate(amount=Decimal("-1"))
    assert "Amount must be positive" in str(exc.value)


def test_transaction_update_allows_all_none() -> None:
    update = TransactionUpdate()
    assert update.amount is None
    assert update.type is None


def test_user_register_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        UserRegister(email="test@example.com", password="short")


def test_user_register_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        UserRegister(email="not-an-email", password="password123")


def test_user_register_valid_passes() -> None:
    user = UserRegister(email="test@example.com", password="password123")
    assert user.email == "test@example.com"
