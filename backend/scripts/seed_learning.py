from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.lesson import Lesson, LessonStatus
from app.models.lesson_content_block import (
    LessonContentBlock,
    LessonContentBlockType,
)
from app.models.lesson_practice import LessonPractice
from app.models.learning_path import LearningPath, LearningPathStatus
from app.models.module import Module, ModuleStatus
from app.models.practice import (
    Practice,
    PracticeActivityMode,
    PracticeStatus,
)
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.room import Room, RoomAccessLevel, RoomStatus


async def seed_learning() -> None:
    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(LearningPath).where(
                LearningPath.slug == "linux-fundamentals"
            )
        )

        if existing.scalar_one_or_none() is not None:
            print("Learning catalog already exists: linux-fundamentals")
            return

        path = LearningPath(
            slug="linux-fundamentals",
            title="Linux Fundamentals",
            description=(
                "Build a practical foundation in Linux, the command line, "
                "filesystems, and essential commands used in cybersecurity."
            ),
            status=LearningPathStatus.PUBLISHED,
            position=0,
        )

        module = Module(
            slug="linux-basics",
            title="Linux Basics",
            description=(
                "Learn the Linux command-line environment and the basic "
                "commands used to navigate and inspect a system."
            ),
            status=ModuleStatus.PUBLISHED,
            position=0,
        )

        room = Room(
            slug="linux-command-line",
            title="Linux Command Line",
            description=(
                "Learn how to work with the Linux shell and perform "
                "fundamental filesystem operations."
            ),
            status=RoomStatus.PUBLISHED,
            position=0,
            access_level=RoomAccessLevel.FREE,
        )

        lesson_one = Lesson(
            slug="introduction-to-linux-cli",
            title="Introduction to the Linux CLI",
            description=(
                "Understand what the Linux command line is and how "
                "commands are executed through a shell."
            ),
            position=0,
            status=LessonStatus.PUBLISHED,
        )

        lesson_two = Lesson(
            slug="files-and-directories",
            title="Files and Directories",
            description=(
                "Learn how Linux represents files and directories and "
                "how to navigate between them."
            ),
            position=1,
            status=LessonStatus.PUBLISHED,
        )

        lesson_three = Lesson(
            slug="basic-linux-commands",
            title="Basic Linux Commands",
            description=(
                "Practice several essential Linux commands used for "
                "system navigation and inspection."
            ),
            position=2,
            status=LessonStatus.PUBLISHED,
        )

        path.modules.append(module)
        module.rooms.append(room)
        room.lessons.extend(
            [
                lesson_one,
                lesson_two,
                lesson_three,
            ]
        )

        lesson_one.content_blocks.extend(
            [
                LessonContentBlock(
                    position=0,
                    block_type=LessonContentBlockType.HEADING,
                    content={
                        "text": "What is the Linux command line?"
                    },
                ),
                LessonContentBlock(
                    position=1,
                    block_type=LessonContentBlockType.TEXT,
                    content={
                        "text": (
                            "The Linux command line is a text-based "
                            "interface for interacting with the operating "
                            "system. Commands are entered into a shell, "
                            "which interprets them and requests the "
                            "corresponding operation from the system."
                        )
                    },
                ),
                LessonContentBlock(
                    position=2,
                    block_type=LessonContentBlockType.CODE,
                    content={
                        "language": "bash",
                        "code": "pwd",
                    },
                ),
                LessonContentBlock(
                    position=3,
                    block_type=LessonContentBlockType.TEXT,
                    content={
                        "text": (
                            "The pwd command prints the current working "
                            "directory."
                        )
                    },
                ),
            ]
        )

        lesson_two.content_blocks.extend(
            [
                LessonContentBlock(
                    position=0,
                    block_type=LessonContentBlockType.HEADING,
                    content={
                        "text": "Working with files and directories"
                    },
                ),
                LessonContentBlock(
                    position=1,
                    block_type=LessonContentBlockType.TEXT,
                    content={
                        "text": (
                            "Linux organizes files inside directories. "
                            "The shell provides commands for viewing the "
                            "current location and moving through the "
                            "filesystem."
                        )
                    },
                ),
                LessonContentBlock(
                    position=2,
                    block_type=LessonContentBlockType.CODE,
                    content={
                        "language": "bash",
                        "code": "pwd\nls\ncd /tmp",
                    },
                ),
                LessonContentBlock(
                    position=3,
                    block_type=LessonContentBlockType.LIST,
                    content={
                        "items": [
                            "pwd - print the current working directory",
                            "ls - list directory contents",
                            "cd - change the current directory",
                        ]
                    },
                ),
            ]
        )

        lesson_three.content_blocks.extend(
            [
                LessonContentBlock(
                    position=0,
                    block_type=LessonContentBlockType.HEADING,
                    content={
                        "text": "Essential commands"
                    },
                ),
                LessonContentBlock(
                    position=1,
                    block_type=LessonContentBlockType.TEXT,
                    content={
                        "text": (
                            "These commands are frequently used when "
                            "working from a Linux terminal."
                        )
                    },
                ),
                LessonContentBlock(
                    position=2,
                    block_type=LessonContentBlockType.CODE,
                    content={
                        "language": "bash",
                        "code": "pwd\nls\nwhoami\nid",
                    },
                ),
            ]
        )

        practice = Practice(
            title="Linux Command Basics Practice",
            description=(
                "Check your understanding of several basic Linux "
                "commands."
            ),
            status=PracticeStatus.PUBLISHED,
            activity_mode=PracticeActivityMode.TEXT,
        )

        activities = [
            PracticeActivity(
                position=0,
                activity_type=PracticeActivityType.TEXT_QUESTION,
                title="Current directory",
                instructions=(
                    "Which Linux command prints the current working "
                    "directory?"
                ),
                required=True,
                evaluation_type=PracticeEvaluationType.TEXT_EXACT,
                configuration={
                    "expected_answer": "pwd",
                },
                guidance_policy={},
            ),
            PracticeActivity(
                position=1,
                activity_type=PracticeActivityType.TEXT_QUESTION,
                title="List files",
                instructions=(
                    "Which Linux command lists files and directories "
                    "in the current directory?"
                ),
                required=True,
                evaluation_type=PracticeEvaluationType.TEXT_EXACT,
                configuration={
                    "expected_answer": "ls",
                },
                guidance_policy={},
            ),
            PracticeActivity(
                position=2,
                activity_type=PracticeActivityType.TEXT_QUESTION,
                title="Current user",
                instructions=(
                    "Which Linux command prints the username of the "
                    "current user?"
                ),
                required=True,
                evaluation_type=PracticeEvaluationType.TEXT_EXACT,
                configuration={
                    "expected_answer": "whoami",
                },
                guidance_policy={},
            ),
        ]

        practice.activities.extend(activities)

        lesson_practice = LessonPractice(
            position=0,
            required=True,
            practice=practice,
        )

        lesson_three.lesson_practices.append(lesson_practice)

        session.add(path)

        await session.commit()

        print("Created learning catalog:")
        print("  Path:   Linux Fundamentals")
        print("  Module: Linux Basics")
        print("  Room:   Linux Command Line")
        print("  Lessons: 3")
        print("  Practice activities: 3")


if __name__ == "__main__":
    asyncio.run(seed_learning())
