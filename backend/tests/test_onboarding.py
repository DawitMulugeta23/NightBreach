from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.domains.onboarding.models import LearnerProfile
from app.main import app
from app.models.user import User


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def auth_headers(client):
    username = f"onboard_{__import__('uuid').uuid4().hex[:10]}"
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,             "email": f"{username}@example.com",
            "password": "strong-password-123",
        },
    )
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "strong-password-123"},
    )
    assert response.status_code == 200

    yield {"Authorization": f"Bearer {response.json()['access_token']}"}

    async with AsyncSessionLocal() as session:
        user = (
            await session.execute(select(User).where(User.username == username))
        ).scalar_one_or_none()
        if user:
            await session.execute(
                delete(LearnerProfile).where(LearnerProfile.learner_id == user.id)
            )
            await session.execute(delete(User).where(User.id == user.id))
            await session.commit()


@pytest.mark.asyncio
async def test_onboarding_requires_authentication(client):
    response = await client.post("/api/v1/onboarding/start")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_onboarding_start_returns_first_question(client, auth_headers):
    response = await client.post("/api/v1/onboarding/start", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["question_id"] == "goals"
    assert body["dimension"] == "goals"
    assert len(body["options"]) > 0
    assert body["progress"]["answered"] == 0


@pytest.mark.asyncio
async def test_beginner_path_produces_foundational_recommendations(client, auth_headers):
    # Walk a complete beginner through the whole tree.
    sheet = {
        "goals": "fundamentals",
        "background": "beginner",
        "computer": "beginner",
        "networking": "beginner",
        "networking_followup": "unsure",
        "linux": "none",
        "practical": "none",
    }

    # Answer questions one at a time; the client sends the full sheet.
    response = await client.post(
        "/api/v1/onboarding/answer",
        headers=auth_headers,
        json={
            "question_id": "goals",
            "option_ids": ["fundamentals"],
            "answer_sheet": sheet,
        },
    )
    assert response.status_code == 200

    # The service should detect that all gated questions are already answered.
    # If not, submit the remaining branch answers one at a time.
    for qid, oid in list(sheet.items())[1:]:
        response = await client.post(
            "/api/v1/onboarding/answer",
            headers=auth_headers,
            json={
                "question_id": qid,
                "option_ids": [oid],
                "answer_sheet": sheet,
            },
        )
        assert response.status_code == 200
        if response.json()["completed"]:
            break

    body = response.json()
    assert body["completed"] is True
    profile = body["profile"]
    assert profile["linux_cli_knowledge"] == "NONE"
    assert profile["challenge_recommendation"] == "HIGH_GUIDANCE"
    assert any("linux" in p for p in profile["recommended_learning_paths"])
    assert any("linux" in g for g in profile["knowledge_gaps"])


@pytest.mark.asyncio
async def test_experienced_learner_gets_independent_recommendation(client, auth_headers):
    sheet = {
        "goals": "web_pentest",
        "background": "pentester",
        "computer": "advanced",
        "networking": "advanced",
        "linux": "proficient",
        "linux_grep": "grep",
        "web_security": "advanced",
        "web_sqli": "inject",
        "practical": "regular_ctf",
        "tools": "nmap,burp",
        "nmap_version": "nmap",
    }

    last = None
    for qid, oid in sheet.items():
        last = await client.post(
            "/api/v1/onboarding/answer",
            headers=auth_headers,
            json={
                "question_id": qid,
                "option_ids": oid.split(","),
                "answer_sheet": sheet,
            },
        )
        assert last.status_code == 200
        if last.json()["completed"]:
            break

    body = last.json()
    assert body["completed"] is True
    profile = body["profile"]
    assert profile["challenge_recommendation"] == "LOW_GUIDANCE"
    assert "nmap" in profile["tool_experience"]