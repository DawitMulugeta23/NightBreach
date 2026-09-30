from __future__ import annotations

from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.domains.sandbox.dependencies import get_runtime_provider
from app.main import app
from app.models.sandbox import (
    Environment,
    EnvironmentMachine,
    EnvironmentState,
)
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


@pytest.mark.asyncio
async def test_terminate_environment_cleans_runtime_and_persists_destroyed(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-terminate"},
    )

    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )

    assert provision_response.status_code == 200, provision_response.text
    assert provision_response.json()["state"] == "ready"

    old_machine_ids = set(runtime.machines)
    old_network_ids = set(runtime.networks)

    terminate_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/terminate",
        headers=headers,
    )

    assert terminate_response.status_code == 200, terminate_response.text

    terminated = terminate_response.json()

    assert terminated["id"] == environment_id
    assert terminated["state"] == "destroyed"
    assert terminated["state_version"] == 5

    assert runtime.machines == {}
    assert runtime.networks == {}

    assert old_machine_ids.issubset(
        set(runtime.removed_machines)
    )
    assert old_network_ids.issubset(
        set(runtime.removed_networks)
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Environment)
            .options(
                selectinload(Environment.networks),
                selectinload(Environment.machines).selectinload(
                    EnvironmentMachine.interfaces
                ),
            )
            .where(
                Environment.id == UUID(environment_id)
            )
        )
        environment = result.scalar_one()

        assert environment.state == EnvironmentState.DESTROYED
        assert environment.state_version == 5

        for machine in environment.machines:
            assert machine.runtime_machine_id is None

        for network in environment.networks:
            assert network.runtime_network_id is None


@pytest.mark.asyncio
async def test_destroyed_environment_cannot_be_terminated_again(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-double-terminate"},
    )

    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )

    assert provision_response.status_code == 200, provision_response.text

    first_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/terminate",
        headers=headers,
    )

    assert first_response.status_code == 200, first_response.text
    assert first_response.json()["state"] == "destroyed"

    second_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/terminate",
        headers=headers,
    )

    assert second_response.status_code >= 400


@pytest.mark.asyncio
async def test_validate_provisioned_environment(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-validation"},
    )

    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )

    assert provision_response.status_code == 200, provision_response.text
    assert provision_response.json()["state"] == "ready"

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["environment_id"] == environment_id
    assert data["valid"] is True
    assert data["errors"] == []


@pytest.mark.asyncio
async def test_validate_detects_stopped_runtime_machine(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-validation-stopped"},
    )

    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )

    assert provision_response.status_code == 200, provision_response.text

    machine_id = next(iter(runtime.machines))
    runtime.machines[machine_id].running = False

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["valid"] is False
    assert any(
        "is not running" in error
        for error in data["errors"]
    )


@pytest.mark.asyncio
async def test_validation_does_not_change_environment_state(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-validation-state"},
    )

    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )

    assert provision_response.status_code == 200, provision_response.text

    before = provision_response.json()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["valid"] is True

    after_response = await client.get(
        f"/api/v1/sandbox/environments/{environment_id}",
        headers=headers,
    )

    assert after_response.status_code == 200, after_response.text

    after = after_response.json()

    assert after["state"] == before["state"]
    assert after["state_version"] == before["state_version"]

@pytest.mark.asyncio
async def test_validate_detects_runtime_network_attachment_drift(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "validation-network-drift"},
    )
    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )
    assert provision_response.status_code == 200, provision_response.text

    machine_id = next(iter(runtime.machines))
    machine = runtime.machines[machine_id]

    machine.network_attachments = []

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["valid"] is False
    assert any(
        "is not attached to runtime network" in error
        for error in body["errors"]
    )


@pytest.mark.asyncio
async def test_validate_detects_runtime_address_drift(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "validation-address-drift"},
    )
    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )
    assert provision_response.status_code == 200, provision_response.text

    machine_id = next(iter(runtime.machines))
    machine = runtime.machines[machine_id]

    attachment = machine.network_attachments[0]
    machine.network_attachments = [
        type(attachment)(
            network_id=attachment.network_id,
            ipv4_address="172.30.0.99",
        )
    ]

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["valid"] is False
    assert any(
        "has runtime address" in error
        for error in body["errors"]
    )


@pytest.mark.asyncio
async def test_validate_detects_missing_runtime_network(client, runtime, auth_headers):
    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers_only(auth_headers),
        json={"activity_id": "validation-missing-network"},
    )
    assert create_response.status_code == 201
    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers_only(auth_headers),
        json=provision_payload(),
    )
    assert provision_response.status_code == 200

    network_id = next(iter(runtime.networks))
    runtime.networks.pop(network_id)

    validation_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers_only(auth_headers),
    )

    assert validation_response.status_code == 200
    body = validation_response.json()
    assert body["valid"] is False
    assert any("could not be inspected" in error for error in body["errors"])


