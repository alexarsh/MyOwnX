"""Fixtures: env, ASGI client and fake upstream clients (no network)."""

import os
import time

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("USER_SERVICE_URL", "http://user-service.test")
os.environ.setdefault("POST_SERVICE_URL", "http://post-service.test")

import jwt  # noqa: E402
import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


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


def make_post(post_id, author_id, text="hello"):
    return {
        "id": post_id,
        "author_id": author_id,
        "text": text,
        "reply_to_id": None,
        "created_at": "2026-01-01T00:00:00Z",
        "like_count": 0,
        "reply_count": 0,
        "liked_by_me": False,
    }


def make_user(user_id, username):
    return {
        "id": user_id,
        "username": username,
        "display_name": username.title(),
        "bio": "",
        "created_at": "2026-01-01T00:00:00Z",
    }
