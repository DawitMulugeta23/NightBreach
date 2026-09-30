from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.practice import Practice, PracticeActivityMode, PracticeStatus
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.practice_attempt import PracticeAttempt
from app.models.user import User
from app.models.ctf_challenge import (
    CTFChallenge,
    CTFChallengeGroup,
    CTFChallengeMode,
    CTFChallengeStatus,
    CTFChallengeType,
)
from app.models.ctf_attempt import CTFAttempt
from app.models.ctf_submission import CTFSubmission


TEST_USERNAME = "practice_api_user"
TEST_EMAIL = "practice_api@example.com"
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
async def auth_headers(client):
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(
            select(User.id).where(User.username == TEST_USERNAME)
        )
        user_id = user_result.scalar_one_or_none()

        if user_id is not None:
            attempt_result = await session.execute(
                select(CTFAttempt.id).where(
                    CTFAttempt.learner_id == user_id
                )
            )
            attempt_ids = list(attempt_result.scalars().all())

            if attempt_ids:
                await session.execute(
                    delete(CTFSubmission).where(
                        CTFSubmission.attempt_id.in_(attempt_ids)
                    )
                )

                await session.execute(
                    delete(CTFAttempt).where(
                        CTFAttempt.id.in_(attempt_ids)
                    )
                )

            await session.execute(
                delete(User).where(User.id == user_id)
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
        return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def practice_activities():
    async with AsyncSessionLocal() as session:
        published_practice = Practice(
            title=f"Published API Practice {uuid4()}",
            description="Published practice for API tests.",
            status=PracticeStatus.PUBLISHED,
            activity_mode=PracticeActivityMode.TEXT,
        )

        draft_practice = Practice(
            title=f"Draft API Practice {uuid4()}",
            description="Draft practice for API tests.",
            status=PracticeStatus.DRAFT,
            activity_mode=PracticeActivityMode.TEXT,
        )

        published_activity = PracticeActivity(
            position=0,
            activity_type=PracticeActivityType.TEXT_QUESTION,
            title="API Test Activity",
            instructions="Answer the question.",
            required=True,
            evaluation_type=PracticeEvaluationType.TEXT_EXACT,
            configuration={
                "expected_answer": "Linux",
            },
            guidance_policy={},
        )

        draft_activity = PracticeActivity(
            position=0,
            activity_type=PracticeActivityType.TEXT_QUESTION,
            title="Draft API Activity",
            instructions="This must not be executable.",
            required=True,
            evaluation_type=PracticeEvaluationType.TEXT_EXACT,
            configuration={
                "expected_answer": "Linux",
            },
            guidance_policy={},
        )

        published_practice.activities.append(published_activity)
        draft_practice.activities.append(draft_activity)

        session.add_all([
            published_practice,
            draft_practice,
        ])

        await session.commit()

        await session.refresh(published_activity)
        await session.refresh(draft_activity)

        yield {
            "published_activity_id": published_activity.id,
            "draft_activity_id": draft_activity.id,
        }

        await session.rollback()


@pytest_asyncio.fixture
async def guided_ctf_practice_activity():
    async with AsyncSessionLocal() as session:
        group = CTFChallengeGroup(
            code=f"practice-api-{uuid4().hex[:10]}",
            name="Practice API Guided CTF Group",
            description="Guided CTF group used by Practice API tests.",
            position=1,
        )

        challenge = CTFChallenge(
            slug=f"practice-api-ctf-{uuid4().hex}",
            title="Practice API Guided CTF",
            description="Guided CTF challenge for Practice API tests.",
            objective="Submit the test flag.",
            scenario="A controlled guided CTF scenario.",
            difficulty="easy",
            mode=CTFChallengeMode.GUIDED,
            status=CTFChallengeStatus.PUBLISHED,
            challenge_type=CTFChallengeType.FLAG,
            validation_config={
                "expected_flag": "NB{practice-api-flag}",
                "comparison": "exact",
            },
        )

        group.challenges.append(challenge)

        session.add(group)
        await session.flush()

        practice = Practice(
            title=f"Guided CTF API Practice {uuid4()}",
            description="Practice containing a guided CTF activity.",
            status=PracticeStatus.PUBLISHED,
            activity_mode=PracticeActivityMode.GUIDED_CTF,
        )

        activity = PracticeActivity(
            position=0,
            activity_type=PracticeActivityType.GUIDED_CTF,
            title="Guided CTF API Activity",
            instructions="Complete the linked CTF challenge.",
            required=True,
            evaluation_type=PracticeEvaluationType.FLAG_SUBMISSION,
            configuration={
                "challenge_id": str(challenge.id),
            },
            guidance_policy={},
        )

        practice.activities.append(activity)
        session.add(practice)

        await session.commit()

        await session.refresh(challenge)
        await session.refresh(activity)

        yield {
            "activity_id": activity.id,
            "challenge_id": challenge.id,
        }

        attempt_result = await session.execute(
            select(CTFAttempt.id).where(
                CTFAttempt.challenge_id == challenge.id
            )
        )
        attempt_ids = list(attempt_result.scalars().all())

        if attempt_ids:
            await session.execute(
                delete(CTFSubmission).where(
                    CTFSubmission.attempt_id.in_(attempt_ids)
                )
            )

            await session.execute(
                delete(CTFAttempt).where(
                    CTFAttempt.id.in_(attempt_ids)
                )
            )

        await session.delete(practice)
        await session.delete(challenge)
        await session.delete(group)
        await session.commit()


@pytest.mark.asyncio
async def test_start_guided_ctf_attempt_creates_linked_ctf_attempt(
    client,
    auth_headers,
    guided_ctf_practice_activity,
):
    environment_id = uuid4()
    session_id = f"practice-api-session-{uuid4().hex}"

    response = await client.post(
        f"/api/v1/practice/activities/"
        f"{guided_ctf_practice_activity['activity_id']}/attempts",
        headers=auth_headers,
        json={
            "environment_id": str(environment_id),
            "session_id": session_id,
        },
    )

    assert response.status_code == 201, response.text

    body = response.json()

    assert body["practice_activity_id"] == str(
        guided_ctf_practice_activity["activity_id"]
    )
    assert body["attempt_no"] == 1
    assert body["ctf_attempt_id"]

    async with AsyncSessionLocal() as session:
        ctf_attempt = await session.get(
            CTFAttempt,
            body["ctf_attempt_id"],
        )

        assert ctf_attempt is not None
        assert ctf_attempt.challenge_id == (
            guided_ctf_practice_activity["challenge_id"]
        )
        assert ctf_attempt.environment_id == environment_id
        assert ctf_attempt.session_id == session_id
        assert ctf_attempt.attempt_number == 1


@pytest.mark.asyncio
async def test_start_attempt_creates_first_attempt(
    client,
    auth_headers,
    practice_activities,
):
    response = await client.post(
        f"/api/v1/practice/activities/"
        f"{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["practice_activity_id"] == str(
        practice_activities["published_activity_id"]
    )
    assert body["attempt_no"] == 1
    assert body["id"]
    assert body["started_at"]
    assert "learner_id" not in body


@pytest.mark.asyncio
async def test_start_attempt_creates_second_attempt(
    client,
    auth_headers,
    practice_activities,
):
    url = (
        "/api/v1/practice/activities/"
        f"{practice_activities['published_activity_id']}/attempts"
    )

    first = await client.post(
        url,
        headers=auth_headers,
    )
    second = await client.post(
        url,
        headers=auth_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 201

    assert first.json()["attempt_no"] == 1
    assert second.json()["attempt_no"] == 2


@pytest.mark.asyncio
async def test_start_attempt_rejects_unpublished_activity(
    client,
    auth_headers,
    practice_activities,
):
    response = await client.post(
        f"/api/v1/practice/activities/"
        f"{practice_activities['draft_activity_id']}/attempts",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_start_attempt_requires_authentication(
    client,
    practice_activities,
):
    response = await client.post(
        f"/api/v1/practice/activities/"
        f"{practice_activities['published_activity_id']}/attempts",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_submit_attempt_accepts_correct_answer(
    client,
    auth_headers,
    practice_activities,
):
    start = await client.post(
        f"/api/v1/practice/activities/{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/v1/practice/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"submission": "Linux"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == attempt_id
    assert body["result"] == "SUCCESS"
    assert float(body["score"]) == 1.0
    assert body["submitted_at"]
    assert "submission_ref" not in body


@pytest.mark.asyncio
async def test_submit_attempt_rejects_incorrect_answer(
    client,
    auth_headers,
    practice_activities,
):
    start = await client.post(
        f"/api/v1/practice/activities/{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/v1/practice/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"submission": "Windows"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"] == "FAILED"
    assert float(body["score"]) == 0.0


@pytest.mark.asyncio
async def test_submit_attempt_cannot_be_submitted_twice(
    client,
    auth_headers,
    practice_activities,
):
    start = await client.post(
        f"/api/v1/practice/activities/{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    first = await client.post(
        f"/api/v1/practice/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"submission": "Linux"},
    )
    assert first.status_code == 200

    second = await client.post(
        f"/api/v1/practice/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"submission": "Linux"},
    )

    assert second.status_code == 422
    assert second.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_submit_attempt_requires_ownership(
    client,
    auth_headers,
    practice_activities,
):
    start = await client.post(
        f"/api/v1/practice/activities/{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    second_username = f"other_{uuid4().hex[:8]}"
    second_email = f"practice_other_{uuid4().hex[:8]}@example.com"

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": second_username,
            "email": second_email,
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 201, response.text

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": second_username,
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 200

    other_headers = {
        "Authorization": f"Bearer {response.json()['access_token']}"
    }

    response = await client.post(
        f"/api/v1/practice/attempts/{attempt_id}/submit",
        headers=other_headers,
        json={"submission": "Linux"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_submit_attempt_requires_authentication(
    client,
    auth_headers,
    practice_activities,
):
    start = await client.post(
        f"/api/v1/practice/activities/{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/v1/practice/attempts/{attempt_id}/submit",
        json={"submission": "Linux"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_attempt_returns_own_attempt(
    client,
    auth_headers,
    practice_activities,
):
    start = await client.post(
        f"/api/v1/practice/activities/"
        f"{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.get(
        f"/api/v1/practice/attempts/{attempt_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == attempt_id
    assert body["practice_activity_id"] == str(
        practice_activities["published_activity_id"]
    )
    assert body["attempt_no"] == 1
    assert body["result"] is None
    assert body["score"] is None
    assert body["submitted_at"] is None
    assert "learner_id" not in body
    assert "submission_ref" in body


@pytest.mark.asyncio
async def test_get_attempt_returns_submitted_attempt(
    client,
    auth_headers,
    practice_activities,
):
    start = await client.post(
        f"/api/v1/practice/activities/"
        f"{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    submit = await client.post(
        f"/api/v1/practice/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={"submission": "Linux"},
    )
    assert submit.status_code == 200

    response = await client.get(
        f"/api/v1/practice/attempts/{attempt_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == attempt_id
    assert body["result"] == "SUCCESS"
    assert float(body["score"]) == 1.0
    assert body["submitted_at"]
    assert "learner_id" not in body


@pytest.mark.asyncio
async def test_get_attempt_returns_not_found_for_unknown_attempt(
    client,
    auth_headers,
):
    response = await client.get(
        f"/api/v1/practice/attempts/{uuid4()}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_attempt_requires_ownership(
    client,
    auth_headers,
    practice_activities,
):
    start = await client.post(
        f"/api/v1/practice/activities/"
        f"{practice_activities['published_activity_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    second_username = f"reader_{uuid4().hex[:8]}"
    second_email = f"reader_{uuid4().hex[:8]}@example.com"

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": second_username,
            "email": second_email,
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 201, response.text

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": second_username,
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 200

    other_headers = {
        "Authorization": f"Bearer {response.json()['access_token']}"
    }

    response = await client.get(
        f"/api/v1/practice/attempts/{attempt_id}",
        headers=other_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_attempt_requires_authentication(
    client,
):
    response = await client.get(
        f"/api/v1/practice/attempts/{uuid4()}",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_attempts_returns_learner_history_in_attempt_order(
    client,
    auth_headers,
    practice_activities,
):
    url = (
        "/api/v1/practice/activities/"
        f"{practice_activities['published_activity_id']}/attempts"
    )

    first = await client.post(
        url,
        headers=auth_headers,
    )
    second = await client.post(
        url,
        headers=auth_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 201

    first_id = first.json()["id"]
    second_id = second.json()["id"]

    submit = await client.post(
        f"/api/v1/practice/attempts/{first_id}/submit",
        headers=auth_headers,
        json={"submission": "Linux"},
    )

    assert submit.status_code == 200

    response = await client.get(
        url,
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2

    assert body[0]["id"] == first_id
    assert body[0]["attempt_no"] == 1
    assert body[0]["result"] == "SUCCESS"
    assert float(body[0]["score"]) == 1.0

    assert body[1]["id"] == second_id
    assert body[1]["attempt_no"] == 2
    assert body[1]["result"] is None
    assert body[1]["score"] is None

    for attempt in body:
        assert "learner_id" not in attempt


@pytest.mark.asyncio
async def test_list_attempts_requires_authentication(
    client,
    practice_activities,
):
    response = await client.get(
        "/api/v1/practice/activities/"
        f"{practice_activities['published_activity_id']}/attempts",
    )

    assert response.status_code == 401
