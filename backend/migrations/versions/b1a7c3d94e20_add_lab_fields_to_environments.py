"""add lab fields to sandbox environments

Revision ID: b1a7c3d94e20
Revises: 9c7d5e2a1b34
"""
import sqlalchemy as sa
from alembic import op

revision = "b1a7c3d94e20"
down_revision = "9c7d5e2a1b34"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sandbox_environments", sa.Column("lab_slug", sa.String(100), nullable=True))
    op.add_column("sandbox_environments", sa.Column("lab_secret", sa.String(64), nullable=True))
    op.add_column("sandbox_environments", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_sandbox_environments_lab_slug", "sandbox_environments", ["lab_slug"])


def downgrade() -> None:
    op.drop_index("ix_sandbox_environments_lab_slug", table_name="sandbox_environments")
    op.drop_column("sandbox_environments", "expires_at")
    op.drop_column("sandbox_environments", "lab_secret")
    op.drop_column("sandbox_environments", "lab_slug")
