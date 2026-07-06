"""Signup, login and token-protected endpoints."""

from tests.conftest import auth, signup


async def test_signup_returns_token(client):
    token = await signup(client, "alice")
    assert token


async def test_signup_duplicate_username_conflicts(client):
    await signup(client, "alice")
    response = await client.post(
        "/api/users/signup",
        json={"username": "alice", "display_name": "A", "password": "password123"},
    )
    assert response.status_code == 409


async def test_signup_rejects_bad_username_and_short_password(client):
    bad_username = await client.post(
        "/api/users/signup",
        json={"username": "Not Valid!", "display_name": "A", "password": "password123"},
    )
    short_password = await client.post(
        "/api/users/signup",
        json={"username": "bob", "display_name": "B", "password": "short"},
    )
    assert bad_username.status_code == 422
    assert short_password.status_code == 422


async def test_login_roundtrip(client):
    await signup(client, "alice", password="password123")
    ok = await client.post(
        "/api/users/login",
        json={"username": "alice", "password": "password123"},
    )
    wrong = await client.post(
        "/api/users/login",
        json={"username": "alice", "password": "wrong-password"},
    )
    unknown = await client.post(
        "/api/users/login",
        json={"username": "nobody", "password": "password123"},
    )
    assert ok.status_code == 200 and ok.json()["access_token"]
    assert wrong.status_code == 401
    assert unknown.status_code == 401


async def test_me_requires_valid_token(client):
    token = await signup(client, "alice")
    ok = await client.get("/api/users/me", headers=auth(token))
    anonymous = await client.get("/api/users/me")
    garbage = await client.get(
        "/api/users/me", headers={"authorization": "Bearer not-a-token"}
    )
    assert ok.status_code == 200
    assert ok.json()["username"] == "alice"
    assert "password_hash" not in ok.json()
    assert anonymous.status_code == 401
    assert garbage.status_code == 401
