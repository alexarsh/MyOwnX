"""Home and profile timelines: compose follow graph + posts + authors.

Exactly three upstream calls per home-timeline page, whatever the page
size (following-ids -> batch posts -> batch author hydration).
"""

from fastapi import APIRouter, Depends, Query

from app import clients
from app.security import current_user_id, optional_user_id

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


async def _with_authors(page: dict) -> dict:
    author_ids = sorted({item["author_id"] for item in page["items"]})
    authors = await clients.users_by_ids(author_ids)
    return {
        "items": [
            {**item, "author": authors.get(item["author_id"])}
            for item in page["items"]
        ],
        "next_cursor": page["next_cursor"],
    }


@router.get("")
async def home_timeline(
    cursor: int | None = Query(default=None),
    limit: int = Query(default=20, le=50),
    user_id: int = Depends(current_user_id),
):
    author_ids = await clients.following_ids(user_id)
    author_ids.append(user_id)  # own posts belong in the home feed
    page = await clients.posts_by_authors(author_ids, cursor, limit, user_id)
    return await _with_authors(page)


@router.get("/thread/{post_id}")
async def thread(
    post_id: int,
    viewer_id: int | None = Depends(optional_user_id),
):
    data = await clients.thread(post_id, viewer_id)
    posts = [data["post"], *data["replies"]]
    authors = await clients.users_by_ids(sorted({p["author_id"] for p in posts}))
    data["post"] = {**data["post"], "author": authors.get(data["post"]["author_id"])}
    data["replies"] = [
        {**reply, "author": authors.get(reply["author_id"])}
        for reply in data["replies"]
    ]
    return data


@router.get("/user/{username}")
async def user_timeline(
    username: str,
    cursor: int | None = Query(default=None),
    limit: int = Query(default=20, le=50),
    viewer_id: int | None = Depends(optional_user_id),
):
    author = await clients.profile(username)
    page = await clients.posts_by_authors([author["id"]], cursor, limit, viewer_id)
    return {
        "items": [{**item, "author": author} for item in page["items"]],
        "next_cursor": page["next_cursor"],
    }
