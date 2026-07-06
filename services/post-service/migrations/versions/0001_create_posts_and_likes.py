"""create posts and likes tables

Revision ID: 0001
Revises: None
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("text", sa.String(280), nullable=False),
        sa.Column(
            "reply_to_id",
            sa.BigInteger(),
            sa.ForeignKey("posts.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "search_vector",
            TSVECTOR(),
            sa.Computed("to_tsvector('english', text)", persisted=True),
        ),
    )
    # profile pages & timeline fan-in: newest posts per author (keyset on id)
    op.create_index("ix_posts_author_id_id", "posts", ["author_id", "id"])
    # thread lookups and reply counts
    op.create_index("ix_posts_reply_to_id", "posts", ["reply_to_id"])
    # full-text search
    op.create_index(
        "ix_posts_search_vector", "posts", ["search_vector"], postgresql_using="gin"
    )

    op.create_table(
        "likes",
        sa.Column("user_id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "post_id",
            sa.BigInteger(),
            sa.ForeignKey("posts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    # like counts are aggregated by post
    op.create_index("ix_likes_post_id", "likes", ["post_id"])


def downgrade() -> None:
    op.drop_index("ix_likes_post_id", table_name="likes")
    op.drop_table("likes")
    op.drop_index("ix_posts_search_vector", table_name="posts")
    op.drop_index("ix_posts_reply_to_id", table_name="posts")
    op.drop_index("ix_posts_author_id_id", table_name="posts")
    op.drop_table("posts")
