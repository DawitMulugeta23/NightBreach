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

BLOCKS = [
    (B.HEADING, {"text": "Who is allowed to do what?"}),
    (B.TEXT, {"text": (
        "Every file on a Linux system has an owner, a group and a set of permissions. "
        "Permissions are split into three classes - the owner (user), the group and "
        "everyone else (others) - and each class can be given read (r), write (w) and "
        "execute (x) rights."
    )}),
    (B.CODE, {"language": "bash", "code": "ls -l notes.txt"}),
    (B.TERMINAL_OUTPUT, {"text": "-rw-r--r-- 1 alice staff 220 Oct  6 09:12 notes.txt"}),
    (B.TEXT, {"text": (
        "Read the permission string from left to right. The first character is the file "
        "type. The next nine are three groups of three: owner (rw-), group (r--) and "
        "others (r--). Here the owner can read and write, while the group and everybody "
        "else can only read."
    )}),
    (B.HEADING, {"text": "Changing ownership and permissions"}),
    (B.CODE, {"language": "bash", "code": (
        "chmod 640 report.txt         # owner rw-, group r--, others ---\n"
        "chown alice:staff report.txt # set the owner and the group\n"
        "umask                        # permissions removed from newly created files"
    )}),
    (B.CALLOUT, {"type": "important", "title": "Cybersecurity connection", "text": (
        "Overly permissive files are one of the most common real-world findings. A backup, "
        "a configuration file or a key that everyone can read turns any low-privilege "
        "account into a source of secrets."
    )}),
    (B.HEADING, {"text": "Lab: find the exposed file"}),
    (B.TEXT, {"text": (
        "You get two machines on a private network: an attack machine, which is the "
        "terminal you control, and a target server. Find a file on the target whose "
        "permissions expose sensitive data and recover the flag stored in it."
    )}),
    (B.TEXT, {"text": (
        "1. Launch the lab and open the terminal on the attack machine.\n"
        "2. The lab network is shown next to the machines. Find the target by scanning it.\n"
        "3. Log in to the target over SSH as student with the password Student#2024.\n"
        "4. Look for places where backups are kept and compare the permissions of the files.\n"
        "5. Submit the flag you recover. It looks like NB{...}."
    )}),
    (B.CALLOUT, {"type": "tip", "title": "Hints", "text": (
        "nmap -sn lists the live hosts on a network. ls -l shows permissions. "
        "cat prints a file you are allowed to read."
    )}),
    (B.CALLOUT, {"type": "warning", "title": "The lab is disposable", "text": (
        "The attack machine can only reach the target. If you break something, reset the lab."
    )}),
]


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
