"""Timeline composition and search aggregation over faked upstreams."""

from app import clients

from tests.conftest import auth, make_post, make_user


async def test_home_timeline_requires_auth(client):
    response = await client.get("/api/timeline")
    assert response.status_code == 401


async def test_home_timeline_includes_self_and_hydrates_authors(
    client, monkeypatch
):
    calls = {}

    async def fake_following_ids(user_id):
        calls["following_of"] = user_id
        return [2]

    async def fake_posts_by_authors(author_ids, cursor, limit, viewer_id):
        calls["author_ids"] = author_ids
        return {
            "items": [make_post(10, 2, "from bob"), make_post(9, 1, "own post")],
            "next_cursor": 9,
        }

    async def fake_users_by_ids(ids):
        calls["hydrated_ids"] = ids
        return {1: make_user(1, "alice"), 2: make_user(2, "bob")}

    monkeypatch.setattr(clients, "following_ids", fake_following_ids)
    monkeypatch.setattr(clients, "posts_by_authors", fake_posts_by_authors)
    monkeypatch.setattr(clients, "users_by_ids", fake_users_by_ids)

    response = await client.get("/api/timeline", headers=auth(1))
    body = response.json()

    assert response.status_code == 200
    assert calls["following_of"] == 1
    assert calls["author_ids"] == [2, 1]  # followees plus myself
    assert calls["hydrated_ids"] == [1, 2]  # deduplicated batch, no N+1
    assert [item["author"]["username"] for item in body["items"]] == ["bob", "alice"]
    assert body["next_cursor"] == 9


async def test_thread_hydrates_authors(client, monkeypatch):
    async def fake_thread(post_id, viewer_id):
        return {"post": make_post(1, 5, "root"), "replies": [make_post(2, 6, "re")]}

    async def fake_users_by_ids(ids):
        return {5: make_user(5, "eve"), 6: make_user(6, "frank")}

    monkeypatch.setattr(clients, "thread", fake_thread)
    monkeypatch.setattr(clients, "users_by_ids", fake_users_by_ids)

    body = (await client.get("/api/timeline/thread/1")).json()
    assert body["post"]["author"]["username"] == "eve"
    assert body["replies"][0]["author"]["username"] == "frank"


async def test_search_posts_attaches_authors(client, monkeypatch):
    async def fake_search_posts(q, limit, viewer_id):
        return {"items": [make_post(5, 7, f"about {q}")], "next_cursor": None}

    async def fake_users_by_ids(ids):
        return {7: make_user(7, "carol")}

    monkeypatch.setattr(clients, "search_posts", fake_search_posts)
    monkeypatch.setattr(clients, "users_by_ids", fake_users_by_ids)

    body = (await client.get("/api/search?q=rust&type=posts")).json()
    assert body["posts"][0]["author"]["username"] == "carol"


async def test_search_users_passthrough(client, monkeypatch):
    async def fake_search_users(q, limit):
        return [make_user(3, "dave")]

    monkeypatch.setattr(clients, "search_users", fake_search_users)

    body = (await client.get("/api/search?q=dav&type=users")).json()
    assert [user["username"] for user in body["users"]] == ["dave"]


async def test_search_requires_query(client):
    response = await client.get("/api/search")
    assert response.status_code == 422
