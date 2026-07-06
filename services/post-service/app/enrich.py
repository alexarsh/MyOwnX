"""Batch hydration of posts with like/reply counts and viewer state.

Always three grouped queries per page regardless of page size — never
one query per post (no N+1).
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Like, Post
from app.schemas import PostOut, ThreadOut


async def hydrate(
    session: AsyncSession, posts: list[Post], viewer_id: int | None
) -> list[PostOut]:
    if not posts:
        return []
    ids = [post.id for post in posts]

    like_rows = await session.execute(
        select(Like.post_id, func.count())
        .where(Like.post_id.in_(ids))
        .group_by(Like.post_id)
    )
    like_counts = dict(like_rows.all())

    reply_rows = await session.execute(
        select(Post.reply_to_id, func.count())
        .where(Post.reply_to_id.in_(ids))
        .group_by(Post.reply_to_id)
    )
    reply_counts = dict(reply_rows.all())

    liked: set[int] = set()
    if viewer_id is not None:
        liked_rows = await session.execute(
            select(Like.post_id).where(
                Like.user_id == viewer_id, Like.post_id.in_(ids)
            )
        )
        liked = set(liked_rows.scalars())

    return [
        PostOut(
            id=post.id,
            author_id=post.author_id,
            text=post.text,
            reply_to_id=post.reply_to_id,
            created_at=post.created_at,
            like_count=like_counts.get(post.id, 0),
            reply_count=reply_counts.get(post.id, 0),
            liked_by_me=post.id in liked,
        )
        for post in posts
    ]


async def load_thread(
    session: AsyncSession, post_id: int, viewer_id: int | None
) -> ThreadOut | None:
    post = await session.get(Post, post_id)
    if post is None:
        return None
    replies_result = await session.execute(
        select(Post).where(Post.reply_to_id == post_id).order_by(Post.id)
    )
    replies = list(replies_result.scalars())
    hydrated = await hydrate(session, [post, *replies], viewer_id)
    return ThreadOut(post=hydrated[0], replies=hydrated[1:])
