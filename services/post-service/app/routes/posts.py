"""Create, read (thread view) and delete posts."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.enrich import hydrate
from app.models import Post
from app.schemas import PostCreate, PostOut, ThreadOut
from app.security import current_user_id, optional_user_id

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("", response_model=PostOut, status_code=201)
async def create_post(
    body: PostCreate,
    user_id: int = Depends(current_user_id),
    session: AsyncSession = Depends(get_session),
):
    if body.reply_to_id is not None:
        parent = await session.get(Post, body.reply_to_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent post not found")
        if parent.reply_to_id is not None:
            raise HTTPException(
                status_code=400, detail="Replies to replies are not supported"
            )
    post = Post(author_id=user_id, text=body.text, reply_to_id=body.reply_to_id)
    session.add(post)
    await session.commit()
    return (await hydrate(session, [post], user_id))[0]


@router.get("/{post_id}", response_model=ThreadOut)
async def thread(
    post_id: int,
    viewer_id: int | None = Depends(optional_user_id),
    session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    replies_result = await session.execute(
        select(Post).where(Post.reply_to_id == post_id).order_by(Post.id)
    )
    replies = list(replies_result.scalars())
    hydrated = await hydrate(session, [post, *replies], viewer_id)
    return ThreadOut(post=hydrated[0], replies=hydrated[1:])


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user_id: int = Depends(current_user_id),
    session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != user_id:
        raise HTTPException(status_code=403, detail="Not your post")
    await session.delete(post)
    await session.commit()
