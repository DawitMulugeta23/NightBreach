"""add onboarding_quiz_completed to users

Revision ID: d4f8a1b3c9e2
Revises: a1c9e3f2b7d4
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa

revision = "d4f8a1b3c9e2"
down_revision = "a1c9e3f2b7d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("onboarding_quiz_completed", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("users", "onboarding_quiz_completed")
