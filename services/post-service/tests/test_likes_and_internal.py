"""Likes, cursor pagination and full-text search."""

from tests.conftest import auth, create_post


async def test_like_unlike_is_idempotent(client):
    post = await create_post(client, user_id=1)

    for _ in range(2):  # double-like must not double-count
        response = await client.post(f"/api/posts/{post['id']}/like", headers=auth(2))
        assert response.status_code == 204

    liked = (await client.get(f"/api/posts/{post['id']}", headers=auth(2))).json()
    assert liked["post"]["like_count"] == 1
    assert liked["post"]["liked_by_me"] is True

    await client.delete(f"/api/posts/{post['id']}/like", headers=auth(2))
    unliked = (await client.get(f"/api/posts/{post['id']}", headers=auth(2))).json()
    assert unliked["post"]["like_count"] == 0
    assert unliked["post"]["liked_by_me"] is False


async def test_like_missing_post_is_404(client):
    response = await client.post("/api/posts/99999/like", headers=auth(1))
    assert response.status_code == 404


async def test_internal_posts_cursor_pagination(client):
    for n in range(5):
        await create_post(client, user_id=1, text=f"post {n}")
    await create_post(client, user_id=2, text="someone else")

    first = (await client.get("/internal/posts?author_ids=1&limit=2")).json()
    assert [p["text"] for p in first["items"]] == ["post 4", "post 3"]
    assert first["next_cursor"] is not None

    second = (
        await client.get(f"/internal/posts?author_ids=1&limit=2&cursor={first['next_cursor']}")
    ).json()
    assert [p["text"] for p in second["items"]] == ["post 2", "post 1"]

    first_ids = {p["id"] for p in first["items"]}
    assert first_ids.isdisjoint({p["id"] for p in second["items"]})


async def test_internal_posts_excludes_replies_and_other_authors(client):
    root = await create_post(client, user_id=1, text="root")
    await create_post(client, user_id=1, text="a reply", reply_to_id=root["id"])
    await create_post(client, user_id=2, text="other author")

    page = (await client.get("/internal/posts?author_ids=1")).json()
    assert [p["id"] for p in page["items"]] == [root["id"]]


async def test_internal_thread_endpoint(client):
    root = await create_post(client, 1, "root post")
    await create_post(client, 2, "a reply", reply_to_id=root["id"])

    body = (
        await client.get(f"/internal/posts/{root['id']}/thread?viewer_id=2")
    ).json()
    missing = await client.get("/internal/posts/99999/thread")
    assert body["post"]["id"] == root["id"]
    assert [r["text"] for r in body["replies"]] == ["a reply"]
    assert missing.status_code == 404


async def test_internal_search_matches_words(client):
    await create_post(client, 1, "Rockets are launching tonight")
    await create_post(client, 1, "All good")

    hit = (await client.get("/internal/posts/search?q=rockets")).json()
    stopwords = (await client.get("/internal/posts/search?q=all%20good")).json()
    common_word = (await client.get("/internal/posts/search?q=Same")).json()
    miss = (await client.get("/internal/posts/search?q=quantum")).json()
    assert [p["text"] for p in hit["items"]] == ["Rockets are launching tonight"]
    # 'simple' config: posts made entirely of english stopwords still match
    assert [p["text"] for p in stopwords["items"]] == ["All good"]
    assert common_word["items"] == []
    assert miss["items"] == []
