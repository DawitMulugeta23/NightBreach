"""Seed lesson 7 of 'Linux Command Line Basics': Linux File Permissions (lab).

Idempotent. Run from backend/:  python scripts/seed_linux_permissions_lab.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select

from app.db.session import AsyncSessionLocal
from app.models.ctf_challenge import (
    CTFChallenge,
    CTFChallengeGroup,
    CTFChallengeMode,
    CTFChallengeStatus,
    CTFChallengeType,
)
from app.models.lesson import (
    Lesson,
    LessonAccessOverride,
    LessonCompletionRule,
    LessonStatus,
)
from app.models.lesson_content_block import LessonContentBlock, LessonContentBlockType
from app.models.lesson_practice import LessonPractice
from app.models.practice import Practice, PracticeActivityMode, PracticeStatus
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.room import Room

ROOM_SLUG = "linux-command-line-basics"
LESSON_SLUG = "linux-file-permissions"
LAB_SLUG = "linux-file-permissions"
OBJECTIVE_ID = "permissions-flag-001"
CHALLENGE_SLUG = "linux-file-permissions-lab"

B = LessonContentBlockType

from lessons.linux_file_permissions import BLOCKS as _BLOCK_DATA  # noqa: E402

BLOCKS = [(B[name], content) for name, content in _BLOCK_DATA]


async def get_or_create(session, model, **filters):
    result = await session.execute(select(model).filter_by(**filters))
    obj = result.scalar_one_or_none()
    if obj:
        return obj, False
    obj = model(id=uuid4(), **filters)
    session.add(obj)
    # Required fields are populated by the caller before the next query.
    return obj, True


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        room = (await session.execute(select(Room).where(Room.slug == ROOM_SLUG))).scalar_one()

        # --- CTF challenge that points at the lab ---------------------------
        group, _ = await get_or_create(session, CTFChallengeGroup, code="linux-labs")
        group.name = "Linux Labs"
        group.description = "Hands-on Linux labs run on isolated lab machines."
        group.position = 0

        challenge, _ = await get_or_create(session, CTFChallenge, slug=CHALLENGE_SLUG)
        challenge.title = "Recover the exposed flag"
        challenge.description = "A file on the target server is readable by everyone."
        challenge.objective = "Find the file with unsafe permissions and submit the flag stored in it."
        challenge.scenario = "A backup file on a Linux server was left world-readable."
        challenge.group_id = group.id
        challenge.difficulty = "beginner"
        challenge.mode = CTFChallengeMode.GUIDED
        challenge.status = CTFChallengeStatus.PUBLISHED
        challenge.challenge_type = CTFChallengeType.FLAG
        challenge.environment_requirement_id = None
        challenge.validation_config = {
            "lab": {"slug": LAB_SLUG, "objective_id": OBJECTIVE_ID},
            "comparison": "normalized",
        }

        # --- lesson ---------------------------------------------------------
        last_position = (await session.execute(
            select(func.max(Lesson.position)).where(Lesson.room_id == room.id)
        )).scalar()

        lesson, created = await get_or_create(session, Lesson, room_id=room.id, slug=LESSON_SLUG)
        lesson.title = "Linux File Permissions"
        lesson.description = (
            "Read ownership and permissions, then use an attack machine to find a "
            "file that exposes sensitive data on a target server."
        )
        lesson.status = LessonStatus.PUBLISHED
        lesson.access_override = LessonAccessOverride.FREE
        lesson.completion_rule = LessonCompletionRule.REQUIRED_PRACTICE
        lesson.environment_requirement_id = None
        if created:
            lesson.position = 0 if last_position is None else last_position + 1
            for index, (block_type, content) in enumerate(BLOCKS):
                session.add(LessonContentBlock(
                    id=uuid4(), lesson_id=lesson.id, position=index,
                    block_type=block_type, content=content,
                ))

        # --- practice: a quiz question plus the required lab ----------------
        practice, practice_created = await get_or_create(
            session, Practice, title="Linux File Permissions - Practice"
        )
        practice.description = "Check the permission basics, then complete the lab."
        practice.status = PracticeStatus.PUBLISHED
        practice.activity_mode = PracticeActivityMode.PRACTICAL
        practice.environment_requirement_id = None

        if practice_created:
            options = [
                "Only the owner",
                "The owner and the group only",
                "Everyone on the system",
                "Nobody",
            ]
            session.add(PracticeActivity(
                id=uuid4(), practice_id=practice.id, position=0,
                activity_type=PracticeActivityType.TEXT_QUESTION,
                title="In -rw-r--r--, who is allowed to read the file?",
                instructions="Choose the correct answer.",
                required=True,
                evaluation_type=PracticeEvaluationType.MULTIPLE_CHOICE,
                environment_requirement_id=None,
                configuration={"options": options, "correct_answer": "Everyone on the system"},
                guidance_policy={},
            ))
            session.add(PracticeActivity(
                id=uuid4(), practice_id=practice.id, position=1,
                activity_type=PracticeActivityType.GUIDED_CTF,
                title="Recover the exposed flag",
                instructions=(
                    "Launch the lab, find the file on the target server whose permissions "
                    "expose sensitive data, and submit the flag you recover."
                ),
                required=True,
                evaluation_type=PracticeEvaluationType.FLAG_SUBMISSION,
                environment_requirement_id=None,
                configuration={"challenge_id": str(challenge.id), "lab_slug": LAB_SLUG},
                guidance_policy={},
            ))
            session.add(LessonPractice(
                id=uuid4(), lesson_id=lesson.id, practice_id=practice.id,
                position=0, required=True,
            ))

        await session.commit()
        print(f"lesson {'created' if created else 'already present'}: {lesson.title} "
              f"(position {lesson.position}, id {lesson.id})")


asyncio.run(seed())
