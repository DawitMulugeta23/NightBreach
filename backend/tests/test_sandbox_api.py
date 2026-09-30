from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select, update

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.sandbox import (
    Environment,
    EnvironmentMachine,
    EnvironmentNetwork,
    EnvironmentState,
    MachineInterface,
    MachineRole,
)
from app.models.user import User
from app.domains.sandbox.dependencies import get_runtime_provider


TEST_USERNAME = "sandbox_api_user"
TEST_EMAIL = "sandbox_api@example.com"
TEST_PASSWORD = "strong-password-123"


class FakeRuntime:
    def __init__(self) -> None:
        self.started_machines: list[str] = []
        self.stopped_machines: list[str] = []
        self.removed_machines: list[str] = []
        self.removed_networks: list[str] = []
        self.created_networks: list[dict] = []
        self.created_machines: list[dict] = []

    def start_machine(self, *, machine_id: str) -> None:
        self.started_machines.append(machine_id)

    def stop_machine(self, *, machine_id: str) -> None:
        self.stopped_machines.append(machine_id)

    def remove_machine(self, *, machine_id: str) -> None:
        self.removed_machines.append(machine_id)

    def remove_network(self, *, network_id: str) -> None:
        self.removed_networks.append(network_id)

    def create_network(
        self,
        *,
        name: str,
        subnet: str,
        gateway: str,
    ):
        runtime_id = f"new-network-{len(self.created_networks) + 1}"

        self.created_networks.append(
            {
                "id": runtime_id,
                "name": name,
                "subnet": subnet,
                "gateway": gateway,
            }
        )

        return type(
            "RuntimeNetwork",
            (),
            {
                "id": runtime_id,
                "name": name,
            },
        )()

    def create_machine(
        self,
        *,
        name: str,
        image: str,
        network_attachments,
    ):
        runtime_id = f"new-machine-{len(self.created_machines) + 1}"

        self.created_machines.append(
            {
                "id": runtime_id,
                "name": name,
                "image": image,
                "network_attachments": network_attachments,
            }
        )

        return type(
            "RuntimeMachine",
            (),
            {
                "id": runtime_id,
                "name": name,
            },
        )()


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
        existing_user = await session.scalar(
            select(User).where(User.username == TEST_USERNAME)
        )

        if existing_user is not None:
            await session.execute(
                delete(Environment).where(
                    Environment.learner_id == existing_user.id
                )
            )

            await session.execute(
                delete(User).where(User.id == existing_user.id)
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

    return {
        "Authorization": f"Bearer {response.json()['access_token']}",
    }


@pytest_asyncio.fixture
async def runtime():
    fake_runtime = FakeRuntime()

    app.dependency_overrides[get_runtime_provider] = (
        lambda: fake_runtime
    )

    yield fake_runtime

    app.dependency_overrides.pop(get_runtime_provider, None)


async def create_environment(client, auth_headers) -> str:
    response = await client.post(
        "/api/v1/sandbox/environments",
        headers=auth_headers,
        json={
            "activity_id": "WEB-01",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


@pytest.mark.asyncio
async def test_start_environment_starts_runtime_machines_and_transitions(
    client,
    auth_headers,
    runtime,
):
    environment_id = await create_environment(
        client,
        auth_headers,
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            update(Environment)
            .where(Environment.id == environment_id)
            .values(state=EnvironmentState.STOPPED)
        )
        assert result.rowcount == 1

        environment = await session.get(
            Environment,
            environment_id,
        )
        assert environment is not None

        machine = EnvironmentMachine(
            environment_id=environment.id,
            name="attack-machine",
            role=MachineRole.ATTACK,
            image="nightbreach/attack-machine:latest",
            runtime_machine_id="runtime-machine-start-1",
        )

        session.add(machine)
        await session.commit()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/start",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == environment_id
    assert body["state"] == "ready"
    assert body["state_version"] == 2

    assert runtime.started_machines == [
        "runtime-machine-start-1",
    ]


@pytest.mark.asyncio
async def test_stop_environment_stops_runtime_machines_and_transitions(
    client,
    auth_headers,
    runtime,
):
    environment_id = await create_environment(
        client,
        auth_headers,
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            update(Environment)
            .where(Environment.id == environment_id)
            .values(state=EnvironmentState.ACTIVE)
        )
        assert result.rowcount == 1

        environment = await session.get(
            Environment,
            environment_id,
        )
        assert environment is not None

        machine = EnvironmentMachine(
            environment_id=environment.id,
            name="target-machine",
            role=MachineRole.TARGET,
            image="nightbreach/target-machine:latest",
            runtime_machine_id="runtime-machine-stop-1",
        )

        session.add(machine)
        await session.commit()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/stop",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == environment_id
    assert body["state"] == "stopped"
    assert body["state_version"] == 2

    assert runtime.stopped_machines == [
        "runtime-machine-stop-1",
    ]


@pytest.mark.asyncio
async def test_start_environment_requires_authentication(
    client,
):
    environment_id = uuid4()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/start",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_stop_environment_requires_authentication(
    client,
):
    environment_id = uuid4()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/stop",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reset_environment_rebuilds_runtime_and_returns_ready(
    client,
    auth_headers,
    runtime,
):
    environment_id = await create_environment(
        client,
        auth_headers,
    )

    async with AsyncSessionLocal() as session:
        environment = await session.get(
            Environment,
            environment_id,
        )
        assert environment is not None

        environment.state = EnvironmentState.ACTIVE

        network = EnvironmentNetwork(
            environment_id=environment.id,
            name="lab",
            subnet="10.20.0.0/24",
            gateway="10.20.0.1",
            runtime_network_id="old-network",
        )
        session.add(network)
        await session.flush()

        machine = EnvironmentMachine(
            environment_id=environment.id,
            name="target",
            role=MachineRole.TARGET,
            image="nightbreach/target-machine:latest",
            runtime_machine_id="old-machine",
        )
        session.add(machine)
        await session.flush()

        interface = MachineInterface(
            machine_id=machine.id,
            network_id=network.id,
            name="eth0",
            address="10.20.0.10",
        )
        session.add(interface)

        await session.commit()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/reset",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == environment_id
    assert body["activity_id"] == "WEB-01"
    assert body["state"] == "ready"

    assert runtime.stopped_machines == [
        "old-machine",
    ]

    assert runtime.removed_machines == [
        "old-machine",
    ]

    assert runtime.removed_networks == [
        "old-network",
    ]

    assert len(runtime.created_networks) == 1
    assert runtime.created_networks[0]["subnet"] == "10.20.0.0/24"
    assert runtime.created_networks[0]["gateway"] == "10.20.0.1"

    assert len(runtime.created_machines) == 1
    assert (
        runtime.created_machines[0]["image"]
        == "nightbreach/target-machine:latest"
    )

    attachments = runtime.created_machines[0]["network_attachments"]

    assert len(attachments) == 1
    assert attachments[0].ipv4_address == "10.20.0.10"

    assert runtime.started_machines == [
        runtime.created_machines[0]["id"],
    ]



@pytest.mark.asyncio
async def test_reset_environment_rebuilds_runtime_and_transitions(
    client,
    auth_headers,
    runtime,
):
    environment_id = await create_environment(
        client,
        auth_headers,
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            update(Environment)
            .where(Environment.id == environment_id)
            .values(state=EnvironmentState.READY)
        )
        assert result.rowcount == 1

        environment = await session.get(
            Environment,
            environment_id,
        )
        assert environment is not None

        network = EnvironmentNetwork(
            environment_id=environment.id,
            name="lab",
            subnet="10.10.0.0/24",
            gateway="10.10.0.1",
            runtime_network_id="runtime-network-old-1",
        )

        session.add(network)
        await session.flush()

        machine = EnvironmentMachine(
            environment_id=environment.id,
            name="target-machine",
            role=MachineRole.TARGET,
            image="nightbreach/target-machine:latest",
            runtime_machine_id="runtime-machine-old-1",
        )

        session.add(machine)
        await session.flush()

        interface = MachineInterface(
            machine_id=machine.id,
            network_id=network.id,
            name="eth0",
            address="10.10.0.10",
        )

        session.add(interface)
        await session.commit()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/reset",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == environment_id
    assert body["state"] == "ready"
    assert body["state_version"] == 3

    assert runtime.stopped_machines == [
        "runtime-machine-old-1",
    ]

    assert runtime.removed_machines == [
        "runtime-machine-old-1",
    ]

    assert runtime.removed_networks == [
        "runtime-network-old-1",
    ]

    assert len(runtime.created_networks) == 1

    created_network = runtime.created_networks[0]

    assert created_network["id"] == "new-network-1"
    assert created_network["subnet"] == "10.10.0.0/24"
    assert created_network["gateway"] == "10.10.0.1"

    assert len(runtime.created_machines) == 1

    created_machine = runtime.created_machines[0]

    assert created_machine["id"] == "new-machine-1"
    assert created_machine["image"] == (
        "nightbreach/target-machine:latest"
    )

    attachments = created_machine["network_attachments"]

    assert len(attachments) == 1
    assert attachments[0].network_id == "new-network-1"
    assert attachments[0].ipv4_address == "10.10.0.10"

    assert runtime.started_machines == [
        "new-machine-1",
    ]

    async with AsyncSessionLocal() as session:
        environment = await session.get(
            Environment,
            environment_id,
        )

        assert environment is not None
        assert environment.state == EnvironmentState.READY
        assert environment.state_version == 3

        networks_result = await session.execute(
            select(EnvironmentNetwork).where(
                EnvironmentNetwork.environment_id == environment_id,
            )
        )
        networks = list(networks_result.scalars().all())

        machines_result = await session.execute(
            select(EnvironmentMachine).where(
                EnvironmentMachine.environment_id == environment_id,
            )
        )
        machines = list(machines_result.scalars().all())

        assert len(networks) == 1
        assert networks[0].runtime_network_id == (
            "new-network-1"
        )

        assert len(machines) == 1
        assert machines[0].runtime_machine_id == (
            "new-machine-1"
        )


@pytest.mark.asyncio
async def test_reset_environment_requires_authentication(
    client,
):
    environment_id = uuid4()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/reset",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_provision_environment_creates_runtime_topology_and_returns_ready(
    client,
    auth_headers,
    runtime,
):
    environment_id = await create_environment(
        client,
        auth_headers,
    )

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=auth_headers,
        json={
            "networks": [
                {
                    "name": "lab",
                    "subnet": "10.30.0.0/24",
                    "gateway": "10.30.0.1",
                }
            ],
            "machines": [
                {
                    "name": "attacker",
                    "role": "attack",
                    "image": "nightbreach/attack-machine:latest",
                    "interfaces": [
                        {
                            "name": "eth0",
                            "network_name": "lab",
                            "address": "10.30.0.10",
                        }
                    ],
                },
                {
                    "name": "target",
                    "role": "target",
                    "image": "nightbreach/target-machine:latest",
                    "interfaces": [
                        {
                            "name": "eth0",
                            "network_name": "lab",
                            "address": "10.30.0.20",
                        }
                    ],
                },
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == environment_id
    assert body["activity_id"] == "WEB-01"
    assert body["state"] == "ready"
    assert body["state_version"] == 3

    assert len(runtime.created_networks) == 1

    network = runtime.created_networks[0]

    assert network["name"].startswith(
        f"nb-env-{environment_id}-net-lab"
    )
    assert network["subnet"] == "10.30.0.0/24"
    assert network["gateway"] == "10.30.0.1"

    assert len(runtime.created_machines) == 2

    assert runtime.created_machines[0]["image"] == (
        "nightbreach/attack-machine:latest"
    )
    assert runtime.created_machines[1]["image"] == (
        "nightbreach/target-machine:latest"
    )

    assert len(runtime.started_machines) == 2

    async with AsyncSessionLocal() as session:
        environment = await session.get(
            Environment,
            environment_id,
        )

        assert environment is not None
        assert environment.state == EnvironmentState.READY

        networks = (
            await session.scalars(
                select(EnvironmentNetwork).where(
                    EnvironmentNetwork.environment_id == environment.id
                )
            )
        ).all()

        machines = (
            await session.scalars(
                select(EnvironmentMachine).where(
                    EnvironmentMachine.environment_id == environment.id
                )
            )
        ).all()

        assert len(networks) == 1
        assert len(machines) == 2

        interfaces = (
            await session.scalars(
                select(MachineInterface).where(
                    MachineInterface.machine_id.in_(
                        [machine.id for machine in machines]
                    )
                )
            )
        ).all()

        assert len(interfaces) == 2


@pytest.mark.asyncio
async def test_provision_environment_requires_authentication(
    client,
):
    environment_id = uuid4()

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        json={
            "networks": [
                {
                    "name": "lab",
                    "subnet": "10.30.0.0/24",
                    "gateway": "10.30.0.1",
                }
            ],
            "machines": [
                {
                    "name": "target",
                    "role": "target",
                    "image": "nightbreach/target-machine:latest",
                    "network_name": "lab",
                    "interfaces": [
                        {
                            "name": "eth0",
                            "address": "10.30.0.10",
                        }
                    ],
                }
            ],
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_provision_environment_rejects_unknown_network(
    client,
    auth_headers,
    runtime,
):
    environment_id = await create_environment(
        client,
        auth_headers,
    )

    response = await client.post(
        f"/api/v1/sandbox/environments/{environment_id}/provision",
        headers=auth_headers,
        json={
            "networks": [
                {
                    "name": "lab",
                    "subnet": "10.40.0.0/24",
                    "gateway": "10.40.0.1",
                }
            ],
            "machines": [
                {
                    "name": "target",
                    "role": "target",
                    "image": "nightbreach/target-machine:latest",
                    "interfaces": [
                        {
                            "name": "eth0",
                            "network_name": "missing-network",
                            "address": "10.40.0.10",
                        }
                    ],
                }
            ],
        },
    )

    assert response.status_code >= 400

    assert runtime.created_networks
    assert runtime.removed_networks == [
        runtime.created_networks[0]["id"],
    ]
