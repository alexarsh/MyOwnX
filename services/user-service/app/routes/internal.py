"""Internal service-to-service endpoints (not exposed via the gateway)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Follow, User
from app.schemas import UserOut

router = APIRouter(prefix="/internal/users", tags=["internal"])


def _parse_ids(raw: str) -> list[int]:
    return [int(part) for part in raw.split(",") if part][:100]


@router.get("", response_model=list[UserOut])
async def users_by_ids(
    ids: str = Query(default=""),
    session: AsyncSession = Depends(get_session),
):
    id_list = _parse_ids(ids)
    if not id_list:
        return []
    result = await session.execute(select(User).where(User.id.in_(id_list)))
    return list(result.scalars())


@router.get("/search", response_model=list[UserOut])
async def search_users(
    q: str = Query(min_length=1, max_length=50),
    limit: int = Query(default=20, le=50),
    session: AsyncSession = Depends(get_session),
):
    pattern = f"%{q.lower()}%"
    result = await session.execute(
        select(User)
        .where(
            or_(
                User.username.ilike(pattern),
                User.display_name.ilike(pattern),
            )
        )
        .order_by(User.id)
        .limit(limit)
    )
    return list(result.scalars())


@router.get("/{user_id}/following-ids", response_model=list[int])
async def following_ids(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Follow.followee_id).where(Follow.follower_id == user_id)
    )
    return list(result.scalars())
