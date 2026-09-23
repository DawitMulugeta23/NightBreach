"""
Seeds the Learning Paths hierarchy: Paths → Rooms → Lessons → Questions.

Content lives in db/content/ — one module per path (linux.py, networking.py)
plus stubs.py for placeholder paths. This module only knows how to upsert.

Idempotent: re-running updates existing rows by (slug | order_index) keys and
inserts only what's missing; user progress is never touched.

Runs automatically at backend startup (main.py, guarded by a Postgres advisory
lock so multi-worker launches can't race) and manually via:
    python -m db.seed_learning
"""
import asyncio
import uuid

from sqlalchemy import select, text

from db.session import AsyncSessionLocal
from db.models import (
    LearningPath, Room, Lesson, LessonQuestion, QuestionType, QuestionDifficulty,
)
from db.content.common import _resolve_answer_hash  # noqa: F401  (re-exported for CLI parity)
from db.content import SEED_DATA


async def seed(db=None):
    """Upsert all content. Pass an open AsyncSession to run inside a caller
    transaction (startup auto-seed does this while holding the advisory lock)."""
    if db is not None:
        return await _seed_with(db)
    async with AsyncSessionLocal() as session:
        return await _seed_with(session)


async def _seed_with(db):
    for path_data in SEED_DATA:
        result = await db.execute(
            select(LearningPath).where(LearningPath.slug == path_data['slug'])
        )
        path = result.scalar_one_or_none()
        if path is None:
            path = LearningPath(
                id=uuid.uuid4(),
                slug=path_data['slug'],
                title=path_data['title'],
                description=path_data['description'],
                icon=path_data['icon'],
                order_index=path_data['order_index'],
            )
            db.add(path)
            await db.flush()
            print(f'Created path: {path.title}')
        else:
            path.title = path_data['title']
            path.description = path_data['description']
            path.icon = path_data['icon']
            path.order_index = path_data['order_index']
            print(f'Updated path: {path.title}')

        for room_data in path_data['rooms']:
            result = await db.execute(
                select(Room)
                .where(Room.path_id == path.id)
                .where(Room.order_index == room_data['order_index'])
            )
            room = result.scalar_one_or_none()
            if room is None:
                room = Room(
                    id=uuid.uuid4(),
                    path_id=path.id,
                    order_index=room_data['order_index'],
                    title=room_data['title'],
                    description=room_data['description'],
                )
                db.add(room)
                await db.flush()
                print(f'  Created room: {room.title}')
            else:
                room.title = room_data['title']
                room.description = room_data['description']
                print(f'  Updated room: {room.title}')

            for lesson_data in room_data['lessons']:
                result = await db.execute(
                    select(Lesson)
                    .where(Lesson.room_id == room.id)
                    .where(Lesson.order_index == lesson_data['order_index'])
                )
                lesson = result.scalar_one_or_none()
                if lesson is None:
                    lesson = Lesson(
                        id=uuid.uuid4(),
                        room_id=room.id,
                        order_index=lesson_data['order_index'],
                        title=lesson_data['title'],
                        blocks=lesson_data['blocks'],
                    )
                    db.add(lesson)
                    await db.flush()
                    print(f'    Created lesson: {lesson.title}')
                else:
                    lesson.title = lesson_data['title']
                    lesson.blocks = lesson_data['blocks']
                    print(f'    Updated lesson: {lesson.title}')

                for q_data in lesson_data.get('questions', []):
                    result = await db.execute(
                        select(LessonQuestion)
                        .where(LessonQuestion.lesson_id == lesson.id)
                        .where(LessonQuestion.order_index == q_data['order_index'])
                    )
                    question = result.scalar_one_or_none()
                    if question is None:
                        question = LessonQuestion(
                            id=uuid.uuid4(),
                            lesson_id=lesson.id,
                            order_index=q_data['order_index'],
                            question_type=QuestionType(q_data['question_type']),
                            difficulty=QuestionDifficulty(q_data['difficulty']),
                            prompt=q_data['prompt'],
                            answer_hash=_resolve_answer_hash(q_data),
                            setup_script=q_data.get('setup_script'),
                        )
                        db.add(question)
                        print(f'      Created question #{q_data["order_index"]}')
                    else:
                        question.prompt = q_data['prompt']
                        question.difficulty = QuestionDifficulty(q_data['difficulty'])
                        question.answer_hash = _resolve_answer_hash(q_data)
                        question.setup_script = q_data.get('setup_script')
                        print(f'      Updated question #{q_data["order_index"]}')

    await db.commit()
    print('\nLearning paths seeded successfully')


# Advisory lock key for startup auto-seeding. Arbitrary constant; uniqueness
# across the application is what matters. Taken session-level: if another
# worker holds it, we simply skip (they are seeding the same content).
ADVISORY_LOCK_KEY = 742193


async def seed_on_startup():
    """
    Content auto-seed with a Postgres advisory lock.

    Guarantees the course catalog always matches the deployed code: a fresh
    database (or one missing newly authored rooms) is filled in on boot,
    so '0 modules / coming soon' can never result from a skipped manual
    seeder run. Cheap when already up to date: one SELECT per seed row.
    """
    async with AsyncSessionLocal() as db:
        try:
            got = (
                await db.execute(text("SELECT pg_try_advisory_lock(:k)"),
                                 {"k": ADVISORY_LOCK_KEY})
            ).scalar()
            if not got:
                print('Content seed: another worker holds the lock, skipping.')
                return
            await _seed_with(db)
        except Exception as e:
            print(f'WARNING: content auto-seed failed: {e}')
        finally:
            try:
                await db.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": ADVISORY_LOCK_KEY})
            except Exception:
                pass


if __name__ == '__main__':
    asyncio.run(seed())
