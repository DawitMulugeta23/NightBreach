from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio

from sqlalchemy import delete

from app.db.session import AsyncSessionLocal
from app.domains.practice.service import PracticeService
from app.domains.progress.service import ProgressService
from app.models.lesson import Lesson, LessonStatus
from app.models.lesson_practice import LessonPractice
from app.models.learning_path import LearningPath, LearningPathStatus
from app.models.module import Module, ModuleStatus
from app.models.practice import Practice, PracticeStatus
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.progress import ProgressStatus
from app.models.room import Room, RoomAccessLevel, RoomStatus
from app.models.user import User



@pytest_asyncio.fixture(autouse=True)
async def cleanup_progress_test_data():
    yield

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(User).where(
                User.username.like("prog_%")
            )
        )
        await session.execute(
            delete(LearningPath).where(
                LearningPath.slug.like("progress-path-%")
            )
        )
        await session.commit()



async def create_user(session, prefix: str = "progress") -> User:
    user = User(
        id=uuid4(),
        email=f"{prefix}-{uuid4()}@example.com",
        username=f"prog_{uuid4().hex[:15]}",
        hashed_password="test-hash",
    )
    session.add(user)
    await session.flush()
    return user


async def create_learning_tree(
    session,
    *,
    required_activity: bool = True,
):
    path = LearningPath(
        id=uuid4(),
        slug=f"progress-path-{uuid4().hex[:10]}",
        title="Progress Test Path",
        description="Progress test path",
        status=LearningPathStatus.PUBLISHED,
        position=1,
    )

    module = Module(
        id=uuid4(),
        slug=f"progress-module-{uuid4().hex[:10]}",
        title="Progress Test Module",
        description="Progress test module",
        status=ModuleStatus.PUBLISHED,
        position=1,
    )

    room = Room(
        id=uuid4(),
        slug=f"progress-room-{uuid4().hex[:10]}",
        title="Progress Test Room",
        description="Progress test room",
        status=RoomStatus.PUBLISHED,
        position=1,
        access_level=RoomAccessLevel.FREE,
    )

    lesson = Lesson(
        id=uuid4(),
        slug=f"progress-lesson-{uuid4().hex[:10]}",
        title="Progress Test Lesson",
        description="Progress test lesson",
        position=1,
        status=LessonStatus.PUBLISHED,
    )

    practice = Practice(
        id=uuid4(),
        title="Progress Test Practice",
        description="Progress test practice",
        status=PracticeStatus.PUBLISHED,
    )

    activity = PracticeActivity(
        id=uuid4(),
        position=1,
        activity_type=PracticeActivityType.TEXT_QUESTION,
        title="Progress Test Activity",
        instructions="Answer the test question.",
        required=required_activity,
        evaluation_type=PracticeEvaluationType.TEXT_EXACT,
        configuration={"expected_answer": "Linux"},
        guidance_policy={},
    )

    lesson.lesson_practices.append(
        LessonPractice(
            id=uuid4(),
            position=1,
            required=True,
            practice=practice,
        )
    )
    practice.activities.append(activity)
    room.lessons.append(lesson)
    module.rooms.append(room)
    path.modules.append(module)

    session.add(path)
    await session.flush()

    return path, module, room, lesson, practice, activity


@pytest.mark.asyncio
async def test_successful_required_activity_completes_lesson():
    async with AsyncSessionLocal() as session:
        learner = await create_user(session, "progress-success")
        _, _, _, lesson, _, activity = await create_learning_tree(session)

        practice_service = PracticeService(session)

        attempt = await practice_service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        submitted = await practice_service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Linux",
        )

        assert submitted.result == "SUCCESS"

        progress_service = ProgressService(session)

        progress = await progress_service.get_lesson_progress(
            learner_id=learner.id,
            lesson_id=lesson.id,
        )

        assert progress is not None
        assert progress.status == ProgressStatus.COMPLETED
        assert progress.completed_at is not None

        await session.rollback()


@pytest.mark.asyncio
async def test_failed_activity_does_not_complete_lesson():
    async with AsyncSessionLocal() as session:
        learner = await create_user(session, "progress-failed")
        _, _, _, lesson, _, activity = await create_learning_tree(session)

        practice_service = PracticeService(session)

        attempt = await practice_service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        submitted = await practice_service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Windows",
        )

        assert submitted.result == "FAILED"

        progress_service = ProgressService(session)

        progress = await progress_service.get_lesson_progress(
            learner_id=learner.id,
            lesson_id=lesson.id,
        )

        assert progress is None

        await session.rollback()


