from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.ctf_challenge import (
    CTFChallenge,
    CTFChallengeGroup,
    CTFChallengeMode,
    CTFChallengeStatus,
    CTFChallengeType,
)
from app.models.ctf_attempt import CTFAttempt
from app.models.ctf_submission import CTFSubmission


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
    username = f"ctf_api_{uuid4().hex[:10]}"
    email = f"{username}@example.com"
    password = "strong-password-123"

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200

    return {
        "Authorization": f"Bearer {response.json()['access_token']}",
    }


@pytest_asyncio.fixture
async def ctf_challenges():
    async with AsyncSessionLocal() as session:
        group = CTFChallengeGroup(
            code=f"test-{uuid4().hex[:10]}",
            name="CTF API Test Group",
            description="Group used by CTF API tests.",
            position=1,
        )

        published = CTFChallenge(
            slug=f"published-{uuid4().hex}",
            title="Published CTF Challenge",
            description="A published challenge for API tests.",
            objective="Find the test flag.",
            scenario="A controlled test scenario.",
            difficulty="easy",
            mode=CTFChallengeMode.INDEPENDENT,
            status=CTFChallengeStatus.PUBLISHED,
            challenge_type=CTFChallengeType.FLAG,
            validation_config={
                "expected_flag": "NB{test-flag}",
                "comparison": "exact",
            },
        )

        draft = CTFChallenge(
            slug=f"draft-{uuid4().hex}",
            title="Draft CTF Challenge",
            description="A draft challenge that must remain hidden.",
            objective="Do not expose this challenge.",
            scenario="Draft scenario.",
            difficulty="easy",
            mode=CTFChallengeMode.GUIDED,
            status=CTFChallengeStatus.DRAFT,
            challenge_type=CTFChallengeType.FLAG,
            validation_config={
                "expected_flag": "NB{draft-flag}",
            },
        )

        group.challenges.extend([published, draft])
        session.add(group)

        await session.commit()

        await session.refresh(group)
        await session.refresh(published)
        await session.refresh(draft)

        try:
            yield {
                "group_id": group.id,
                "published_id": published.id,
                "published_slug": published.slug,
                "draft_id": draft.id,
            }
        finally:
            attempt_ids = (
                await session.execute(
                    CTFAttempt.__table__.select()
                    .with_only_columns(CTFAttempt.id)
                    .where(
                        CTFAttempt.challenge_id.in_(
                            [published.id, draft.id]
                        )
                    )
                )
            ).scalars().all()

            if attempt_ids:
                await session.execute(
                    CTFSubmission.__table__.delete().where(
                        CTFSubmission.attempt_id.in_(attempt_ids)
                    )
                )
            await session.execute(
                CTFAttempt.__table__.delete().where(
                    CTFAttempt.challenge_id.in_(
                        [published.id, draft.id]
                    )
                )
            )
            await session.execute(
                CTFChallenge.__table__.delete().where(
                    CTFChallenge.id.in_([published.id, draft.id])
                )
            )
            await session.execute(
                CTFChallengeGroup.__table__.delete().where(
                    CTFChallengeGroup.id == group.id
                )
            )
            await session.commit()


