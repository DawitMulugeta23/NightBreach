"""add first_attempt_correct to user_question_progress

Revision ID: e7a2c4f9b1d3
Revises: d4f8a1b3c9e2
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa

revision = "e7a2c4f9b1d3"
down_revision = "d4f8a1b3c9e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_question_progress",
        sa.Column("first_attempt_correct", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("user_question_progress", "first_attempt_correct")
