"""Public profiles and the follow/unfollow endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Follow, User
from app.schemas import ProfileOut
from app.security import current_user_id, optional_user_id

router = APIRouter(prefix="/api/users", tags=["profiles"])


async def _get_by_username(session: AsyncSession, username: str) -> User:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{username}", response_model=ProfileOut)
async def profile(
    username: str,
    viewer_id: int | None = Depends(optional_user_id),
    session: AsyncSession = Depends(get_session),
):
    user = await _get_by_username(session, username)
    followers = await session.scalar(
        select(func.count()).where(Follow.followee_id == user.id)
    )
    following = await session.scalar(
        select(func.count()).where(Follow.follower_id == user.id)
    )
    followed_by_me = False
    if viewer_id is not None:
        followed_by_me = (
            await session.get(Follow, (viewer_id, user.id))
        ) is not None
    return ProfileOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        created_at=user.created_at,
        followers=followers,
        following=following,
        followed_by_me=followed_by_me,
    )


@router.post("/{username}/follow", status_code=204)
async def follow(
    username: str,
    viewer_id: int = Depends(current_user_id),
    session: AsyncSession = Depends(get_session),
):
    user = await _get_by_username(session, username)
    if user.id == viewer_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    session.add(Follow(follower_id=viewer_id, followee_id=user.id))
    try:
        await session.commit()
    except IntegrityError:
        pass  # already following — idempotent


@router.delete("/{username}/follow", status_code=204)
async def unfollow(
    username: str,
    viewer_id: int = Depends(current_user_id),
    session: AsyncSession = Depends(get_session),
):
    user = await _get_by_username(session, username)
    await session.execute(
        delete(Follow).where(
            Follow.follower_id == viewer_id, Follow.followee_id == user.id
        )
    )
    await session.commit()
