import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from db.session import AsyncSessionLocal
from db.models import Lesson

LESSONS_ROOT = Path(__file__).resolve().parent.parent.parent / "lessons"


async def seed_lessons():
    async with AsyncSessionLocal() as db:
        for lesson_file in sorted(LESSONS_ROOT.glob("*.json")):
            data = json.loads(lesson_file.read_text())

            result = await db.execute(select(Lesson).where(Lesson.order_index == data["order_index"]))
            existing = result.scalar_one_or_none()

            if existing is not None:
                existing.title = data["title"]
                existing.blocks = data["blocks"]
                print(f"Updated lesson {data['order_index']}: {data['title']}")
            else:
                db.add(Lesson(
                    order_index=data["order_index"],
                    title=data["title"],
                    blocks=data["blocks"],
                ))
                print(f"Added lesson {data['order_index']}: {data['title']}")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_lessons())
