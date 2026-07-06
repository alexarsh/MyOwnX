"""Like / unlike endpoints (idempotent)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Like, Post
from app.security import current_user_id

router = APIRouter(prefix="/api/posts", tags=["likes"])


@router.post("/{post_id}/like", status_code=204)
async def like(
    post_id: int,
    user_id: int = Depends(current_user_id),
    session: AsyncSession = Depends(get_session),
):
    if await session.get(Post, post_id) is None:
        raise HTTPException(status_code=404, detail="Post not found")
    session.add(Like(user_id=user_id, post_id=post_id))
    try:
        await session.commit()
    except IntegrityError:
        pass  # already liked — idempotent


@router.delete("/{post_id}/like", status_code=204)
async def unlike(
    post_id: int,
    user_id: int = Depends(current_user_id),
    session: AsyncSession = Depends(get_session),
):
    await session.execute(
        delete(Like).where(Like.user_id == user_id, Like.post_id == post_id)
    )
    await session.commit()