@pytest.mark.asyncio
async def test_list_challenges_returns_published_only(
    client,
    auth_headers,
    ctf_challenges,
):
    response = await client.get(
        "/api/v1/ctf/challenges",
        params={"group_id": str(ctf_challenges["group_id"])},
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "items" in body
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == str(
        ctf_challenges["published_id"]
    )
    assert body["items"][0]["status"] == "published"

    assert "validation_config" not in body["items"][0]


@pytest.mark.asyncio
async def test_get_challenge_by_id_returns_published_challenge(
    client,
    auth_headers,
    ctf_challenges,
):
    response = await client.get(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(ctf_challenges["published_id"])
    assert body["slug"] == ctf_challenges["published_slug"]
    assert body["challenge_type"] == "flag"
    assert "validation_config" not in body


@pytest.mark.asyncio
async def test_get_challenge_by_slug_returns_published_challenge(
    client,
    auth_headers,
    ctf_challenges,
):
    response = await client.get(
        f"/api/v1/ctf/challenges/slug/{ctf_challenges['published_slug']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(ctf_challenges["published_id"])
    assert body["slug"] == ctf_challenges["published_slug"]


@pytest.mark.asyncio
async def test_draft_challenge_is_not_visible(
    client,
    auth_headers,
    ctf_challenges,
):
    response = await client.get(
        f"/api/v1/ctf/challenges/{ctf_challenges['draft_id']}",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_start_attempt_creates_first_attempt(
    client,
    auth_headers,
    ctf_challenges,
):
    response = await client.post(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}/attempts",
        headers=auth_headers,
        json={
            "session_id": "ctf-test-session-1",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["challenge_id"] == str(
        ctf_challenges["published_id"]
    )
    assert body["attempt_number"] == 1
    assert body["status"] == "started"
    assert body["session_id"] == "ctf-test-session-1"
    assert body["started_at"]
    assert body["completed_at"] is None
    assert "learner_id" in body


@pytest.mark.asyncio
async def test_start_attempt_increments_attempt_number(
    client,
    auth_headers,
    ctf_challenges,
):
    url = (
        f"/api/v1/ctf/challenges/"
        f"{ctf_challenges['published_id']}/attempts"
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

    assert first.json()["attempt_number"] == 1
    assert second.json()["attempt_number"] == 2


@pytest.mark.asyncio
async def test_mark_attempt_in_progress(
    client,
    auth_headers,
    ctf_challenges,
):
    start = await client.post(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/v1/ctf/attempts/{attempt_id}/start",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_submit_correct_flag_passes_attempt_and_records_submission(
    client,
    auth_headers,
    ctf_challenges,
):
    start = await client.post(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/v1/ctf/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={
            "submission_value": "NB{test-flag}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["attempt"]["id"] == attempt_id
    assert body["attempt"]["status"] == "passed"

    assert body["submission"]["attempt_id"] == attempt_id
    assert body["submission"]["submission_value"] == "NB{test-flag}"
    assert body["submission"]["result"] == "passed"
    assert body["submission"]["submitted_at"]


@pytest.mark.asyncio
async def test_submit_incorrect_flag_fails_attempt(
    client,
    auth_headers,
    ctf_challenges,
):
    start = await client.post(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/v1/ctf/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={
            "submission_value": "NB{wrong-flag}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["attempt"]["status"] == "failed"
    assert body["submission"]["result"] == "failed"


@pytest.mark.asyncio
async def test_get_attempt_returns_owned_attempt(
    client,
    auth_headers,
    ctf_challenges,
):
    start = await client.post(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.get(
        f"/api/v1/ctf/attempts/{attempt_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == attempt_id


@pytest.mark.asyncio
async def test_list_attempts_returns_learner_attempts(
    client,
    auth_headers,
    ctf_challenges,
):
    url = (
        f"/api/v1/ctf/challenges/"
        f"{ctf_challenges['published_id']}/attempts"
    )

    first = await client.post(url, headers=auth_headers)
    second = await client.post(url, headers=auth_headers)

    assert first.status_code == 201
    assert second.status_code == 201

    response = await client.get(
        url,
        headers=auth_headers,
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 2
    assert [item["attempt_number"] for item in items] == [1, 2]


@pytest.mark.asyncio
async def test_list_submissions_returns_submission_history(
    client,
    auth_headers,
    ctf_challenges,
):
    start = await client.post(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    submit = await client.post(
        f"/api/v1/ctf/attempts/{attempt_id}/submit",
        headers=auth_headers,
        json={
            "submission_value": "NB{test-flag}",
        },
    )
    assert submit.status_code == 200

    response = await client.get(
        f"/api/v1/ctf/attempts/{attempt_id}/submissions",
        headers=auth_headers,
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 1
    assert items[0]["attempt_id"] == attempt_id
    assert items[0]["submission_value"] == "NB{test-flag}"
    assert items[0]["result"] == "passed"


@pytest.mark.asyncio
async def test_ctf_endpoints_require_authentication(
    client,
    ctf_challenges,
):
    response = await client.get("/api/v1/ctf/challenges")

    assert response.status_code == 401

    response = await client.get(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}",
    )

    assert response.status_code == 401

    response = await client.get(
        f"/api/v1/ctf/challenges/slug/{ctf_challenges['published_slug']}",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ctf_attempts_are_not_accessible_to_another_learner(
    client,
    auth_headers,
    ctf_challenges,
):
    start = await client.post(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    second_username = f"ctf_other_{uuid4().hex[:10]}"
    second_email = f"{second_username}@example.com"
    second_password = "strong-password-123"

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": second_username,
            "email": second_email,
            "password": second_password,
        },
    )
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": second_username,
            "password": second_password,
        },
    )
    assert response.status_code == 200

    second_headers = {
        "Authorization": f"Bearer {response.json()['access_token']}",
    }

    response = await client.get(
        f"/api/v1/ctf/attempts/{attempt_id}",
        headers=second_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_environment_failed_marks_attempt_terminal(
    client,
    auth_headers,
    ctf_challenges,
):
    start = await client.post(
        f"/api/v1/ctf/challenges/{ctf_challenges['published_id']}/attempts",
        headers=auth_headers,
    )
    assert start.status_code == 201

    attempt_id = start.json()["id"]

    response = await client.post(
        f"/api/v1/ctf/attempts/{attempt_id}/environment-failed",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == attempt_id
    assert body["status"] == "environment_failed"
    assert body["completed_at"]

import asyncio


@pytest.mark.asyncio
async def test_concurrent_attempt_creation_allocates_unique_attempt_numbers(
    client,
    auth_headers,
    ctf_challenges,
):
    challenge_id = ctf_challenges["published_id"]

    responses = await asyncio.gather(
        client.post(
            f"/api/v1/ctf/challenges/{challenge_id}/attempts",
            headers=auth_headers,
        ),
        client.post(
            f"/api/v1/ctf/challenges/{challenge_id}/attempts",
            headers=auth_headers,
        ),
    )

    assert all(response.status_code == 201 for response in responses)

    numbers = sorted(
        response.json()["attempt_number"]
        for response in responses
    )

    assert numbers == [1, 2]
