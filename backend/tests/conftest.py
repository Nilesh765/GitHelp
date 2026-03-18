import pytest
import pytest_asyncio
import asyncio
from datetime import timedelta
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.common.base import Base
from app.core.database import get_db
from app.core.security import create_access_token
from app.modules.user.model import User
from app.common.enums import UserRole

@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        "postgresql+asyncpg://githelp_user:githelp_pass_123@localhost:5433/githelp_db_test",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    TestSessionLocal = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as async_client:
        yield async_client
    app.dependency_overrides.clear()

@pytest.fixture
async def auth_client(
    client: AsyncClient,
    db_session: AsyncSession,
):
    test_user = User(
        email="testuser@githelp.dev",
        hashed_password="hashed_password",
        role=UserRole.user,
        is_active=True,
        full_name="Test User",
    )
    db_session.add(test_user)
    await db_session.commit()

    access_token = create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(days=1)
    )
    client.headers["Authorization"] = f"Bearer {access_token}"
    yield client, test_user