@pytest.mark.asyncio
async def test_validate_detects_missing_runtime_machine(client, runtime, auth_headers):
    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers_only(auth_headers),
        json={"activity_id": "validation-missing-machine"},
    )
    assert create_response.status_code == 201
    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers_only(auth_headers),
        json=provision_payload(),
    )
    assert provision_response.status_code == 200

    machine_id = next(iter(runtime.machines))
    runtime.machines.pop(machine_id)

    validation_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers_only(auth_headers),
    )

    assert validation_response.status_code == 200
    body = validation_response.json()
    assert body["valid"] is False
    assert any("could not be inspected" in error for error in body["errors"])

@pytest.mark.asyncio
async def test_validate_detects_machine_without_interfaces(
    client,
    runtime,
    auth_headers,
):
    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers_only(auth_headers),
        json={"activity_id": "validation-no-interfaces"},
    )
    assert create_response.status_code == 201
    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers_only(auth_headers),
        json=provision_payload(),
    )
    assert provision_response.status_code == 200

    from sqlalchemy import delete, select
    from app.db.session import AsyncSessionLocal
    from app.models.sandbox import EnvironmentMachine, MachineInterface

    async with AsyncSessionLocal() as session:
        machine_result = await session.execute(
            select(EnvironmentMachine.id)
            .where(
                EnvironmentMachine.environment_id == UUID(environment_id)
            )
            .order_by(EnvironmentMachine.name)
        )
        machine_id = machine_result.scalars().first()
        assert machine_id is not None

        await session.execute(
            delete(MachineInterface).where(
                MachineInterface.machine_id == machine_id
            )
        )
        await session.commit()

    validation_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers_only(auth_headers),
    )

    assert validation_response.status_code == 200
    body = validation_response.json()
    assert body["valid"] is False
    assert any("has no interfaces" in error for error in body["errors"])




@pytest.mark.asyncio
async def test_validate_detects_unknown_interface_network(
    client,
    runtime,
    auth_headers,
):
    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers_only(auth_headers),
        json={"activity_id": "validation-invalid-network"},
    )
    assert create_response.status_code == 201
    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers_only(auth_headers),
        json=provision_payload(),
    )
    assert provision_response.status_code == 200

    from sqlalchemy import select, update
    from app.db.session import AsyncSessionLocal
    from app.models.sandbox import (
        Environment,
        EnvironmentMachine,
        EnvironmentNetwork,
        MachineInterface,
    )

    async with AsyncSessionLocal() as session:
        environment_result = await session.execute(
            select(Environment).where(
                Environment.id == UUID(environment_id)
            )
        )
        environment = environment_result.scalar_one()

        other_environment = Environment(
            id=uuid4(),
            learner_id=environment.learner_id,
            activity_id="validation-other-environment",
        )
        session.add(other_environment)
        await session.flush()

        other_network = EnvironmentNetwork(
            id=uuid4(),
            environment_id=other_environment.id,
            name="other-environment-network",
            subnet="172.31.0.0/24",
            gateway="172.31.0.1",
        )
        session.add(other_network)
        await session.flush()

        interface_result = await session.execute(
            select(MachineInterface.id)
            .join(
                EnvironmentMachine,
                MachineInterface.machine_id == EnvironmentMachine.id,
            )
            .where(
                EnvironmentMachine.environment_id == UUID(environment_id)
            )
            .order_by(MachineInterface.id)
        )
        interface_id = interface_result.scalars().first()
        assert interface_id is not None

        await session.execute(
            update(MachineInterface)
            .where(MachineInterface.id == interface_id)
            .values(network_id=other_network.id)
        )
        await session.commit()

    validation_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/validate",
        headers=headers_only(auth_headers),
    )

    assert validation_response.status_code == 200
    body = validation_response.json()
    assert body["valid"] is False
    assert any(
        "references an unknown network" in error
        for error in body["errors"]
    )




