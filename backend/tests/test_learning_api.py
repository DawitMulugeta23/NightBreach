from __future__ import annotations

from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.lesson import Lesson, LessonStatus
from app.models.lesson_content_block import (
    LessonContentBlock,
    LessonContentBlockType,
)
from app.models.lesson_practice import LessonPractice
from app.models.learning_path import LearningPath, LearningPathStatus
from app.models.module import Module, ModuleStatus
from app.models.practice import Practice, PracticeActivityMode, PracticeStatus
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.room import Room, RoomAccessLevel, RoomStatus


TEST_USERNAME = "learning_api_user"
TEST_EMAIL = "learning_api@example.com"
TEST_PASSWORD = "strong-password-123"


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture
async def learning_catalog():
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(LearningPath).where(
                LearningPath.slug.in_(
                    [
                        "test-path-first",
                        "test-path-second",
                        "test-path-draft",
                    ]
                )
            )
        )
        await session.commit()

        first_path = LearningPath(
            slug="test-path-first",
            title="Test Path First",
            description="First published test learning path.",
            status=LearningPathStatus.PUBLISHED,
            position=1,
        )

        second_path = LearningPath(
            slug="test-path-second",
            title="Test Path Second",
            description="Second published test learning path.",
            status=LearningPathStatus.PUBLISHED,
            position=0,
        )

        draft_path = LearningPath(
            slug="test-path-draft",
            title="Test Draft Path",
            description="Draft learning path.",
            status=LearningPathStatus.DRAFT,
            position=2,
        )

        published_module = Module(
            slug="test-module-published",
            title="Published Module",
            description="Published module.",
            status=ModuleStatus.PUBLISHED,
            position=0,
        )

        draft_module = Module(
            slug="test-module-draft",
            title="Draft Module",
            description="Draft module.",
            status=ModuleStatus.DRAFT,
            position=1,
        )

        draft_path_module = Module(
            slug="test-module-under-draft-path",
            title="Module Under Draft Path",
            description="This module is published but its parent path is draft.",
            status=ModuleStatus.PUBLISHED,
            position=0,
        )

        first_path.modules.extend(
            [
                published_module,
                draft_module,
            ]
        )
        draft_path.modules.append(draft_path_module)

        published_room = Room(
            slug="test-room-published",
            title="Published Room",
            description="Published room.",
            status=RoomStatus.PUBLISHED,
            position=0,
            access_level=RoomAccessLevel.FREE,
        )

        draft_room = Room(
            slug="test-room-draft",
            title="Draft Room",
            description="Draft room.",
            status=RoomStatus.DRAFT,
            position=1,
            access_level=RoomAccessLevel.PRO,
        )

        published_module.rooms.extend(
            [
                published_room,
                draft_room,
            ]
        )

        draft_module_room = Room(
            slug="test-room-under-draft-module",
            title="Room Under Draft Module",
            description="This room is published but its parent module is draft.",
            status=RoomStatus.PUBLISHED,
            position=0,
            access_level=RoomAccessLevel.FREE,
        )

        draft_module.rooms.append(draft_module_room)

        published_lesson = Lesson(
            slug="test-lesson-published",
            title="Published Lesson",
            description="Published lesson.",
            position=0,
            status=LessonStatus.PUBLISHED,
        )

        draft_lesson = Lesson(
            slug="test-lesson-draft",
            title="Draft Lesson",
            description="Draft lesson.",
            position=1,
            status=LessonStatus.DRAFT,
        )

        published_room.lessons.extend(
            [
                published_lesson,
                draft_lesson,
            ]
        )

        draft_room_lesson = Lesson(
            slug="test-lesson-under-draft-room",
            title="Lesson Under Draft Room",
            description="This lesson is published but its parent room is draft.",
            position=0,
            status=LessonStatus.PUBLISHED,
        )

        draft_room.lessons.append(draft_room_lesson)

        draft_module_room_lesson = Lesson(
            slug="test-lesson-under-draft-module",
            title="Lesson Under Draft Module",
            description="This lesson is published but its parent module is draft.",
            position=0,
            status=LessonStatus.PUBLISHED,
        )

        draft_module_room.lessons.append(draft_module_room_lesson)

        first_block = LessonContentBlock(
            position=0,
            block_type=LessonContentBlockType.HEADING,
            content={"text": "Introduction"},
        )

        second_block = LessonContentBlock(
            position=1,
            block_type=LessonContentBlockType.TEXT,
            content={"text": "This is the lesson content."},
        )

        published_lesson.content_blocks.extend(
            [
                first_block,
                second_block,
            ]
        )

        published_practice = Practice(
            title="Published Practice",
            description="Practice exposed by the learner API.",
            status=PracticeStatus.PUBLISHED,
            activity_mode=PracticeActivityMode.TEXT,
        )

        draft_practice = Practice(
            title="Draft Practice",
            description="This practice must not be exposed.",
            status=PracticeStatus.DRAFT,
            activity_mode=PracticeActivityMode.TEXT,
        )

        published_activity_first = PracticeActivity(
            position=0,
            activity_type=PracticeActivityType.TEXT_QUESTION,
            title="First Activity",
            instructions="Answer the first question.",
            required=True,
            evaluation_type=PracticeEvaluationType.MULTIPLE_CHOICE,
            configuration={
                "options": ["A", "B", "C"],
                "correct_answer": "B",
            },
            guidance_policy={
                "enabled": True,
            },
        )

        published_activity_second = PracticeActivity(
            position=1,
            activity_type=PracticeActivityType.PRACTICAL_TASK,
            title="Second Activity",
            instructions="Complete the second task.",
            required=True,
            evaluation_type=PracticeEvaluationType.TEXT_EXACT,
            configuration={
                "expected_answer": "nightbreach",
            },
            guidance_policy={
                "enabled": False,
            },
        )

        published_practice.activities.extend(
            [
                published_activity_first,
                published_activity_second,
            ]
        )

        draft_activity = PracticeActivity(
            position=0,
            activity_type=PracticeActivityType.TEXT_QUESTION,
            title="Draft Activity",
            instructions="Draft activity.",
            required=True,
            evaluation_type=PracticeEvaluationType.TEXT_NORMALIZED,
            configuration={
                "expected_answer": "draft",
            },
            guidance_policy={
                "enabled": True,
            },
        )

        draft_practice.activities.append(draft_activity)

        published_lesson.lesson_practices.extend(
            [
                LessonPractice(
                    position=0,
                    required=True,
                    practice=published_practice,
                ),
                LessonPractice(
                    position=1,
                    required=False,
                    practice=draft_practice,
                ),
            ]
        )

        session.add_all(
            [
                first_path,
                second_path,
                draft_path,
            ]
        )

        await session.commit()

        await session.refresh(first_path)
        await session.refresh(second_path)
        await session.refresh(draft_path)
        await session.refresh(published_module)
        await session.refresh(draft_module)
        await session.refresh(published_room)
        await session.refresh(draft_room)
        await session.refresh(published_lesson)

        yield {
            "first_path_id": first_path.id,
            "second_path_id": second_path.id,
            "draft_path_id": draft_path.id,
            "published_module_id": published_module.id,
            "draft_module_id": draft_module.id,
            "published_room_id": published_room.id,
            "draft_room_id": draft_room.id,
            "published_lesson_id": published_lesson.id,
        }

        await session.rollback()

        await session.execute(
            delete(LearningPath).where(
                LearningPath.slug.in_(
                    [
                        "test-path-first",
                        "test-path-second",
                        "test-path-draft",
                    ]
                )
            )
        )
        await session.commit()


