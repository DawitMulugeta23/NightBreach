"""create CTF domain

Revision ID: ef79c9e0fe46
Revises: b56f065d408a
Create Date: 2026-09-30 07:28:27.983362
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ef79c9e0fe46"
down_revision: Union[str, Sequence[str], None] = "b56f065d408a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ctf_challenge_groups",
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), server_default="0", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_ctf_challenge_groups_code",
        "ctf_challenge_groups",
        ["code"],
        unique=True,
    )

    op.create_table(
        "ctf_challenges",
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("scenario", sa.Text(), nullable=True),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=False),
        sa.Column(
            "mode",
            sa.Enum(
                "GUIDED",
                "INDEPENDENT",
                name="ctf_challenge_mode",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "PUBLISHED",
                "ARCHIVED",
                name="ctf_challenge_status",
                native_enum=False,
            ),
            server_default="draft",
            nullable=False,
        ),
        sa.Column(
            "challenge_type",
            sa.Enum(
                "FLAG",
                "OUTPUT_EXTRACTION",
                "ANSWER",
                name="ctf_challenge_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("environment_requirement_id", sa.Uuid(), nullable=True),
        sa.Column(
            "validation_config",
            sa.JSON(),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["ctf_challenge_groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_ctf_challenges_environment_requirement_id",
        "ctf_challenges",
        ["environment_requirement_id"],
        unique=False,
    )
    op.create_index(
        "ix_ctf_challenges_group_id",
        "ctf_challenges",
        ["group_id"],
        unique=False,
    )
    op.create_index(
        "ix_ctf_challenges_slug",
        "ctf_challenges",
        ["slug"],
        unique=True,
    )

    op.create_table(
        "ctf_attempts",
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("challenge_id", sa.Uuid(), nullable=False),
        sa.Column("environment_id", sa.Uuid(), nullable=True),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "CREATED",
                "STARTED",
                "IN_PROGRESS",
                "SUBMITTED",
                "EVALUATING",
                "PASSED",
                "FAILED",
                "ENVIRONMENT_FAILED",
                name="ctf_attempt_status",
                native_enum=False,
            ),
            server_default="created",
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["ctf_challenges.id"],
        ),
        sa.ForeignKeyConstraint(
            ["learner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id",
            "challenge_id",
            "attempt_number",
            name="uq_ctf_attempt_learner_challenge_number",
        ),
    )

    op.create_index(
        "ix_ctf_attempts_challenge_id",
        "ctf_attempts",
        ["challenge_id"],
        unique=False,
    )
    op.create_index(
        "ix_ctf_attempts_environment_id",
        "ctf_attempts",
        ["environment_id"],
        unique=False,
    )
    op.create_index(
        "ix_ctf_attempts_learner_id",
        "ctf_attempts",
        ["learner_id"],
        unique=False,
    )
    op.create_index(
        "ix_ctf_attempts_session_id",
        "ctf_attempts",
        ["session_id"],
        unique=False,
    )

    op.create_table(
        "ctf_submissions",
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("submission_value", sa.Text(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("result", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["ctf_attempts.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_ctf_submissions_attempt_id",
        "ctf_submissions",
        ["attempt_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ctf_submissions_attempt_id",
        table_name="ctf_submissions",
    )
    op.drop_table("ctf_submissions")

    op.drop_index(
        "ix_ctf_attempts_session_id",
        table_name="ctf_attempts",
    )
    op.drop_index(
        "ix_ctf_attempts_learner_id",
        table_name="ctf_attempts",
    )
    op.drop_index(
        "ix_ctf_attempts_environment_id",
        table_name="ctf_attempts",
    )
    op.drop_index(
        "ix_ctf_attempts_challenge_id",
        table_name="ctf_attempts",
    )
    op.drop_table("ctf_attempts")

    op.drop_index(
        "ix_ctf_challenges_slug",
        table_name="ctf_challenges",
    )
    op.drop_index(
        "ix_ctf_challenges_group_id",
        table_name="ctf_challenges",
    )
    op.drop_index(
        "ix_ctf_challenges_environment_requirement_id",
        table_name="ctf_challenges",
    )
    op.drop_table("ctf_challenges")

    op.drop_index(
        "ix_ctf_challenge_groups_code",
        table_name="ctf_challenge_groups",
    )
    op.drop_table("ctf_challenge_groups")
