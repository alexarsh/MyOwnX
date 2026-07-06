"""Shared fixtures: test database schema, table cleanup, ASGI client."""

import os

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://user_service:user_service_pw@postgres:5432/users_test_db",
)
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import delete  # noqa: E402

from app.db import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Follow, User  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
async def schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:  # leave no schema behind
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean_tables(schema):
    yield
    async with SessionLocal() as session:
        await session.execute(delete(Follow))
        await session.execute(delete(User))
        await session.commit()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def signup(client, username="alice", password="password123"):
    response = await client.post(
        "/api/users/signup",
        json={
            "username": username,
            "display_name": username.title(),
            "password": password,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def auth(token):
    return {"authorization": f"Bearer {token}"}
