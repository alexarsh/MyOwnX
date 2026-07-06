"""create users and follows tables

Revision ID: 0001
Revises: None
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("username", sa.String(30), nullable=False),
        sa.Column("display_name", sa.String(50), nullable=False),
        sa.Column("bio", sa.String(160), nullable=False, server_default=""),
        sa.Column("password_hash", sa.String(72), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "follows",
        sa.Column(
            "follower_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "followee_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    # (follower_id, followee_id) PK already serves "who do I follow";
    # this index serves the reverse direction (follower counts).
    op.create_index("ix_follows_followee_id", "follows", ["followee_id"])


def downgrade() -> None:
    op.drop_index("ix_follows_followee_id", table_name="follows")
    op.drop_table("follows")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
