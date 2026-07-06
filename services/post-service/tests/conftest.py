"""Shared fixtures: test database schema, table cleanup, ASGI client."""

import os
import time

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://post_service:post_service_pw@postgres:5432/posts_test_db",
)
os.environ.setdefault("JWT_SECRET", "test-secret")

import jwt  # noqa: E402
import pytest  # noqa: E402
from app.db import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Like, Post  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import delete  # noqa: E402


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
        await session.execute(delete(Like))
        await session.execute(delete(Post))
        await session.commit()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def auth(user_id):
    token = jwt.encode(
        {"sub": str(user_id), "exp": int(time.time()) + 600},
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )
    return {"authorization": f"Bearer {token}"}


async def create_post(client, user_id, text="hello world", reply_to_id=None):
    response = await client.post(
        "/api/posts",
        json={"text": text, "reply_to_id": reply_to_id},
        headers=auth(user_id),
    )
    assert response.status_code == 201, response.text
    return response.json()
