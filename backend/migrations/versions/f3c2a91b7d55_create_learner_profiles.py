"""create learner_profiles for onboarding

Revision ID: f3c2a91b7d55
Revises: b1a7c3d94e20
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "f3c2a91b7d55"
down_revision = "b1a7c3d94e20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learner_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "learner_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("goals", sa.JSON(), nullable=False),
        sa.Column("technical_background", sa.String(32), nullable=True),
        sa.Column("computer_knowledge", sa.String(16), nullable=True),
        sa.Column("networking_knowledge", sa.String(16), nullable=True),
        sa.Column("linux_cli_knowledge", sa.String(16), nullable=True),
        sa.Column("web_security_knowledge", sa.String(16), nullable=True),
        sa.Column("practical_security_experience", sa.String(32), nullable=True),
        sa.Column("tool_experience", sa.JSON(), nullable=False),
        sa.Column("knowledge_gaps", sa.JSON(), nullable=False),
        sa.Column("recommended_learning_paths", sa.JSON(), nullable=False),
        sa.Column("recommended_practice", sa.JSON(), nullable=False),
        sa.Column("challenge_recommendation", sa.String(32), nullable=True),
        sa.Column("personalized_advice", sa.String(2000), nullable=True),
        sa.Column("specialization_slug", sa.String(64), nullable=True),
        sa.Column("specialization_locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_learner_profiles_learner_id",
        "learner_profiles",
        ["learner_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_learner_profiles_learner_id", table_name="learner_profiles")
    op.drop_table("learner_profiles")