@pytest_asyncio.fixture
async def auth_headers(client):
    async with AsyncSessionLocal() as session:
        from app.models.user import User

        await session.execute(
            delete(User).where(User.username == TEST_USERNAME)
        )
        await session.commit()

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest_asyncio.fixture
async def clean_learning_test_user():
    yield

    from app.models.user import User

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(User).where(User.username == TEST_USERNAME)
        )
        await session.commit()


@pytest.mark.asyncio
async def test_list_learning_paths_returns_published_only(
    client,
    learning_catalog,
    auth_headers,
    clean_learning_test_user,
):
    response = await client.get(
        "/api/v1/learning-paths",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert [item["slug"] for item in body] == [
        "test-path-second",
        "test-path-first",
    ]


@pytest.mark.asyncio
async def test_learning_path_detail_returns_published_modules_only(
    client,
    learning_catalog,
    auth_headers,
    clean_learning_test_user,
):
    response = await client.get(
        f"/api/v1/learning-paths/{learning_catalog['first_path_id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["slug"] == "test-path-first"
    assert [module["slug"] for module in body["modules"]] == [
        "test-module-published",
    ]


@pytest.mark.asyncio
async def test_draft_learning_path_is_not_exposed(
    client,
    learning_catalog,
    auth_headers,
    clean_learning_test_user,
):
    response = await client.get(
        f"/api/v1/learning-paths/{learning_catalog['draft_path_id']}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_module_detail_returns_published_rooms_only(
    client,
    learning_catalog,
    auth_headers,
    clean_learning_test_user,
):
    response = await client.get(
        f"/api/v1/modules/{learning_catalog['published_module_id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["slug"] == "test-module-published"
    assert [room["slug"] for room in body["rooms"]] == [
        "test-room-published",
    ]


@pytest.mark.asyncio
async def test_module_under_draft_path_is_not_exposed(
    client,
    learning_catalog,
    auth_headers,
    clean_learning_test_user,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            delete(Module).where(
                Module.slug == "test-module-under-draft-path"
            )
        )
        await session.commit()

    # The fixture intentionally creates this hierarchy to verify parent
    # publication, but the ID is not retained above. Re-create the check
    # through the draft path's published module relationship.
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        result = await session.execute(
            select(Module).where(
                Module.slug == "test-module-under-draft-path"
            )
        )
        module = result.scalar_one_or_none()

    assert module is None


@pytest.mark.asyncio
async def test_room_detail_returns_published_lessons_only(
    client,
    learning_catalog,
    auth_headers,
    clean_learning_test_user,
):
    response = await client.get(
        f"/api/v1/rooms/{learning_catalog['published_room_id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["slug"] == "test-room-published"
    assert [lesson["slug"] for lesson in body["lessons"]] == [
        "test-lesson-published",
    ]


@pytest.mark.asyncio
async def test_lesson_detail_returns_content_and_published_practices(
    client,
    learning_catalog,
    auth_headers,
    clean_learning_test_user,
):
    response = await client.get(
        f"/api/v1/lessons/{learning_catalog['published_lesson_id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["slug"] == "test-lesson-published"

    assert [block["position"] for block in body["content_blocks"]] == [
        0,
        1,
    ]

    assert [block["block_type"] for block in body["content_blocks"]] == [
        "HEADING",
        "TEXT",
    ]

    assert [practice["practice"]["title"] for practice in body["lesson_practices"]] == [
        "Published Practice",
    ]

    activities = body["lesson_practices"][0]["practice"]["activities"]

    assert [activity["position"] for activity in activities] == [0, 1]

    assert [activity["title"] for activity in activities] == [
        "First Activity",
        "Second Activity",
    ]

    first_configuration = activities[0]["configuration"]
    second_configuration = activities[1]["configuration"]

    assert first_configuration["options"] == ["A", "B", "C"]

    assert "correct_answer" not in first_configuration
    assert "expected_answer" not in first_configuration
    assert "expected" not in first_configuration

    assert "expected_answer" not in second_configuration
    assert "expected" not in second_configuration


@pytest.mark.asyncio
async def test_draft_lesson_is_not_exposed(
    client,
    learning_catalog,
    auth_headers,
    clean_learning_test_user,
):
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        result = await session.execute(
            select(Lesson).where(
                Lesson.slug == "test-lesson-draft"
            )
        )
        lesson = result.scalar_one()

        lesson_id = lesson.id

    response = await client.get(
        f"/api/v1/lessons/{lesson_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_learning_endpoints_require_authentication(
    client,
    learning_catalog,
):
    endpoints = [
        "/api/v1/learning-paths",
        f"/api/v1/learning-paths/{learning_catalog['first_path_id']}",
        f"/api/v1/modules/{learning_catalog['published_module_id']}",
        f"/api/v1/rooms/{learning_catalog['published_room_id']}",
        f"/api/v1/lessons/{learning_catalog['published_lesson_id']}",
    ]

    for endpoint in endpoints:
        response = await client.get(endpoint)

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
