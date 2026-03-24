from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories import user as user_repo
from app.schemas.user import Token, UserResponse


async def register(db: AsyncSession, email: str, password: str) -> UserResponse:
    try:
        user = await user_repo.create(db, email=email, hashed_password=hash_password(password))
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    return UserResponse.model_validate(user)


async def login(db: AsyncSession, email: str, password: str) -> Token:
    user = await user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return Token(access_token=create_access_token(user.id))