@pytest.mark.asyncio
async def test_terminate_partial_machine_failure_persists_successful_cleanup(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-partial-machine-failure"},
    )
    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )
    assert provision_response.status_code == 200, provision_response.text

    machine_ids = list(runtime.machines)
    network_ids = list(runtime.networks)

    assert len(machine_ids) == 2
    assert len(network_ids) == 1

    failed_machine_id = machine_ids[0]
    successful_machine_id = machine_ids[1]
    network_id = network_ids[0]

    runtime.fail_remove_machine_ids.add(failed_machine_id)

    terminate_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/terminate",
        headers=headers,
    )

    assert terminate_response.status_code == 422, terminate_response.text

    assert failed_machine_id in runtime.machines
    assert successful_machine_id not in runtime.machines

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Environment)
            .options(
                selectinload(Environment.networks),
                selectinload(Environment.machines).selectinload(
                    EnvironmentMachine.interfaces
                ),
            )
            .where(
                Environment.id == UUID(environment_id)
            )
        )
        environment = result.scalar_one()

        assert environment.state == EnvironmentState.FAILED

        persisted_machine_ids = {
            machine.runtime_machine_id
            for machine in environment.machines
        }

        assert failed_machine_id in persisted_machine_ids
        assert successful_machine_id not in persisted_machine_ids

        persisted_network_ids = {
            network.runtime_network_id
            for network in environment.networks
        }

        assert network_id not in persisted_network_ids


@pytest.mark.asyncio
async def test_terminate_retry_cleans_remaining_runtime_resources(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-termination-retry"},
    )
    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )
    assert provision_response.status_code == 200, provision_response.text

    machine_ids = list(runtime.machines)
    assert len(machine_ids) == 2

    failed_machine_id = machine_ids[0]

    runtime.fail_remove_machine_ids.add(failed_machine_id)

    first_terminate = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/terminate",
        headers=headers,
    )

    assert first_terminate.status_code == 422, first_terminate.text
    assert failed_machine_id in runtime.machines

    runtime.fail_remove_machine_ids.clear()

    second_terminate = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/terminate",
        headers=headers,
    )

    assert second_terminate.status_code == 200, second_terminate.text

    terminated = second_terminate.json()

    assert terminated["state"] == "destroyed"
    assert runtime.machines == {}
    assert runtime.networks == {}

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Environment)
            .options(
                selectinload(Environment.networks),
                selectinload(Environment.machines).selectinload(
                    EnvironmentMachine.interfaces
                ),
            )
            .where(
                Environment.id == UUID(environment_id)
            )
        )
        environment = result.scalar_one()

        assert environment.state == EnvironmentState.DESTROYED

        for machine in environment.machines:
            assert machine.runtime_machine_id is None

        for network in environment.networks:
            assert network.runtime_network_id is None


@pytest.mark.asyncio
async def test_terminate_network_failure_preserves_failed_network_for_retry(
    client,
    auth_headers,
    runtime,
):
    headers = headers_only(auth_headers)

    create_response = await client.post(
        "/api/v1/sandbox/environments",
        headers=headers,
        json={"activity_id": "api-sandbox-network-removal-failure"},
    )
    assert create_response.status_code == 201, create_response.text

    environment_id = create_response.json()["id"]

    provision_response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=headers,
        json=provision_payload(),
    )
    assert provision_response.status_code == 200, provision_response.text

    network_ids = list(runtime.networks)
    assert len(network_ids) == 1

    failed_network_id = network_ids[0]

    runtime.fail_remove_network_ids.add(failed_network_id)

    first_terminate = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/terminate",
        headers=headers,
    )

    assert first_terminate.status_code == 422, first_terminate.text
    assert runtime.machines == {}
    assert failed_network_id in runtime.networks

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Environment)
            .options(
                selectinload(Environment.networks),
                selectinload(Environment.machines).selectinload(
                    EnvironmentMachine.interfaces
                ),
            )
            .where(
                Environment.id == UUID(environment_id)
            )
        )
        environment = result.scalar_one()

        assert environment.state == EnvironmentState.FAILED
        assert len(environment.networks) == 1
        assert (
            environment.networks[0].runtime_network_id
            == failed_network_id
        )

        for machine in environment.machines:
            assert machine.runtime_machine_id is None

    runtime.fail_remove_network_ids.clear()

    second_terminate = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/terminate",
        headers=headers,
    )

    assert second_terminate.status_code == 200, second_terminate.text

    terminated = second_terminate.json()

    assert terminated["state"] == "destroyed"
    assert runtime.machines == {}
    assert runtime.networks == {}

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Environment)
            .options(
                selectinload(Environment.networks),
                selectinload(Environment.machines).selectinload(
                    EnvironmentMachine.interfaces
                ),
            )
            .where(
                Environment.id == UUID(environment_id)
            )
        )
        environment = result.scalar_one()

        assert environment.state == EnvironmentState.DESTROYED
        assert len(environment.networks) == 1
        assert environment.networks[0].runtime_network_id is None

        for machine in environment.machines:
            assert machine.runtime_machine_id is None
