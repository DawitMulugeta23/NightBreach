"""Replace the content blocks of the Linux Command Line Basics lessons.
Progress, practice and the lab are untouched.   Run from backend/:
    python scripts/update_lesson_content.py
"""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.lesson import Lesson
from app.models.lesson_content_block import LessonContentBlock, LessonContentBlockType
from app.models.room import Room
from lessons import CONTENT


async def main() -> None:
    async with AsyncSessionLocal() as session:
        room = (await session.execute(
            select(Room).where(Room.slug == "linux-command-line-basics")
        )).scalar_one()

        for slug, blocks in CONTENT.items():
            lesson = (await session.execute(
                select(Lesson).where(Lesson.room_id == room.id, Lesson.slug == slug)
            )).scalar_one_or_none()
            if lesson is None:
                print(f"skipped {slug}: lesson not found")
                continue

            await session.execute(
                delete(LessonContentBlock).where(LessonContentBlock.lesson_id == lesson.id)
            )
            for index, (name, content) in enumerate(blocks):
                session.add(LessonContentBlock(
                    id=uuid4(), lesson_id=lesson.id, position=index,
                    block_type=LessonContentBlockType[name], content=content,
                ))
            print(f"{lesson.title}: {len(blocks)} content blocks")

        await session.commit()


asyncio.run(main())
