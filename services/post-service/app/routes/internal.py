"""Internal endpoints consumed by timeline-service."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.enrich import hydrate, load_thread
from app.models import Post
from app.schemas import PageOut, ThreadOut

router = APIRouter(prefix="/internal/posts", tags=["internal"])


@router.get("", response_model=PageOut)
async def posts_by_authors(
    author_ids: str = Query(default=""),
    cursor: int | None = Query(default=None),
    limit: int = Query(default=20, le=50),
    viewer_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    ids = [int(part) for part in author_ids.split(",") if part][:500]
    if not ids:
        return PageOut(items=[], next_cursor=None)

    query = select(Post).where(Post.author_id.in_(ids), Post.reply_to_id.is_(None))
    if cursor is not None:
        query = query.where(Post.id < cursor)  # keyset pagination
    query = query.order_by(Post.id.desc()).limit(limit)
    posts = list((await session.execute(query)).scalars())

    next_cursor = posts[-1].id if len(posts) == limit else None
    return PageOut(
        items=await hydrate(session, posts, viewer_id), next_cursor=next_cursor
    )


@router.get("/search", response_model=PageOut)
async def search_posts(
    q: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=20, le=50),
    viewer_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    query = (
        select(Post)
        .where(Post.search_vector.op("@@")(func.plainto_tsquery("simple", q)))
        .order_by(Post.id.desc())
        .limit(limit)
    )
    posts = list((await session.execute(query)).scalars())
    return PageOut(items=await hydrate(session, posts, viewer_id), next_cursor=None)


@router.get("/{post_id}/thread", response_model=ThreadOut)
async def thread(
    post_id: int,
    viewer_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    result = await load_thread(session, post_id, viewer_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return result
