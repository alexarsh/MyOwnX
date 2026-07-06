"""Request/response schemas for user-service."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SignupIn(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-z0-9_]+$")
    display_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=72)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    bio: str
    created_at: datetime


class ProfileOut(UserOut):
    followers: int
    following: int
    followed_by_me: bool
