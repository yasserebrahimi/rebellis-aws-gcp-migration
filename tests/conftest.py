"""Shared pytest config & fixtures for async FastAPI tests."""
import os, asyncio, pytest, pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

# Set safe test env defaults
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("DEBUG", "true")

from src.core.database import Base, get_session
from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(os.environ["DATABASE_URL"], echo=False, future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def register_and_login():
    """Helper that registers a user and returns an auth header."""
    async def _inner(ac):
        payload = {"email":"test@example.com","password":"Test1234!","full_name":"Tester"}
        r = await ac.post("/auth/register", json=payload)
        assert r.status_code in (200,201,400)
        r = await ac.post("/auth/login", json={"email":payload["email"],"password":payload["password"]})
        assert r.status_code == 200
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _inner
