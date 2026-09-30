"""create learning progress tables

Revision ID: 8b6e2f4c1a90
Revises: 7e4a1c9d6b20
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8b6e2f4c1a90"
down_revision: Union[str, Sequence[str], None] = "7e4a1c9d6b20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


progress_status = sa.Enum(
    "NOT_STARTED",
    "IN_PROGRESS",
    "COMPLETED",
    name="progress_status",
    native_enum=False,
)


def upgrade() -> None:
    progress_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "learner_learning_path_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("learning_path_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            progress_status,
            nullable=False,
            server_default="NOT_STARTED",
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["learner_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["learning_path_id"],
            ["learning_paths.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id",
            "learning_path_id",
            name="uq_learner_learning_path_progress",
        ),
    )
    op.create_index(
        "ix_learner_learning_path_progress_learner_id",
        "learner_learning_path_progress",
        ["learner_id"],
    )
    op.create_index(
        "ix_learner_learning_path_progress_learning_path_id",
        "learner_learning_path_progress",
        ["learning_path_id"],
    )

    op.create_table(
        "learner_module_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("module_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            progress_status,
            nullable=False,
            server_default="NOT_STARTED",
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["learner_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["module_id"],
            ["modules.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id",
            "module_id",
            name="uq_learner_module_progress",
        ),
    )
    op.create_index(
        "ix_learner_module_progress_learner_id",
        "learner_module_progress",
        ["learner_id"],
    )
    op.create_index(
        "ix_learner_module_progress_module_id",
        "learner_module_progress",
        ["module_id"],
    )

    op.create_table(
        "learner_room_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("room_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            progress_status,
            nullable=False,
            server_default="NOT_STARTED",
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["learner_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id",
            "room_id",
            name="uq_learner_room_progress",
        ),
    )
    op.create_index(
        "ix_learner_room_progress_learner_id",
        "learner_room_progress",
        ["learner_id"],
    )
    op.create_index(
        "ix_learner_room_progress_room_id",
        "learner_room_progress",
        ["room_id"],
    )

    op.create_table(
        "learner_lesson_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            progress_status,
            nullable=False,
            server_default="NOT_STARTED",
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["learner_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id",
            "lesson_id",
            name="uq_learner_lesson_progress",
        ),
    )
    op.create_index(
        "ix_learner_lesson_progress_learner_id",
        "learner_lesson_progress",
        ["learner_id"],
    )
    op.create_index(
        "ix_learner_lesson_progress_lesson_id",
        "learner_lesson_progress",
        ["lesson_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_learner_lesson_progress_lesson_id",
        table_name="learner_lesson_progress",
    )
    op.drop_index(
        "ix_learner_lesson_progress_learner_id",
        table_name="learner_lesson_progress",
    )
    op.drop_table("learner_lesson_progress")

    op.drop_index(
        "ix_learner_room_progress_room_id",
        table_name="learner_room_progress",
    )
    op.drop_index(
        "ix_learner_room_progress_learner_id",
        table_name="learner_room_progress",
    )
    op.drop_table("learner_room_progress")

    op.drop_index(
        "ix_learner_module_progress_module_id",
        table_name="learner_module_progress",
    )
    op.drop_index(
        "ix_learner_module_progress_learner_id",
        table_name="learner_module_progress",
    )
    op.drop_table("learner_module_progress")

    op.drop_index(
        "ix_learner_learning_path_progress_learning_path_id",
        table_name="learner_learning_path_progress",
    )
    op.drop_index(
        "ix_learner_learning_path_progress_learner_id",
        table_name="learner_learning_path_progress",
    )
    op.drop_table("learner_learning_path_progress")

    progress_status.drop(op.get_bind(), checkfirst=True)
