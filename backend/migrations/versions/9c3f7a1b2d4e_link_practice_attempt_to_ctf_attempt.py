"""link practice attempts to ctf attempts

Revision ID: 9c3f7a1b2d4e
Revises: ef79c9e0fe46
Create Date: 2026-09-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c3f7a1b2d4e"
down_revision: Union[str, Sequence[str], None] = "ef79c9e0fe46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "practice_attempts",
        sa.Column(
            "ctf_attempt_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_practice_attempts_ctf_attempt_id",
        "practice_attempts",
        ["ctf_attempt_id"],
        unique=True,
    )

    op.create_foreign_key(
        "fk_practice_attempts_ctf_attempt_id",
        "practice_attempts",
        "ctf_attempts",
        ["ctf_attempt_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_practice_attempts_ctf_attempt_id",
        "practice_attempts",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_practice_attempts_ctf_attempt_id",
        table_name="practice_attempts",
    )

    op.drop_column(
        "practice_attempts",
        "ctf_attempt_id",
    )
