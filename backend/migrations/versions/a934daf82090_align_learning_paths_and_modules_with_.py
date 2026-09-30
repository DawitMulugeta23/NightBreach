"""align learning paths and modules with specification

Revision ID: a934daf82090
Revises: ec3cefc238b0
Create Date: 2026-09-28 16:24:34.273110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a934daf82090"
down_revision: Union[str, Sequence[str], None] = "ec3cefc238b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


learning_path_status = sa.Enum(
    "DRAFT",
    "PUBLISHED",
    "ARCHIVED",
    name="learning_path_status",
)

module_status = sa.Enum(
    "DRAFT",
    "PUBLISHED",
    "ARCHIVED",
    name="module_status",
)


def upgrade() -> None:
    """Upgrade schema."""

    # learning_paths
    op.alter_column(
        "learning_paths",
        "name",
        new_column_name="title",
        existing_type=sa.String(length=255),
        existing_nullable=False,
    )

    op.add_column(
        "learning_paths",
        sa.Column(
            "position",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.alter_column(
        "learning_paths",
        "position",
        server_default=None,
    )

    op.alter_column(
        "learning_paths",
        "slug",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.String(length=100),
        existing_nullable=False,
    )

    op.alter_column(
        "learning_paths",
        "description",
        existing_type=sa.TEXT(),
        nullable=False,
    )

    learning_path_status.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "learning_paths",
        "status",
        existing_type=sa.VARCHAR(length=32),
        type_=learning_path_status,
        postgresql_using="status::learning_path_status",
        existing_nullable=False,
    )

    op.create_check_constraint(
        "ck_learning_paths_position_nonnegative",
        "learning_paths",
        "position >= 0",
    )

    # modules
    module_status.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "modules",
        "name",
        new_column_name="title",
        existing_type=sa.String(length=255),
        existing_nullable=False,
    )

    op.add_column(
        "modules",
        sa.Column(
            "slug",
            sa.String(length=100),
            nullable=False,
            server_default="default",
        ),
    )

    op.alter_column(
        "modules",
        "slug",
        server_default=None,
    )

    op.add_column(
        "modules",
        sa.Column(
            "status",
            module_status,
            nullable=False,
            server_default="DRAFT",
        ),
    )

    op.alter_column(
        "modules",
        "status",
        server_default=None,
    )

    op.alter_column(
        "modules",
        "description",
        existing_type=sa.TEXT(),
        nullable=False,
    )

    op.create_unique_constraint(
        "uq_modules_learning_path_slug",
        "modules",
        ["learning_path_id", "slug"],
    )

    op.create_unique_constraint(
        "uq_modules_learning_path_position",
        "modules",
        ["learning_path_id", "position"],
    )

    op.create_check_constraint(
        "ck_modules_position_nonnegative",
        "modules",
        "position >= 0",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # modules
    op.drop_constraint(
        "ck_modules_position_nonnegative",
        "modules",
        type_="check",
    )

    op.drop_constraint(
        "uq_modules_learning_path_position",
        "modules",
        type_="unique",
    )

    op.drop_constraint(
        "uq_modules_learning_path_slug",
        "modules",
        type_="unique",
    )

    op.drop_column("modules", "status")
    op.drop_column("modules", "slug")

    op.alter_column(
        "modules",
        "title",
        new_column_name="name",
        existing_type=sa.String(length=200),
        existing_nullable=False,
    )

    op.alter_column(
        "modules",
        "description",
        existing_type=sa.TEXT(),
        nullable=True,
    )

    module_status.drop(op.get_bind(), checkfirst=True)

    # learning_paths
    op.drop_constraint(
        "ck_learning_paths_position_nonnegative",
        "learning_paths",
        type_="check",
    )

    op.alter_column(
        "learning_paths",
        "status",
        existing_type=learning_path_status,
        type_=sa.VARCHAR(length=32),
        postgresql_using="status::text",
        existing_nullable=False,
    )

    learning_path_status.drop(op.get_bind(), checkfirst=True)

    op.alter_column(
        "learning_paths",
        "description",
        existing_type=sa.TEXT(),
        nullable=True,
    )

    op.drop_column("learning_paths", "position")

    op.alter_column(
        "learning_paths",
        "slug",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
    )

    op.alter_column(
        "learning_paths",
        "title",
        new_column_name="name",
        existing_type=sa.String(length=200),
        existing_nullable=False,
    )
