from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import asyncio
from uuid import uuid4

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.learning_path import LearningPath, LearningPathStatus
from app.models.module import Module, ModuleStatus
from app.models.room import Room, RoomStatus, RoomAccessLevel
from app.models.lesson import (
    Lesson,
    LessonStatus,
    LessonAccessOverride,
    LessonCompletionRule,
)
from app.models.lesson_content_block import (
    LessonContentBlock,
    LessonContentBlockType,
)
from app.models.practice import Practice, PracticeStatus, PracticeActivityMode
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.lesson_practice import LessonPractice


async def get_or_create(session, model, **filters):
    result = await session.execute(select(model).filter_by(**filters))
    obj = result.scalar_one_or_none()

    if obj:
        return obj, False

    obj = model(id=uuid4(), **filters)
    session.add(obj)

    # Do not flush here.
    # Required fields are populated by the caller immediately after
    # creation. The final session.commit() performs the flush.
    return obj, True


def block(lesson, position, block_type, content):
    return LessonContentBlock(
        id=uuid4(),
        lesson_id=lesson.id,
        position=position,
        block_type=block_type,
        content=content,
    )


async def add_lesson(
    session,
    room,
    position,
    slug,
    title,
    description,
    blocks,
    question,
    options,
    correct_answer,
):
    lesson, created = await get_or_create(
        session,
        Lesson,
        room_id=room.id,
        slug=slug,
    )

    lesson.title = title
    lesson.description = description
    lesson.position = position
    lesson.status = LessonStatus.PUBLISHED
    lesson.access_override = LessonAccessOverride.FREE
    lesson.completion_rule = LessonCompletionRule.REQUIRED_PRACTICE
    lesson.environment_requirement_id = None

    if created:
        for i, (block_type, content) in enumerate(blocks):
            session.add(
                block(
                    lesson,
                    i,
                    block_type,
                    content,
                )
            )

    practice, practice_created = await get_or_create(
        session,
        Practice,
        title=f"{title} — Practice",
    )

    practice.description = (
        f"Practice for the lesson '{title}'. "
        "Complete the question before continuing."
    )
    practice.status = PracticeStatus.PUBLISHED
    practice.activity_mode = PracticeActivityMode.TEXT
    practice.environment_requirement_id = None

    if practice_created:
        activity = PracticeActivity(
            id=uuid4(),
            practice_id=practice.id,
            position=0,
            activity_type=PracticeActivityType.TEXT_QUESTION,
            title=question,
            instructions="Choose the correct answer.",
            required=True,
            evaluation_type=PracticeEvaluationType.MULTIPLE_CHOICE,
            environment_requirement_id=None,
            configuration={
                "options": options,
                "correct_answer": correct_answer,
            },
            guidance_policy={},
        )
        session.add(activity)

        session.add(
            LessonPractice(
                id=uuid4(),
                lesson_id=lesson.id,
                practice_id=practice.id,
                position=0,
                required=True,
            )
        )

    return lesson


