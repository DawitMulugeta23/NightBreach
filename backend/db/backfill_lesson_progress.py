"""
Backfill user_lesson_progress for users who answered all questions
in a lesson before the automatic marking was added.
Idempotent — safe to re-run.
"""
import asyncio
import uuid

from sqlalchemy import select, func

from db.session import AsyncSessionLocal
from db.models import (
    User, Lesson, LessonQuestion, UserQuestionProgress, UserLessonProgress,
)


async def backfill():
    async with AsyncSessionLocal() as db:
        # Get all lessons
        result = await db.execute(select(Lesson.id))
        lesson_ids = [row[0] for row in result.all()]

        # Get all users
        result = await db.execute(select(User.id))
        user_ids = [row[0] for row in result.all()]

        total_added = 0
        for user_id in user_ids:
            for lesson_id in lesson_ids:
                # All question ids in this lesson
                result = await db.execute(
                    select(LessonQuestion.id).where(LessonQuestion.lesson_id == lesson_id)
                )
                question_ids = {row[0] for row in result.all()}

                # Skip lessons with no questions
                if not question_ids:
                    continue

                # Answered question ids by this user
                result = await db.execute(
                    select(UserQuestionProgress.question_id)
                    .where(UserQuestionProgress.user_id == user_id)
                    .where(UserQuestionProgress.question_id.in_(question_ids))
                )
                answered = {row[0] for row in result.all()}

                if not question_ids.issubset(answered):
                    continue

                # All answered — mark lesson complete if not already
                result = await db.execute(
                    select(UserLessonProgress)
                    .where(UserLessonProgress.user_id == user_id)
                    .where(UserLessonProgress.lesson_id == lesson_id)
                )
                if result.scalar_one_or_none() is None:
                    db.add(UserLessonProgress(user_id=user_id, lesson_id=lesson_id))
                    total_added += 1
                    print(f"  Marked lesson {lesson_id} complete for user {user_id}")

        await db.commit()
        print(f"\n✅ Backfilled {total_added} lesson completions")


if __name__ == "__main__":
    asyncio.run(backfill())
