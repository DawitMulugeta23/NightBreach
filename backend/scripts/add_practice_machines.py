"""Give lessons 1-6 of 'Linux Command Line Basics' an OPTIONAL practice machine.
Idempotent; progress and the existing required questions are untouched.
Run from backend/:  python scripts/add_practice_machines.py
"""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.lesson import Lesson
from app.models.lesson_practice import LessonPractice
from app.models.practice import Practice, PracticeActivityMode, PracticeStatus
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.room import Room

ROOM_SLUG = "linux-command-line-basics"
LAB_SLUG = "linux-practice"
LESSON_SLUGS = [
    "linux-and-the-shell",
    "navigating-the-filesystem",
    "files-and-directories",
    "absolute-and-relative-paths",
    "reading-command-help",
    "command-line-workflow",
]


async def main() -> None:
    async with AsyncSessionLocal() as session:
        room = (await session.execute(select(Room).where(Room.slug == ROOM_SLUG))).scalar_one()

        for slug in LESSON_SLUGS:
            lesson = (await session.execute(
                select(Lesson).where(Lesson.room_id == room.id, Lesson.slug == slug)
            )).scalar_one_or_none()
            if lesson is None:
                print(f"skipped {slug}: lesson not found")
                continue

            title = f"{lesson.title} - Practice Machine"
            practice = (await session.execute(
                select(Practice).where(Practice.title == title)
            )).scalar_one_or_none()

            if practice is None:
                practice = Practice(
                    id=uuid4(),
                    title=title,
                    description="A private terminal for trying the commands from this lesson.",
                    status=PracticeStatus.PUBLISHED,
                    activity_mode=PracticeActivityMode.PRACTICAL,
                    environment_requirement_id=None,
                )
                session.add(practice)
                await session.flush()

            has_activity = (await session.execute(
                select(PracticeActivity.id).where(PracticeActivity.practice_id == practice.id)
            )).first()
            if has_activity is None:
                session.add(PracticeActivity(
                    id=uuid4(),
                    practice_id=practice.id,
                    position=0,
                    activity_type=PracticeActivityType.PRACTICAL_TASK,
                    title="Try the commands yourself",
                    instructions=(
                        "Start the machine and run the commands from this lesson in your own "
                        "terminal. This step is optional and does not affect your progress."
                    ),
                    required=False,
                    evaluation_type=PracticeEvaluationType.COMMAND_RESULT,
                    environment_requirement_id=None,
                    configuration={"lab_slug": LAB_SLUG},
                    guidance_policy={},
                ))

            links = (await session.execute(
                select(LessonPractice).where(LessonPractice.lesson_id == lesson.id)
            )).scalars().all()

            if any(link.practice_id == practice.id for link in links):
                print(f"{lesson.title}: already has a practice machine")
                continue

            # Show the machine first: move the existing question practice down one place.
            for link in links:
                if link.position == 0:
                    link.position = 1
            await session.flush()

            session.add(LessonPractice(
                id=uuid4(), lesson_id=lesson.id, practice_id=practice.id,
                position=0, required=False,
            ))
            print(f"{lesson.title}: practice machine added")

        await session.commit()


asyncio.run(main())
