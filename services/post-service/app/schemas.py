"""Request/response schemas for post-service."""

from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    text: str = Field(min_length=1, max_length=280)
    reply_to_id: int | None = None


class PostOut(BaseModel):
    id: int
    author_id: int
    text: str
    reply_to_id: int | None
    created_at: datetime
    like_count: int
    reply_count: int
    liked_by_me: bool


class ThreadOut(BaseModel):
    post: PostOut
    replies: list[PostOut]


class PageOut(BaseModel):
    items: list[PostOut]
    next_cursor: int | None
