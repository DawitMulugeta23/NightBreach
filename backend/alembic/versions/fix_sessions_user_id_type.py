"""fix sessions.user_id type varchar -> uuid

Revision ID: fix_sessions_user_id_type
Revises: add_learning_paths_v2
Create Date: 2026-09-11
"""
from alembic import op

revision = 'fix_sessions_user_id_type'
down_revision = 'add_learning_paths_v2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Dev-only data — containers will be reconciled by startup orphan cleanup.
    # Cascade: containers.session_id references sessions.id
    op.execute("DELETE FROM containers")
    op.execute("DELETE FROM sessions")

    # Change user_id from VARCHAR to UUID
    op.execute("""
        ALTER TABLE sessions
        ALTER COLUMN user_id TYPE UUID
        USING user_id::uuid;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE sessions
        ALTER COLUMN user_id TYPE VARCHAR
        USING user_id::varchar;
    """)
