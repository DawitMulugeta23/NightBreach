"""add user_wrong_attempts tombstone table

Persists wrong submissions so Algorithm 4 (auto-upgrade) knows a question's
first attempt was wrong even after a server restart or across multiple
worker processes. Kept separate from user_question_progress, whose
existence must keep meaning "answered correctly" (spec §3.3).

Revision ID: b8c3d5e6f1a2
Revises: e7a2c4f9b1d3
Create Date: 2026-09-23

"""
from alembic import op

revision = "b8c3d5e6f1a2"
down_revision = "e7a2c4f9b1d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_wrong_attempts (
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            question_id UUID NOT NULL REFERENCES lesson_questions(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (user_id, question_id)
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_user_wrong_attempts_user_id ON user_wrong_attempts (user_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_wrong_attempts")
