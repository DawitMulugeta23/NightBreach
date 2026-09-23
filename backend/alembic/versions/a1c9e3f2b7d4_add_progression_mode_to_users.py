"""add progression_mode to users

Revision ID: a1c9e3f2b7d4
Revises: 3b47d64de6e8
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa

revision = "a1c9e3f2b7d4"
down_revision = "3b47d64de6e8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("progression_mode", sa.String(), nullable=False, server_default="strict"),
    )


def downgrade() -> None:
    op.drop_column("users", "progression_mode")
