"""Profiles, follow graph and internal endpoints."""

from tests.conftest import auth, signup


async def test_profile_counts_and_404(client):
    await signup(client, "alice")
    profile = await client.get("/api/users/alice")
    missing = await client.get("/api/users/nobody")
    body = profile.json()
    assert profile.status_code == 200
    assert (body["followers"], body["following"], body["followed_by_me"]) == (0, 0, False)
    assert missing.status_code == 404


async def test_follow_unfollow_flow(client):
    await signup(client, "alice")
    bob = await signup(client, "bob")

    first = await client.post("/api/users/alice/follow", headers=auth(bob))
    again = await client.post("/api/users/alice/follow", headers=auth(bob))
    assert first.status_code == 204
    assert again.status_code == 204  # idempotent

    seen_by_bob = (await client.get("/api/users/alice", headers=auth(bob))).json()
    assert seen_by_bob["followers"] == 1
    assert seen_by_bob["followed_by_me"] is True

    bob_profile = (await client.get("/api/users/bob", headers=auth(bob))).json()
    assert bob_profile["following"] == 1

    unfollow = await client.delete("/api/users/alice/follow", headers=auth(bob))
    assert unfollow.status_code == 204
    after = (await client.get("/api/users/alice", headers=auth(bob))).json()
    assert after["followers"] == 0


async def test_cannot_follow_yourself_or_anonymously(client):
    alice = await signup(client, "alice")
    self_follow = await client.post("/api/users/alice/follow", headers=auth(alice))
    anonymous = await client.post("/api/users/alice/follow")
    assert self_follow.status_code == 400
    assert anonymous.status_code == 401


async def test_internal_batch_and_following_ids(client):
    alice = await signup(client, "alice")
    bob = await signup(client, "bob")
    alice_id = (await client.get("/api/users/me", headers=auth(alice))).json()["id"]
    bob_id = (await client.get("/api/users/me", headers=auth(bob))).json()["id"]

    await client.post("/api/users/bob/follow", headers=auth(alice))

    batch = await client.get(f"/internal/users?ids={alice_id},{bob_id}")
    following = await client.get(f"/internal/users/{alice_id}/following-ids")
    assert {user["username"] for user in batch.json()} == {"alice", "bob"}
    assert following.json() == [bob_id]


async def test_internal_user_search_is_case_insensitive(client):
    await signup(client, "alice")
    await signup(client, "bob")
    hits = await client.get("/internal/users/search?q=ALI")
    assert [user["username"] for user in hits.json()] == ["alice"]
