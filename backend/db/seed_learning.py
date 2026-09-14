"""
Seeds the Learning Paths hierarchy: Paths → Rooms → Lessons → Questions.
Idempotent — re-running updates existing rows by slug/title.
"""
import asyncio
import hashlib
import uuid

from sqlalchemy import select

from db.session import AsyncSessionLocal
from db.models import (
    LearningPath, Room, Lesson, LessonQuestion, QuestionType,
)


def _hash_answer(answer: str) -> str:
    return hashlib.sha256(answer.strip().lower().encode()).hexdigest()


SEED_DATA = [
    # ============ 1. LINUX FUNDAMENTALS ============
    {
        "slug": "linux-fundamentals",
        "title": "Linux Fundamentals",
        "description": "Master the Linux command line from first principles.",
        "icon": "/linuxlogo.jpeg",
        "order_index": 1,
        "rooms": [
            {
                "order_index": 1,
                "title": "Getting Started",
                "description": "Your first steps in the Linux terminal.",
                "lessons": [
                    {
                        "order_index": 1,
                        "title": "Linux History & OS/Kernel",
                        "blocks": [
                            {"type": "text", "heading": "What is Linux?", "body": "Linux is a family of open-source operating systems built around the Linux kernel, first released by Linus Torvalds in 1991. Unlike Windows or macOS, Linux is distributed as many 'distributions' (Ubuntu, Fedora, Debian, Arch) that share the same kernel but differ in packaging and defaults."},
                            {"type": "text", "heading": "Kernel vs Operating System", "body": "The kernel is the core program that talks to the hardware. The operating system is the kernel plus all the user-space tools (shell, utilities, package manager). When people say 'Linux', they usually mean a full distribution, not just the kernel."},
                        ],
                        "questions": [
                            {"order_index": 1, "question_type": "text", "prompt": "In what year did Linus Torvalds first release the Linux kernel?", "answer": "1991"},
                        ],
                    },
                    {
                        "order_index": 2,
                        "title": "The whoami Command",
                        "blocks": [
                            {"type": "text", "heading": "whoami — Who Am I?", "body": "The whoami command prints the username of the account you are currently logged in as. It takes no arguments and always returns exactly one line: your username."},
                            {"type": "text", "heading": "Why It Matters", "body": "In security work, knowing exactly which user you are is critical. Running a command as root vs a regular user has drastically different consequences."},
                            {"type": "practice", "command": "whoami", "instructions": "Start the machine and run whoami in the terminal. Note the exact output — you'll be asked for it below."},
                        ],
                        "questions": [
                            {"order_index": 1, "question_type": "terminal", "prompt": "Run whoami in the terminal. What is the exact output?", "answer": "{username}", "setup_script": "echo 'whoami' > /tmp/hint.txt"},
                        ],
                    },
                    {
                        "order_index": 3,
                        "title": "The pwd Command",
                        "blocks": [
                            {"type": "text", "heading": "pwd — Print Working Directory", "body": "The pwd command prints the absolute path of the directory you are currently in."},
                            {"type": "practice", "command": "pwd", "instructions": "Run pwd in the terminal. It should print your home directory path."},
                        ],
                        "questions": [
                            {"order_index": 1, "question_type": "text", "prompt": "What character does every absolute path in Linux start with?", "answer": "/"},
                            {"order_index": 2, "question_type": "terminal", "prompt": "Run pwd in the terminal. Paste the full output.", "answer": "/home/{username}"},
                        ],
                    },
                ],
            },
            {
                "order_index": 2,
                "title": "File System Navigation",
                "description": "Move around the Linux file system with confidence.",
                "lessons": [
                    {
                        "order_index": 1,
                        "title": "Understanding Paths",
                        "blocks": [
                            {"type": "text", "heading": "Absolute vs Relative Paths", "body": "An absolute path starts with / and describes the location from the root of the filesystem. A relative path is interpreted from your current working directory."},
                            {"type": "practice", "command": "ls /", "instructions": "Run ls / to see the top-level directories of the Linux filesystem."},
                        ],
                        "questions": [
                            {"order_index": 1, "question_type": "text", "prompt": "What character does every absolute path in Linux start with?", "answer": "/"},
                        ],
                    },
                ],
            },
        ],
    },

    # ============ 2. NETWORKING FUNDAMENTALS (placeholder) ============
    {
        "slug": "networking-fundamentals",
        "title": "Networking Fundamentals",
        "description": "Understand TCP/IP, subnetting, VLANs, routing, and essential protocols.",
        "icon": "/Networking.jpg",
        "order_index": 2,
        "rooms": [],
    },

    # ============ 3. CYBER SECURITY (placeholder) ============
    {
        "slug": "fundamental-cybersecurity",
        "title": "Cyber Security",
        "description": "Core principles of information security, risk management, and threat landscapes.",
        "icon": "/fundamentalCybersecurity.jpeg",
        "order_index": 3,
        "rooms": [],
    },

    # ============ 4. DEFENSIVE SECURITY (placeholder) ============
    {
        "slug": "defensive-security",
        "title": "Defensive Security",
        "description": "Learn to detect, prevent, and mitigate attacks and harden systems.",
        "icon": "/defensive.jpeg",
        "order_index": 4,
        "rooms": [],
    },

    # ============ 5. OFFENSIVE SECURITY (placeholder) ============
    {
        "slug": "offensive-security",
        "title": "Offensive Security",
        "description": "Understand ethical hacking techniques, vulnerability exploitation, and post-exploitation.",
        "icon": "/offensive.jpeg",
        "order_index": 5,
        "rooms": [],
    },

    # ============ 6. WEB APPLICATION HACKING (placeholder) ============
    {
        "slug": "web-app-hacking",
        "title": "Web Application Hacking",
        "description": "Analyze and exploit OWASP Top 10 web vulnerabilities and tackle complex labs.",
        "icon": "/webapppentest.jpg",
        "order_index": 6,
        "rooms": [],
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        for path_data in SEED_DATA:
            result = await db.execute(
                select(LearningPath).where(LearningPath.slug == path_data["slug"])
            )
            path = result.scalar_one_or_none()

            if path is None:
                path = LearningPath(
                    id=uuid.uuid4(),
                    slug=path_data["slug"],
                    title=path_data["title"],
                    description=path_data["description"],
                    icon=path_data.get("icon"),
                    order_index=path_data["order_index"],
                )
                db.add(path)
                await db.flush()
                print(f"Created path: {path.title}")
            else:
                path.title = path_data["title"]
                path.description = path_data["description"]
                path.icon = path_data.get("icon")
                path.order_index = path_data["order_index"]
                print(f"Updated path: {path.title}")

            for room_data in path_data["rooms"]:
                result = await db.execute(
                    select(Room)
                    .where(Room.path_id == path.id)
                    .where(Room.order_index == room_data["order_index"])
                )
                room = result.scalar_one_or_none()

                if room is None:
                    room = Room(
                        id=uuid.uuid4(),
                        path_id=path.id,
                        order_index=room_data["order_index"],
                        title=room_data["title"],
                        description=room_data["description"],
                    )
                    db.add(room)
                    await db.flush()
                    print(f"  Created room: {room.title}")
                else:
                    room.title = room_data["title"]
                    room.description = room_data["description"]
                    print(f"  Updated room: {room.title}")

                for lesson_data in room_data["lessons"]:
                    result = await db.execute(
                        select(Lesson)
                        .where(Lesson.room_id == room.id)
                        .where(Lesson.order_index == lesson_data["order_index"])
                    )
                    lesson = result.scalar_one_or_none()

                    if lesson is None:
                        lesson = Lesson(
                            id=uuid.uuid4(),
                            room_id=room.id,
                            order_index=lesson_data["order_index"],
                            title=lesson_data["title"],
                            blocks=lesson_data["blocks"],
                        )
                        db.add(lesson)
                        await db.flush()
                        print(f"    Created lesson: {lesson.title}")
                    else:
                        lesson.title = lesson_data["title"]
                        lesson.blocks = lesson_data["blocks"]
                        print(f"    Updated lesson: {lesson.title}")

                    for q_data in lesson_data.get("questions", []):
                        result = await db.execute(
                            select(LessonQuestion)
                            .where(LessonQuestion.lesson_id == lesson.id)
                            .where(LessonQuestion.order_index == q_data["order_index"])
                        )
                        question = result.scalar_one_or_none()

                        if question is None:
                            question = LessonQuestion(
                                id=uuid.uuid4(),
                                lesson_id=lesson.id,
                                order_index=q_data["order_index"],
                                question_type=QuestionType(q_data["question_type"]),
                                prompt=q_data["prompt"],
                                answer_hash=_hash_answer(q_data["answer"]),
                                setup_script=q_data.get("setup_script"),
                            )
                            db.add(question)
                            print(f"      Created question #{q_data['order_index']}")
                        else:
                            question.prompt = q_data["prompt"]
                            question.answer_hash = _hash_answer(q_data["answer"])
                            question.setup_script = q_data.get("setup_script")
                            print(f"      Updated question #{q_data['order_index']}")

        await db.commit()
        print("\n✅ Learning paths seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed())
