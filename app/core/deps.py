from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories import user as user_repo

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedException("Not authenticated")

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise UnauthorizedException("Invalid token")

    user = await user_repo.get_by_id(db, user_id)
    if user is None:
        raise UnauthorizedException("User not found")

    return user