async def seed():
    async with AsyncSessionLocal() as session:

        # ------------------------------------------------------------
        # LEARNING PATH
        # ------------------------------------------------------------

        path, _ = await get_or_create(
            session,
            LearningPath,
            slug="linux",
        )

        path.title = "Linux"
        path.description = (
            "Build practical Linux skills from the command line upward. "
            "Learn filesystem navigation, files, users, permissions, "
            "processes, networking, administration, and security."
        )
        path.status = LearningPathStatus.PUBLISHED
        path.position = 0

        # ------------------------------------------------------------
        # MODULE
        # ------------------------------------------------------------

        module, _ = await get_or_create(
            session,
            Module,
            learning_path_id=path.id,
            slug="linux-foundations",
        )

        module.title = "Linux Foundations"
        module.description = (
            "Learn the Linux operating-system concepts and command-line "
            "skills required for practical cybersecurity work."
        )
        module.status = ModuleStatus.PUBLISHED
        module.position = 0

        # ------------------------------------------------------------
        # ROOM
        # ------------------------------------------------------------

        room, _ = await get_or_create(
            session,
            Room,
            module_id=module.id,
            slug="linux-command-line-basics",
        )

        room.title = "Linux Command Line Basics"
        room.description = (
            "A practical introduction to the Linux shell, filesystem, "
            "files, directories, and basic command-line navigation."
        )
        room.status = RoomStatus.PUBLISHED
        room.position = 0
        room.access_level = RoomAccessLevel.FREE

        # ------------------------------------------------------------
        # LESSON 1
        # ------------------------------------------------------------

        await add_lesson(
            session,
            room,
            0,
            "linux-and-the-shell",
            "Linux and the Shell",
            "Understand Linux, the terminal, and the shell.",
            [
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "What is Linux?",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "Linux is an operating system widely used on "
                            "servers, security appliances, cloud systems, "
                            "development machines, and security laboratories. "
                            "In cybersecurity, Linux is important because many "
                            "security tools and servers are operated from the "
                            "command line."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "The Terminal",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "The terminal provides a text interface through "
                            "which you interact with the operating system. "
                            "Instead of clicking graphical controls, you type "
                            "commands and receive text output."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "The Shell",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "A shell interprets commands entered in the "
                            "terminal. Bash is one of the most common shells "
                            "on Linux systems."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "echo Hello, Linux!",
                    },
                ),
                (
                    LessonContentBlockType.TERMINAL_OUTPUT,
                    {
                        "text": "Hello, Linux!",
                    },
                ),
                (
                    LessonContentBlockType.CALLOUT,
                    {
                        "type": "important",
                        "title": "Cybersecurity connection",
                        "text": (
                            "Security analysts and penetration testers "
                            "frequently automate tasks through shell commands "
                            "and shell scripts."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Practice",
                        "level": 2,
                    },
                ),
            ],
            "Which component interprets commands entered by a user?",
            [
                "The shell",
                "The monitor",
                "The keyboard",
                "The filesystem",
            ],
            "The shell",
        )

        # ------------------------------------------------------------
        # LESSON 2
        # ------------------------------------------------------------

        await add_lesson(
            session,
            room,
            1,
            "navigating-the-filesystem",
            "Navigating the Linux Filesystem",
            "Learn how Linux organizes directories and how to move through them.",
            [
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "The Linux Filesystem",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "Linux organizes files and directories in a "
                            "hierarchical filesystem. The top of this hierarchy "
                            "is represented by the root directory, written as /."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Where Am I?",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "The pwd command prints the current working "
                            "directory."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "pwd",
                    },
                ),
                (
                    LessonContentBlockType.TERMINAL_OUTPUT,
                    {
                        "text": "/home/student",
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Listing a Directory",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "ls",
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "The ls command displays files and directories "
                            "inside the current directory."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Changing Directories",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "cd /tmp\npwd",
                    },
                ),
                (
                    LessonContentBlockType.TERMINAL_OUTPUT,
                    {
                        "text": "/tmp",
                    },
                ),
                (
                    LessonContentBlockType.CALLOUT,
                    {
                        "type": "warning",
                        "title": "Common mistake",
                        "text": (
                            "Remember that cd changes your current directory, "
                            "while ls only displays directory contents."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Practice",
                        "level": 2,
                    },
                ),
            ],
            "Which command displays the current working directory?",
            [
                "pwd",
                "cd",
                "ls",
                "cat",
            ],
            "pwd",
        )

        # ------------------------------------------------------------
        # LESSON 3
        # ------------------------------------------------------------

        await add_lesson(
            session,
            room,
            2,
            "files-and-directories",
            "Files and Directories",
            "Learn how to create, inspect, copy, move, and remove files.",
            [
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Creating a Directory",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "mkdir linux-lab",
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "mkdir creates a new directory. After creating "
                            "linux-lab, you can enter it with cd."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "cd linux-lab",
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Creating a File",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "touch notes.txt",
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "touch can create an empty file when the file "
                            "does not already exist."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Reading a File",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "cat notes.txt",
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Copying and Moving",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "cp notes.txt backup.txt\nmv backup.txt archive.txt",
                    },
                ),
                (
                    LessonContentBlockType.CALLOUT,
                    {
                        "type": "important",
                        "title": "Security connection",
                        "text": (
                            "Security investigations frequently involve "
                            "creating evidence copies, inspecting files, "
                            "and moving artifacts into analysis directories."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Practice",
                        "level": 2,
                    },
                ),
            ],
            "Which command creates a new directory?",
            [
                "mkdir",
                "touch",
                "cat",
                "mv",
            ],
            "mkdir",
        )

        # ------------------------------------------------------------
        # LESSON 4
        # ------------------------------------------------------------

        await add_lesson(
            session,
            room,
            3,
            "absolute-and-relative-paths",
            "Absolute and Relative Paths",
            "Understand how Linux represents file locations.",
            [
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Absolute Paths",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "An absolute path starts from the filesystem root. "
                            "For example, /home/student/notes.txt identifies "
                            "a specific location from the root of the filesystem."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "cat /home/student/notes.txt",
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Relative Paths",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "A relative path is interpreted from the current "
                            "working directory."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "cat notes.txt",
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Parent Directory",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "The special path .. represents the parent "
                            "directory. A single dot, ., represents the "
                            "current directory."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "cd ..\npwd",
                    },
                ),
                (
                    LessonContentBlockType.CALLOUT,
                    {
                        "type": "tip",
                        "title": "Remember",
                        "text": (
                            "Absolute paths begin from /. Relative paths begin "
                            "from your current working directory."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Practice",
                        "level": 2,
                    },
                ),
            ],
            "Which path is an absolute path?",
            [
                "/home/student/file.txt",
                "file.txt",
                "../file.txt",
                "./file.txt",
            ],
            "/home/student/file.txt",
        )

        # ------------------------------------------------------------
        # LESSON 5
        # ------------------------------------------------------------

        await add_lesson(
            session,
            room,
            4,
            "reading-command-help",
            "Reading Command Help",
            "Learn how to discover command usage without memorizing everything.",
            [
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Why Documentation Matters",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "Linux contains a large number of commands and "
                            "options. Cybersecurity practitioners should learn "
                            "how to read documentation instead of relying "
                            "entirely on memorization."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "The --help Option",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "ls --help",
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "Many commands provide a short usage summary "
                            "through the --help option."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Manual Pages",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "man ls",
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "The man command opens the manual page for a "
                            "command. Manual pages are one of the most useful "
                            "references available on a Linux system."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CALLOUT,
                    {
                        "type": "important",
                        "title": "Cybersecurity habit",
                        "text": (
                            "Before using an unfamiliar command in a real "
                            "environment, understand what it does and what "
                            "its options change."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Practice",
                        "level": 2,
                    },
                ),
            ],
            "Which command opens a manual page for another command?",
            [
                "man",
                "pwd",
                "mkdir",
                "touch",
            ],
            "man",
        )

        # ------------------------------------------------------------
        # LESSON 6
        # ------------------------------------------------------------

        await add_lesson(
            session,
            room,
            5,
            "command-line-workflow",
            "Building a Command-Line Workflow",
            "Combine basic Linux commands into a repeatable workflow.",
            [
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "A Practical Workflow",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "Effective command-line work is usually a sequence "
                            "of small, verifiable operations. First determine "
                            "where you are, inspect the directory, create or "
                            "select the required files, and verify the result."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "pwd\nls\nmkdir lab\ncd lab\ntouch evidence.txt\nls",
                    },
                ),
                (
                    LessonContentBlockType.TERMINAL_OUTPUT,
                    {
                        "text": (
                            "/home/student\n"
                            "lab\n"
                            "evidence.txt"
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Verify Your Work",
                        "level": 2,
                    },
                ),
                (
                    LessonContentBlockType.TEXT,
                    {
                        "text": (
                            "Verification is an important security habit. "
                            "Do not assume a command succeeded simply because "
                            "it was entered. Inspect the resulting state."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.CODE,
                    {
                        "language": "bash",
                        "code": "pwd\nls -la",
                    },
                ),
                (
                    LessonContentBlockType.CALLOUT,
                    {
                        "type": "important",
                        "title": "Security mindset",
                        "text": (
                            "A strong Linux workflow is deliberate: execute, "
                            "observe, verify, and only then continue."
                        ),
                    },
                ),
                (
                    LessonContentBlockType.HEADING,
                    {
                        "text": "Practice",
                        "level": 2,
                    },
                ),
            ],
            "What should you do after performing an important filesystem operation?",
            [
                "Verify the resulting state",
                "Immediately close the terminal",
                "Ignore the command output",
                "Delete the directory",
            ],
            "Verify the resulting state",
        )

        await session.commit()

        print()
        print("Linux learning content inserted successfully.")
        print()
        print("Learning Path : Linux")
        print("Module        : Linux Foundations")
        print("Room          : Linux Command Line Basics")
        print("Lessons       : 6")
        print("Practice      : 6")
        print("Status        : PUBLISHED")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
