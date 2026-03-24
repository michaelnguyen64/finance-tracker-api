from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import Token, UserRegister, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)) -> UserResponse:
    return await auth_service.register(db, email=body.email, password=body.password)


@router.post("/login", response_model=Token)
async def login(body: UserRegister, db: AsyncSession = Depends(get_db)) -> Token:
    return await auth_service.login(db, email=body.email, password=body.password)
