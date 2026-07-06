"""Posts, replies, threads and deletion rules."""

from tests.conftest import auth, create_post


async def test_create_post(client):
    post = await create_post(client, user_id=1, text="first!")
    assert post["text"] == "first!"
    assert post["author_id"] == 1
    state = (post["like_count"], post["reply_count"], post["liked_by_me"])
    assert state == (0, 0, False)


async def test_create_requires_auth_and_valid_text(client):
    anonymous = await client.post("/api/posts", json={"text": "hi"})
    empty = await client.post("/api/posts", json={"text": ""}, headers=auth(1))
    too_long = await client.post(
        "/api/posts", json={"text": "x" * 281}, headers=auth(1)
    )
    assert anonymous.status_code == 401
    assert empty.status_code == 422
    assert too_long.status_code == 422


async def test_reply_and_thread_view(client):
    root = await create_post(client, 1, "root post")
    reply = await create_post(client, 2, "a reply", reply_to_id=root["id"])

    thread = (await client.get(f"/api/posts/{root['id']}")).json()
    assert thread["post"]["reply_count"] == 1
    assert [r["id"] for r in thread["replies"]] == [reply["id"]]


async def test_reply_validation(client):
    root = await create_post(client, 1, "root")
    reply = await create_post(client, 2, "reply", reply_to_id=root["id"])

    to_missing = await client.post(
        "/api/posts", json={"text": "hi", "reply_to_id": 99999}, headers=auth(1)
    )
    to_reply = await client.post(
        "/api/posts",
        json={"text": "nested", "reply_to_id": reply["id"]},
        headers=auth(1),
    )
    assert to_missing.status_code == 404
    assert to_reply.status_code == 400  # single-level threads only


async def test_delete_only_own_posts(client):
    post = await create_post(client, user_id=1)

    forbidden = await client.delete(f"/api/posts/{post['id']}", headers=auth(2))
    assert forbidden.status_code == 403

    deleted = await client.delete(f"/api/posts/{post['id']}", headers=auth(1))
    assert deleted.status_code == 204
    assert (await client.get(f"/api/posts/{post['id']}")).status_code == 404
