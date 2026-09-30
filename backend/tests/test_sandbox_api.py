from __future__ import annotations

from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.domains.sandbox.dependencies import get_runtime_provider
from app.main import app
from app.models.sandbox import Environment, EnvironmentState
from app.models.user import User
from sandbox_test_helpers import FakeRuntime


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture
async def runtime():
    provider = FakeRuntime()
    app.dependency_overrides[get_runtime_provider] = lambda: provider

    yield provider

    app.dependency_overrides.pop(get_runtime_provider, None)


@pytest_asyncio.fixture
async def auth_headers(client):
    unique_id = uuid4().hex[:12]
    username = f"api_{unique_id}"
    email = f"api_{unique_id}@example.com"
    password = "strong-password-123"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201, register_response.text

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.id).where(User.username == username)
        )
        user_id = result.scalar_one()

    yield {
        "Authorization": f"Bearer {token}",
        "user_id": user_id,
    }

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Environment).where(Environment.learner_id == user_id)
        )
        await session.execute(
            delete(User).where(User.id == user_id)
        )
        await session.commit()


def headers_only(auth_headers):
    return {
        "Authorization": auth_headers["Authorization"],
    }


def provision_payload():
    return {
        "networks": [
            {
                "name": "lab",
                "subnet": "172.30.0.0/24",
                "gateway": "172.30.0.1",
            }
        ],
        "machines": [
            {
                "name": "attacker",
                "role": "attack",
                "image": "ubuntu:24.04",
                "interfaces": [
                    {
                        "name": "eth0",
                        "network_name": "lab",
                        "address": "172.30.0.10",
                    }
                ],
            },
            {
                "name": "target",
                "role": "target",
                "image": "ubuntu:24.04",
                "interfaces": [
                    {
                        "name": "eth0",
                        "network_name": "lab",
                        "address": "172.30.0.20",
                    }
                ],
            },
        ],
    }


@pytest.mark.asyncio
async def test_sandbox_endpoints_require_authentication(client):
    response = await client.post(
        "/api/v1/sandbox/environments",
        json={"activity_id": "api-sandbox-test"},
    )

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_and_get_environment(
    client,
    auth_headers,
):
    headers = headers_only(auth_headers)

    response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-test"},
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert UUID(data["id"])
    assert data["learner_id"] == str(auth_headers["user_id"])
    assert data["activity_id"] == "api-sandbox-test"
    assert data["state"] == "requested"
    assert data["state_version"] == 1

    environment_id = data["id"]

    response = await client.get(
        f"/api/v1/sandbox/environments/{environment_id}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == environment_id
    assert data["learner_id"] == str(auth_headers["user_id"])
    assert data["state"] == "requested"


@pytest.mark.asyncio
async def test_provision_stop_start_and_reset_environment(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-lifecycle"},
    )

    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )

    assert provision_response.status_code == 200, provision_response.text

    provisioned = provision_response.json()

    assert provisioned["state"] == "ready"
    assert provisioned["state_version"] == 3
    assert len(runtime.networks) == 1
    assert len(runtime.machines) == 2

    stop_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/stop",
        headers=headers,
    )

    assert stop_response.status_code == 200, stop_response.text
    assert stop_response.json()["state"] == "stopped"

    assert all(
        machine.running is False
        for machine in runtime.machines.values()
    )

    start_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/start",
        headers=headers,
    )

    assert start_response.status_code == 200, start_response.text
    assert start_response.json()["state"] == "ready"

    assert all(
        machine.running is True
        for machine in runtime.machines.values()
    )

    old_machine_ids = set(runtime.machines)
    old_network_ids = set(runtime.networks)

    reset_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/reset",
        headers=headers,
    )

    assert reset_response.status_code == 200, reset_response.text
    assert reset_response.json()["state"] == "ready"

    assert old_machine_ids.isdisjoint(runtime.machines)
    assert old_network_ids.isdisjoint(runtime.networks)
    assert len(runtime.machines) == 2
    assert len(runtime.networks) == 1


@pytest.mark.asyncio
async def test_provision_failure_returns_failed_state(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-failure"},
    )

    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    runtime.fail_create_machine = True

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )

    assert response.status_code >= 400

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Environment.state).where(
                Environment.id == UUID(environment_id)
            )
        )
        state = result.scalar_one()

    assert state == EnvironmentState.FAILED
    assert runtime.machines == {}


@pytest.mark.asyncio
async def test_environment_ownership_is_enforced(
    client,
    auth_headers,
):
    owner_headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=owner_headers,
        json={"activity_id": "api-sandbox-owned"},
    )

    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    unique_id = uuid4().hex[:12]
    username = f"other_{unique_id}"
    email = f"other_{unique_id}@example.com"
    password = "strong-password-123"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201, register_response.text

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert login_response.status_code == 200, login_response.text

    other_headers = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }

    response = await client.get(
        f"/api/v1/sandbox/environments/{environment_id}",
        headers=other_headers,
    )

    assert response.status_code == 404

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.id).where(User.username == username)
        )
        other_user_id = result.scalar_one()

        await session.execute(
            delete(Environment).where(
                Environment.learner_id == other_user_id
            )
        )
        await session.execute(
            delete(User).where(User.id == other_user_id)
        )
        await session.commit()
