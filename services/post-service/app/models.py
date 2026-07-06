"""ORM models owned by post-service: posts and likes."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        # profile pages & timeline fan-in: newest posts per author
        Index("ix_posts_author_id_id", "author_id", "id"),
        # thread lookups
        Index("ix_posts_reply_to_id", "reply_to_id"),
        # full-text search
        Index("ix_posts_search_vector", "search_vector", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    author_id: Mapped[int] = mapped_column(BigInteger)  # cross-service ref, no FK
    text: Mapped[str] = mapped_column(String(280))
    reply_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    search_vector: Mapped[str] = mapped_column(
        TSVECTOR, Computed("to_tsvector('english', text)", persisted=True)
    )


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (
        # like counts are aggregated by post
        Index("ix_likes_post_id", "post_id"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
