"""add progress timestamp defaults

Revision ID: 9c7d5e2a1b34
Revises: 8b6e2f4c1a90
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c7d5e2a1b34"
down_revision: Union[str, Sequence[str], None] = "8b6e2f4c1a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PROGRESS_TABLES = (
    "learner_learning_path_progress",
    "learner_module_progress",
    "learner_room_progress",
    "learner_lesson_progress",
)


def upgrade() -> None:
    for table_name in PROGRESS_TABLES:
        op.alter_column(
            table_name,
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            existing_nullable=False,
        )
        op.alter_column(
            table_name,
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            existing_nullable=False,
        )


def downgrade() -> None:
    for table_name in PROGRESS_TABLES:
        op.alter_column(
            table_name,
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            server_default=None,
            existing_nullable=False,
        )
        op.alter_column(
            table_name,
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            server_default=None,
            existing_nullable=False,
        )
