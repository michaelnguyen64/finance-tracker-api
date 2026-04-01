from __future__ import annotations

import structlog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories import user as user_repo
from app.schemas.user import Token, UserResponse

logger = structlog.get_logger(__name__)


async def register(db: AsyncSession, email: str, password: str) -> UserResponse:
    try:
        user = await user_repo.create(db, email=email, hashed_password=hash_password(password))
    except IntegrityError:
        await db.rollback()
        raise ConflictException("Email already registered")
    logger.info("user_registered", user_id=user.id)
    return UserResponse.model_validate(user)


async def login(db: AsyncSession, email: str, password: str) -> Token:
    user = await user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Invalid credentials")
    logger.info("user_logged_in", user_id=user.id)
    return Token(access_token=create_access_token(user.id))
