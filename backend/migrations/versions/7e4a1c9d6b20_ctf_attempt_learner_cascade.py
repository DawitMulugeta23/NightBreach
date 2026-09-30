"""cascade CTF attempts when learner is deleted

Revision ID: 7e4a1c9d6b20
Revises: 9c3f7a1b2d4e
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op


revision: str = "7e4a1c9d6b20"
down_revision: Union[str, Sequence[str], None] = "9c3f7a1b2d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "ctf_attempts_learner_id_fkey",
        "ctf_attempts",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "ctf_attempts_learner_id_fkey",
        "ctf_attempts",
        "users",
        ["learner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ctf_attempts_learner_id_fkey",
        "ctf_attempts",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "ctf_attempts_learner_id_fkey",
        "ctf_attempts",
        "users",
        ["learner_id"],
        ["id"],
    )
