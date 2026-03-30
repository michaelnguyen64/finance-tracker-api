from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.models.category import Category, CategoryType
from app.models.transaction import Transaction, TransactionType
from app.models.user import User


@pytest.fixture
def mock_db() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_user() -> User:
    user = User()
    user.id = 1
    user.email = "test@example.com"
    user.hashed_password = "hashed"
    return user


@pytest.fixture
def sample_category() -> Category:
    category = Category()
    category.id = 1
    category.name = "Salary"
    category.type = CategoryType.income
    category.user_id = 1
    return category


@pytest.fixture
def sample_transaction(sample_category: Category) -> Transaction:
    transaction = Transaction()
    transaction.id = 1
    transaction.amount = Decimal("1000000")
    transaction.type = TransactionType.income
    transaction.note = "Monthly salary"
    transaction.date = date(2024, 3, 1)
    transaction.category_id = 1
    transaction.user_id = 1
    transaction.category = sample_category
    return transaction
