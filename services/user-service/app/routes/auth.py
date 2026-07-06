"""Signup, login and current-user endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.schemas import LoginIn, SignupIn, TokenOut, UserOut
from app.security import (
    current_user_id,
    hash_password,
    issue_token,
    verify_password,
)

router = APIRouter(prefix="/api/users", tags=["auth"])


@router.post("/signup", response_model=TokenOut, status_code=201)
async def signup(body: SignupIn, session: AsyncSession = Depends(get_session)):
    user = User(
        username=body.username,
        display_name=body.display_name,
        password_hash=await hash_password(body.password),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username is already taken")
    return TokenOut(access_token=issue_token(user.id, user.username))


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if user is None or not await verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return TokenOut(access_token=issue_token(user.id, user.username))


@router.get("/me", response_model=UserOut)
async def me(
    user_id: int = Depends(current_user_id),
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
