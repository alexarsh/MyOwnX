"""HTTP clients for user-service and post-service.

One shared connection-pooled AsyncClient per process — connections are
reused across requests instead of re-established per call.
"""

import httpx
from fastapi import HTTPException

from app.config import settings

client = httpx.AsyncClient(timeout=5.0)


async def _get(url: str, params: dict | None = None) -> httpx.Response:
    try:
        response = await client.get(url, params=params)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Upstream service unavailable")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Not found")
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Upstream service error")
    return response


async def following_ids(user_id: int) -> list[int]:
    url = f"{settings.user_service_url}/internal/users/{user_id}/following-ids"
    return (await _get(url)).json()


async def users_by_ids(ids: list[int]) -> dict[int, dict]:
    if not ids:
        return {}
    url = f"{settings.user_service_url}/internal/users"
    params = {"ids": ",".join(str(i) for i in ids)}
    users = (await _get(url, params)).json()
    return {user["id"]: user for user in users}


async def search_users(q: str, limit: int) -> list[dict]:
    url = f"{settings.user_service_url}/internal/users/search"
    return (await _get(url, {"q": q, "limit": limit})).json()


async def profile(username: str) -> dict:
    url = f"{settings.user_service_url}/api/users/{username}"
    return (await _get(url)).json()


async def posts_by_authors(
    author_ids: list[int], cursor: int | None, limit: int, viewer_id: int | None
) -> dict:
    params: dict = {
        "author_ids": ",".join(str(i) for i in author_ids),
        "limit": limit,
    }
    if cursor is not None:
        params["cursor"] = cursor
    if viewer_id is not None:
        params["viewer_id"] = viewer_id
    url = f"{settings.post_service_url}/internal/posts"
    return (await _get(url, params)).json()


async def search_posts(q: str, limit: int, viewer_id: int | None) -> dict:
    params: dict = {"q": q, "limit": limit}
    if viewer_id is not None:
        params["viewer_id"] = viewer_id
    url = f"{settings.post_service_url}/internal/posts/search"
    return (await _get(url, params)).json()
