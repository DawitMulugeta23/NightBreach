"""add user_lesson_progress + lessons list in room endpoint

Revision ID: add_user_lesson_progress
Revises: fix_sessions_user_id_type
Create Date: 2026-09-11
"""
from alembic import op

revision = 'add_user_lesson_progress'
down_revision = 'fix_sessions_user_id_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_lesson_progress (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
            completed_at TIMESTAMPTZ DEFAULT now(),
            UNIQUE (user_id, lesson_id)
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_user_lesson_progress_user_id ON user_lesson_progress (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_user_lesson_progress_lesson_id ON user_lesson_progress (lesson_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_lesson_progress CASCADE")
