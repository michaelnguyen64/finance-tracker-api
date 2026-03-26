from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.services import auth as auth_service


@pytest.mark.asyncio
async def test_register_success(mock_db: AsyncMock) -> None:
    mock_user = AsyncMock()
    mock_user.id = 1
    mock_user.email = "new@example.com"

    with (
        patch("app.services.auth.user_repo.get_by_email", new_callable=AsyncMock) as mock_get,
        patch("app.services.auth.user_repo.create", new_callable=AsyncMock) as mock_create,
    ):
        mock_get.return_value = None
        mock_create.return_value = mock_user

        result = await auth_service.register(mock_db, "new@example.com", "password123")

    assert result.email == "new@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email_raises_400(mock_db: AsyncMock) -> None:
    from sqlalchemy.exc import IntegrityError

    with patch("app.services.auth.user_repo.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = IntegrityError(None, None, Exception())

        with pytest.raises(HTTPException) as exc:
            await auth_service.register(mock_db, "dupe@example.com", "password123")

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_login_success(mock_db: AsyncMock) -> None:
    from app.core.security import hash_password

    mock_user = AsyncMock()
    mock_user.id = 1
    mock_user.hashed_password = hash_password("password123")

    with patch("app.services.auth.user_repo.get_by_email", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_user

        result = await auth_service.login(mock_db, "test@example.com", "password123")

    assert result.access_token
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_raises_401(mock_db: AsyncMock) -> None:
    from app.core.security import hash_password

    mock_user = AsyncMock()
    mock_user.hashed_password = hash_password("correct_password")

    with patch("app.services.auth.user_repo.get_by_email", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_user

        with pytest.raises(HTTPException) as exc:
            await auth_service.login(mock_db, "test@example.com", "wrong_password")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email_raises_401(mock_db: AsyncMock) -> None:
    with patch("app.services.auth.user_repo.get_by_email", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        with pytest.raises(HTTPException) as exc:
            await auth_service.login(mock_db, "nobody@example.com", "password123")

    assert exc.value.status_code == 401
