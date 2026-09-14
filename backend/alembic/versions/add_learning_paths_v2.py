"""add learning paths hierarchy (paths -> rooms -> lessons -> questions)

Revision ID: add_learning_paths_v2
Revises: 96a1fe2fefe5
Create Date: 2026-09-11
"""
from alembic import op

revision = 'add_learning_paths_v2'
down_revision = '96a1fe2fefe5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # question_type enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE question_type AS ENUM ('text', 'terminal');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    # learning_paths
    op.execute("""
        CREATE TABLE IF NOT EXISTS learning_paths (
            id UUID PRIMARY KEY,
            slug VARCHAR NOT NULL UNIQUE,
            title VARCHAR NOT NULL,
            description TEXT NOT NULL,
            icon VARCHAR,
            order_index INTEGER NOT NULL UNIQUE
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_learning_paths_slug ON learning_paths (slug)")

    # rooms
    op.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id UUID PRIMARY KEY,
            path_id UUID NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
            order_index INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            description TEXT NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_rooms_path_id ON rooms (path_id)")

    # add room_id to lessons (nullable, existing lessons keep working)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE lessons ADD COLUMN room_id UUID REFERENCES rooms(id) ON DELETE CASCADE;
        EXCEPTION WHEN duplicate_column THEN null;
        END $$;
    """)

    # FIX: Drop old global unique constraint on lessons.order_index and replace
    # with a composite (room_id, order_index) constraint, since lessons now
    # belong to rooms. Old flat structure required globally unique order_index.
    op.execute("ALTER TABLE lessons DROP CONSTRAINT IF EXISTS lessons_order_index_key;")
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE lessons ADD CONSTRAINT lessons_room_order_unique UNIQUE (room_id, order_index);
        EXCEPTION WHEN duplicate_table THEN null;
        END $$;
    """)

    # lesson_questions
    op.execute("""
        CREATE TABLE IF NOT EXISTS lesson_questions (
            id UUID PRIMARY KEY,
            lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
            order_index INTEGER NOT NULL,
            question_type question_type NOT NULL,
            prompt TEXT NOT NULL,
            answer_hash VARCHAR NOT NULL,
            setup_script TEXT
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_lesson_questions_lesson_id ON lesson_questions (lesson_id)")

    # user_question_progress
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_question_progress (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            question_id UUID NOT NULL REFERENCES lesson_questions(id) ON DELETE CASCADE,
            answered_at TIMESTAMPTZ DEFAULT now()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_user_question_progress_user_id ON user_question_progress (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_user_question_progress_question_id ON user_question_progress (question_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_question_progress CASCADE")
    op.execute("DROP TABLE IF EXISTS lesson_questions CASCADE")
    op.execute("ALTER TABLE lessons DROP CONSTRAINT IF EXISTS lessons_room_order_unique")
    op.execute("ALTER TABLE lessons DROP COLUMN IF EXISTS room_id")
    op.execute("DROP TABLE IF EXISTS rooms CASCADE")
    op.execute("DROP TABLE IF EXISTS learning_paths CASCADE")
    op.execute("DROP TYPE IF EXISTS question_type")
