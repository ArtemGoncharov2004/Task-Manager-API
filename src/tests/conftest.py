import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import *  # noqa: F401,F403
from app.schemas.user import UserCreate
from app.services.auth_service import register_user

test_engine = create_async_engine(settings.test_database_url)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        # очистка после каждого теста — чистые таблицы для следующего
        await session.execute(
            text(
                "TRUNCATE TABLE task_tags, tasks, tags, projects, users RESTART IDENTITY CASCADE"
            )
        )
        await session.commit()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    data = UserCreate(email="user1@test.com", password="testpass123")
    user = await register_user(db_session, data)
    return user, "testpass123"


@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    user, password = test_user
    response = await client.post(
        "/auth/login",
        data={"username": user.email, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_project(client, auth_headers):
    response = await client.post(
        "/projects", json={"name": "Test Project"}, headers=auth_headers
    )
    return response.json()
