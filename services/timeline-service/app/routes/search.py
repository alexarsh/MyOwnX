"""Unified search across posts and users."""

from typing import Literal

from fastapi import APIRouter, Depends, Query

from app import clients
from app.security import optional_user_id

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
async def search(
    q: str = Query(min_length=1, max_length=100),
    type: Literal["posts", "users"] = Query(default="posts"),
    limit: int = Query(default=20, le=50),
    viewer_id: int | None = Depends(optional_user_id),
):
    if type == "users":
        return {"users": await clients.search_users(q, limit)}

    page = await clients.search_posts(q, limit, viewer_id)
    author_ids = sorted({item["author_id"] for item in page["items"]})
    authors = await clients.users_by_ids(author_ids)
    return {
        "posts": [
            {**item, "author": authors.get(item["author_id"])}
            for item in page["items"]
        ]
    }
