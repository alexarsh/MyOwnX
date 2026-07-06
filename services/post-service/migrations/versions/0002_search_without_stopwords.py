"""index post search with the simple config (no stopwords)

Short posts are often made of common words ("All good", "Same") which the
english config drops as stopwords, making whole posts unsearchable. The
simple config indexes every word verbatim.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def _swap_search_vector(config: str) -> None:
    op.drop_index("ix_posts_search_vector", table_name="posts")
    op.drop_column("posts", "search_vector")
    op.add_column(
        "posts",
        sa.Column(
            "search_vector",
            TSVECTOR(),
            sa.Computed(f"to_tsvector('{config}', text)", persisted=True),
        ),
    )
    op.create_index(
        "ix_posts_search_vector", "posts", ["search_vector"], postgresql_using="gin"
    )


def upgrade() -> None:
    _swap_search_vector("simple")


def downgrade() -> None:
    _swap_search_vector("english")