@pytest.mark.asyncio
async def test_optional_activity_does_not_block_lesson_completion():
    async with AsyncSessionLocal() as session:
        learner = await create_user(session, "progress-optional")
        _, _, _, lesson, _, activity = await create_learning_tree(
            session,
            required_activity=False,
        )

        practice_service = PracticeService(session)

        attempt = await practice_service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        submitted = await practice_service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="anything",
        )

        assert submitted.result == "FAILED"

        progress_service = ProgressService(session)

        await progress_service.record_lesson_completion(
            learner_id=learner.id,
            lesson_id=lesson.id,
        )

        progress = await progress_service.get_lesson_progress(
            learner_id=learner.id,
            lesson_id=lesson.id,
        )

        assert progress is not None
        assert progress.status == ProgressStatus.COMPLETED

        await session.rollback()


@pytest.mark.asyncio
async def test_lesson_completion_propagates_to_room():
    async with AsyncSessionLocal() as session:
        learner = await create_user(session, "progress-room")
        _, _, room, lesson, _, activity = await create_learning_tree(session)

        practice_service = PracticeService(session)

        attempt = await practice_service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        await practice_service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Linux",
        )

        progress_service = ProgressService(session)

        lesson_progress = await progress_service.get_lesson_progress(
            learner_id=learner.id,
            lesson_id=lesson.id,
        )
        room_progress = await progress_service.get_room_progress(
            learner_id=learner.id,
            room_id=room.id,
        )

        assert lesson_progress is not None
        assert lesson_progress.status == ProgressStatus.COMPLETED
        assert room_progress is not None
        assert room_progress.status == ProgressStatus.COMPLETED

        await session.rollback()


@pytest.mark.asyncio
async def test_room_completion_propagates_to_module():
    async with AsyncSessionLocal() as session:
        learner = await create_user(session, "progress-module")
        _, module, room, lesson, _, activity = await create_learning_tree(session)

        practice_service = PracticeService(session)

        attempt = await practice_service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        await practice_service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Linux",
        )

        progress_service = ProgressService(session)

        module_progress = await progress_service.get_module_progress(
            learner_id=learner.id,
            module_id=module.id,
        )

        assert module_progress is not None
        assert module_progress.status == ProgressStatus.COMPLETED

        await session.rollback()


@pytest.mark.asyncio
async def test_module_completion_propagates_to_learning_path():
    async with AsyncSessionLocal() as session:
        learner = await create_user(session, "progress-path")
        path, _, _, _, _, activity = await create_learning_tree(session)

        practice_service = PracticeService(session)

        attempt = await practice_service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        await practice_service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Linux",
        )

        progress_service = ProgressService(session)

        path_progress = await progress_service.get_learning_path_progress(
            learner_id=learner.id,
            learning_path_id=path.id,
        )

        assert path_progress is not None
        assert path_progress.status == ProgressStatus.COMPLETED

        await session.rollback()


@pytest.mark.asyncio
async def test_progress_is_isolated_between_learners():
    async with AsyncSessionLocal() as session:
        learner_one = await create_user(session, "progress-owner")
        learner_two = await create_user(session, "progress-other")

        _, _, _, lesson, _, activity = await create_learning_tree(session)

        practice_service = PracticeService(session)

        attempt = await practice_service.start_attempt(
            activity_id=activity.id,
            learner_id=learner_one.id,
        )

        await practice_service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner_one.id,
            submission="Linux",
        )

        progress_service = ProgressService(session)

        owner_progress = await progress_service.get_lesson_progress(
            learner_id=learner_one.id,
            lesson_id=lesson.id,
        )
        other_progress = await progress_service.get_lesson_progress(
            learner_id=learner_two.id,
            lesson_id=lesson.id,
        )

        assert owner_progress is not None
        assert owner_progress.status == ProgressStatus.COMPLETED
        assert other_progress is None

        await session.rollback()


@pytest.mark.asyncio
async def test_completion_state_contains_entire_completed_hierarchy():
    async with AsyncSessionLocal() as session:
        learner = await create_user(session, "progress-state")
        path, module, room, lesson, _, activity = await create_learning_tree(
            session
        )

        practice_service = PracticeService(session)

        attempt = await practice_service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        await practice_service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Linux",
        )

        progress_service = ProgressService(session)

        state = await progress_service.get_completion_state(
            learner_id=learner.id,
            lesson_id=lesson.id,
        )

        assert state["lesson_id"] == lesson.id
        assert state["room_id"] == room.id
        assert state["module_id"] == module.id
        assert state["learning_path_id"] == path.id

        assert state["lesson_status"] == ProgressStatus.COMPLETED
        assert state["room_status"] == ProgressStatus.COMPLETED
        assert state["module_status"] == ProgressStatus.COMPLETED
        assert state["learning_path_status"] == ProgressStatus.COMPLETED

        await session.rollback()
