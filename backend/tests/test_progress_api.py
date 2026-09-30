from __future__ import annotations

from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.models.lesson_practice import LessonPractice
from app.models.practice_activity import PracticeActivity
from app.models.practice_attempt import PracticeAttempt
from app.models.progress import (
    LearnerLessonProgress,
    LearnerLearningPathProgress,
    LearnerModuleProgress,
    LearnerRoomProgress,
)

pytest_plugins = ("tests.test_learning_api",)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_progress_api_data():
    yield

    async with AsyncSessionLocal() as session:
        await session.execute(delete(PracticeAttempt))
        await session.execute(delete(LearnerLessonProgress))
        await session.execute(delete(LearnerRoomProgress))
        await session.execute(delete(LearnerModuleProgress))
        await session.execute(delete(LearnerLearningPathProgress))
        await session.commit()


async def get_catalog_activities(lesson_id: UUID):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PracticeActivity)
            .join(
                LessonPractice,
                LessonPractice.practice_id == PracticeActivity.practice_id,
            )
            .where(
                LessonPractice.lesson_id == lesson_id,
                LessonPractice.required.is_(True),
            )
            .order_by(PracticeActivity.position)
        )
        return list(result.scalars().all())


@pytest.mark.asyncio
async def test_progress_endpoints_require_authentication(
    client,
    learning_catalog,
):
    lesson_id = learning_catalog["published_lesson_id"]

    response = await client.get(
        f"/api/v1/progress/lessons/{lesson_id}"
    )

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_progress_returns_none_before_completion(
    client,
    learning_catalog,
    auth_headers,
):
    lesson_id = learning_catalog["published_lesson_id"]

    response = await client.get(
        f"/api/v1/progress/lessons/{lesson_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_completion_state_returns_not_started_hierarchy(
    client,
    learning_catalog,
    auth_headers,
):
    lesson_id = learning_catalog["published_lesson_id"]

    response = await client.get(
        f"/api/v1/progress/lessons/{lesson_id}/completion-state",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["lesson_id"] == str(lesson_id)
    assert data["room_id"] == str(learning_catalog["published_room_id"])
    assert data["module_id"] == str(learning_catalog["published_module_id"])
    assert data["learning_path_id"] == str(
        learning_catalog["first_path_id"]
    )

    assert data["lesson_status"] == "NOT_STARTED"
    assert data["room_status"] == "NOT_STARTED"
    assert data["module_status"] == "NOT_STARTED"
    assert data["learning_path_status"] == "NOT_STARTED"


@pytest.mark.asyncio
async def test_complete_lesson_rejects_incomplete_requirements(
    client,
    learning_catalog,
    auth_headers,
):
    lesson_id = learning_catalog["published_lesson_id"]

    response = await client.post(
        f"/api/v1/progress/lessons/{lesson_id}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 422

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "message" in data["error"]


@pytest.mark.asyncio
async def test_completed_rooms_and_modules_are_empty_initially(
    client,
    learning_catalog,
    auth_headers,
):
    room_id = learning_catalog["published_room_id"]
    module_id = learning_catalog["published_module_id"]

    room_response = await client.get(
        "/api/v1/progress/completed/rooms",
        headers=auth_headers,
        params={"module_id": str(module_id)},
    )

    assert room_response.status_code == 200
    assert room_response.json() == []

    module_response = await client.get(
        "/api/v1/progress/completed/modules",
        headers=auth_headers,
        params={"learning_path_id": str(learning_catalog["first_path_id"])},
    )

    assert module_response.status_code == 200
    assert module_response.json() == []


@pytest.mark.asyncio
async def test_successful_practice_submission_does_not_complete_lesson_yet(
    client,
    learning_catalog,
    auth_headers,
):
    lesson_id = learning_catalog["published_lesson_id"]
    activities = await get_catalog_activities(lesson_id)

    assert len(activities) == 2

    first_activity = activities[0]

    attempt_response = await client.post(
        f"/api/v1/practice/activities/{first_activity.id}/attempts",
        headers=auth_headers,
        json={},
    )

    assert attempt_response.status_code in (200, 201)

    attempt = attempt_response.json()

    submit_response = await client.post(
        f"/api/v1/practice/attempts/{attempt['id']}/submit",
        headers=auth_headers,
        json={"submission": "B"},
    )

    assert submit_response.status_code == 200, submit_response.text

    progress_response = await client.get(
        f"/api/v1/progress/lessons/{lesson_id}",
        headers=auth_headers,
    )

    assert progress_response.status_code == 200
    assert progress_response.json() is None


@pytest.mark.asyncio
async def test_successful_required_activities_complete_entire_hierarchy(
    client,
    learning_catalog,
    auth_headers,
):
    lesson_id = learning_catalog["published_lesson_id"]

    activities = await get_catalog_activities(lesson_id)

    assert len(activities) == 2

    first_activity = activities[0]
    second_activity = activities[1]

    # First required activity.
    attempt_response = await client.post(
        f"/api/v1/practice/activities/{first_activity.id}/attempts",
        headers=auth_headers,
        json={},
    )

    assert attempt_response.status_code in (200, 201)

    first_attempt = attempt_response.json()

    submit_response = await client.post(
        f"/api/v1/practice/attempts/{first_attempt['id']}/submit",
        headers=auth_headers,
        json={"submission": "B"},
    )

    assert submit_response.status_code == 200, submit_response.text

    progress_response = await client.get(
        f"/api/v1/progress/lessons/{lesson_id}",
        headers=auth_headers,
    )

    assert progress_response.status_code == 200
    assert progress_response.json() is None

    # Second required activity.
    attempt_response = await client.post(
        f"/api/v1/practice/activities/{second_activity.id}/attempts",
        headers=auth_headers,
        json={},
    )

    assert attempt_response.status_code in (200, 201)

    second_attempt = attempt_response.json()

    submit_response = await client.post(
        f"/api/v1/practice/attempts/{second_attempt['id']}/submit",
        headers=auth_headers,
        json={"submission": "nightbreach"},
    )

    assert submit_response.status_code == 200, submit_response.text

    # Lesson should now be complete.
    lesson_response = await client.get(
        f"/api/v1/progress/lessons/{lesson_id}",
        headers=auth_headers,
    )

    assert lesson_response.status_code == 200

    lesson_progress = lesson_response.json()

    assert lesson_progress["lesson_id"] == str(lesson_id)
    assert lesson_progress["status"] == "COMPLETED"
    assert lesson_progress["completed_at"] is not None

    # Completion should propagate to room.
    room_response = await client.get(
        f"/api/v1/progress/rooms/{learning_catalog['published_room_id']}",
        headers=auth_headers,
    )

    assert room_response.status_code == 200
    assert room_response.json()["status"] == "COMPLETED"

    # Completion should propagate to module.
    module_response = await client.get(
        f"/api/v1/progress/modules/{learning_catalog['published_module_id']}",
        headers=auth_headers,
    )

    assert module_response.status_code == 200
    assert module_response.json()["status"] == "COMPLETED"

    # Completion should propagate to learning path.
    path_response = await client.get(
        f"/api/v1/progress/learning-paths/{learning_catalog['first_path_id']}",
        headers=auth_headers,
    )

    assert path_response.status_code == 200
    assert path_response.json()["status"] == "COMPLETED"

    # Completion state should show the entire hierarchy.
    state_response = await client.get(
        f"/api/v1/progress/lessons/{lesson_id}/completion-state",
        headers=auth_headers,
    )

    assert state_response.status_code == 200

    state = state_response.json()

    assert state["lesson_status"] == "COMPLETED"
    assert state["room_status"] == "COMPLETED"
    assert state["module_status"] == "COMPLETED"
    assert state["learning_path_status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_completed_rooms_and_modules_are_listed(
    client,
    learning_catalog,
    auth_headers,
):
    lesson_id = learning_catalog["published_lesson_id"]

    activities = await get_catalog_activities(lesson_id)

    assert len(activities) == 2

    for activity, answer in (
        (activities[0], "B"),
        (activities[1], "nightbreach"),
    ):
        attempt_response = await client.post(
            f"/api/v1/practice/activities/{activity.id}/attempts",
            headers=auth_headers,
            json={},
        )

        assert attempt_response.status_code in (200, 201)

        attempt = attempt_response.json()

        submit_response = await client.post(
            f"/api/v1/practice/attempts/{attempt['id']}/submit",
            headers=auth_headers,
            json={"submission": answer},
        )

        assert submit_response.status_code == 200, submit_response.text

    room_response = await client.get(
        "/api/v1/progress/completed/rooms",
        headers=auth_headers,
        params={
            "module_id": str(learning_catalog["published_module_id"]),
        },
    )

    assert room_response.status_code == 200

    rooms = room_response.json()

    assert len(rooms) == 1
    assert rooms[0]["room_id"] == str(
        learning_catalog["published_room_id"]
    )
    assert rooms[0]["status"] == "COMPLETED"

    module_response = await client.get(
        "/api/v1/progress/completed/modules",
        headers=auth_headers,
        params={
            "learning_path_id": str(learning_catalog["first_path_id"]),
        },
    )

    assert module_response.status_code == 200

    modules = module_response.json()

    assert len(modules) == 1
    assert modules[0]["module_id"] == str(
        learning_catalog["published_module_id"]
    )
    assert modules[0]["status"] == "COMPLETED"
