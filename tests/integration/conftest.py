from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.database import get_db
from app.main import app  # import triggers model registration
from app.models.base import Base

load_dotenv()  # loads .env so TEST_DATABASE_URL is available via os.getenv

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/finance_tracker_test",
)


@pytest.fixture(scope="session", autouse=True)
def _schema() -> Generator[None, None, None]:
    async def _create_all() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    async def _drop_all() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    asyncio.run(_create_all())
    yield
    asyncio.run(_drop_all())


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    test_engine = create_async_engine(TEST_DATABASE_URL)

    # Delete rows in reverse FK order so constraints are not violated.
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSession(test_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await test_engine.dispose()
