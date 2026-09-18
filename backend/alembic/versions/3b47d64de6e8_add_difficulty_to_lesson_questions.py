"""add difficulty to lesson questions

Revision ID: 3b47d64de6e8
Revises: add_user_lesson_progress
Create Date: 2026-09-14

"""
from alembic import op
import sqlalchemy as sa


revision = '3b47d64de6e8'
down_revision = 'add_user_lesson_progress'
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type first
    question_difficulty = sa.Enum('easy', 'medium', 'hard', name='question_difficulty')
    question_difficulty.create(op.get_bind(), checkfirst=True)

    # Add the column, default to 'easy' for existing rows
    op.add_column(
        'lesson_questions',
        sa.Column('difficulty', question_difficulty, nullable=False, server_default='easy')
    )
    op.alter_column('lesson_questions', 'difficulty', server_default=None)


def downgrade():
    op.drop_column('lesson_questions', 'difficulty')
    sa.Enum(name='question_difficulty').drop(op.get_bind(), checkfirst=True)
