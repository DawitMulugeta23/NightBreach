from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domains.sandbox.services.environment_service import (
    EnvironmentProvisioningError,
    EnvironmentService,
    InvalidEnvironmentTransitionError,
)
from app.models.sandbox import Environment, EnvironmentMachine, EnvironmentNetwork, EnvironmentState, MachineInterface, MachineRole


def make_environment(
    state: EnvironmentState = EnvironmentState.REQUESTED,
) -> Environment:
    return Environment(
        id=uuid4(),
        learner_id=uuid4(),
        activity_id="WEB-01",
        state=state,
        state_version=1,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (
            EnvironmentState.REQUESTED,
            EnvironmentState.PROVISIONING,
        ),
        (
            EnvironmentState.PROVISIONING,
            EnvironmentState.READY,
        ),
        (
            EnvironmentState.PROVISIONING,
            EnvironmentState.FAILED,
        ),
        (
            EnvironmentState.READY,
            EnvironmentState.ACTIVE,
        ),
        (
            EnvironmentState.READY,
            EnvironmentState.RESETTING,
        ),
        (
            EnvironmentState.READY,
            EnvironmentState.STOPPED,
        ),
        (
            EnvironmentState.ACTIVE,
            EnvironmentState.RESETTING,
        ),
        (
            EnvironmentState.ACTIVE,
            EnvironmentState.STOPPED,
        ),
        (
            EnvironmentState.RESETTING,
            EnvironmentState.READY,
        ),
        (
            EnvironmentState.READY,
            EnvironmentState.TERMINATING,
        ),
        (
            EnvironmentState.ACTIVE,
            EnvironmentState.TERMINATING,
        ),
        (
            EnvironmentState.STOPPED,
            EnvironmentState.READY,
        ),
        (
            EnvironmentState.STOPPED,
            EnvironmentState.PROVISIONING,
        ),
        (
            EnvironmentState.STOPPED,
            EnvironmentState.TERMINATING,
        ),
        (
            EnvironmentState.FAILED,
            EnvironmentState.PROVISIONING,
        ),
        (
            EnvironmentState.FAILED,
            EnvironmentState.TERMINATING,
        ),
        (
            EnvironmentState.TERMINATING,
            EnvironmentState.DESTROYED,
        ),
        (
            EnvironmentState.TERMINATING,
            EnvironmentState.FAILED,
        ),
    ],
)
def test_allowed_environment_transitions(
    current: EnvironmentState,
    target: EnvironmentState,
) -> None:
    assert target in EnvironmentService._ALLOWED_TRANSITIONS[current]


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (
            EnvironmentState.REQUESTED,
            EnvironmentState.ACTIVE,
        ),
        (
            EnvironmentState.REQUESTED,
            EnvironmentState.READY,
        ),
        (
            EnvironmentState.REQUESTED,
            EnvironmentState.FAILED,
        ),
        (
            EnvironmentState.PROVISIONING,
            EnvironmentState.ACTIVE,
        ),
        (
            EnvironmentState.READY,
            EnvironmentState.PROVISIONING,
        ),
        (
            EnvironmentState.STOPPED,
            EnvironmentState.ACTIVE,
        ),
        (
            EnvironmentState.DESTROYED,
            EnvironmentState.ACTIVE,
        ),
        (
            EnvironmentState.DESTROYED,
            EnvironmentState.PROVISIONING,
        ),
    ],
)
def test_disallowed_environment_transitions(
    current: EnvironmentState,
    target: EnvironmentState,
) -> None:
    assert target not in EnvironmentService._ALLOWED_TRANSITIONS[current]


@pytest.mark.asyncio
async def test_transition_rejects_invalid_state() -> None:
    environment = make_environment(EnvironmentState.REQUESTED)

    service = EnvironmentService.__new__(EnvironmentService)

    async def fake_get_environment(
        *,
        environment_id,
        learner_id,
    ):
        return environment

    service.get_environment = fake_get_environment

    with pytest.raises(InvalidEnvironmentTransitionError):
        await service.transition(
            environment_id=environment.id,
            learner_id=environment.learner_id,
            target_state=EnvironmentState.ACTIVE,
        )


@pytest.mark.asyncio
async def test_same_state_transition_is_idempotent() -> None:
    environment = make_environment(EnvironmentState.READY)

    service = EnvironmentService.__new__(EnvironmentService)

    async def fake_get_environment(
        *,
        environment_id,
        learner_id,
    ):
        return environment

    service.get_environment = fake_get_environment

    result = await service.transition(
        environment_id=environment.id,
        learner_id=environment.learner_id,
        target_state=EnvironmentState.READY,
    )

    assert result is environment
    assert result.state == EnvironmentState.READY
    assert result.state_version == 1


class FakeLifecycleRuntime:
    def __init__(self) -> None:
        self.stopped_machines: list[str] = []

    def stop_machine(self, *, machine_id: str) -> None:
        self.stopped_machines.append(machine_id)


@pytest.mark.asyncio
async def test_stop_environment_stops_runtime_machines_and_transitions() -> None:
    from app.models.sandbox import EnvironmentMachine, MachineRole

    environment = make_environment(EnvironmentState.ACTIVE)

    machine_one = EnvironmentMachine(
        environment_id=environment.id,
        name="attack-machine",
        role=MachineRole.ATTACK,
        image="nightbreach/attack-machine:latest",
        runtime_machine_id="runtime-machine-1",
    )

    machine_two = EnvironmentMachine(
        environment_id=environment.id,
        name="target-machine",
        role=MachineRole.TARGET,
        image="nightbreach/target-machine:latest",
        runtime_machine_id="runtime-machine-2",
    )

    machine_without_runtime = EnvironmentMachine(
        environment_id=environment.id,
        name="unprovisioned-machine",
        role=MachineRole.TARGET,
        image="nightbreach/target-machine:latest",
        runtime_machine_id=None,
    )

    environment.machines = [
        machine_one,
        machine_two,
        machine_without_runtime,
    ]

    runtime = FakeLifecycleRuntime()

    service = EnvironmentService.__new__(EnvironmentService)
    service.runtime = runtime

    async def fake_get_environment(
        *,
        environment_id,
        learner_id,
    ):
        return environment

    async def fake_transition(
        *,
        environment_id,
        learner_id,
        target_state,
    ):
        environment.state = target_state
        environment.state_version += 1
        return environment

    service.get_environment = fake_get_environment
    service.transition = fake_transition

    result = await service.stop_environment(
        environment_id=environment.id,
        learner_id=environment.learner_id,
    )

    assert runtime.stopped_machines == [
        "runtime-machine-1",
        "runtime-machine-2",
    ]

    assert result.state == EnvironmentState.STOPPED
    assert result.state_version == 2


@pytest.mark.asyncio
async def test_stop_environment_rejects_invalid_state() -> None:
    environment = make_environment(EnvironmentState.REQUESTED)

    runtime = FakeLifecycleRuntime()

    service = EnvironmentService.__new__(EnvironmentService)
    service.runtime = runtime

    async def fake_get_environment(
        *,
        environment_id,
        learner_id,
    ):
        return environment

    service.get_environment = fake_get_environment

    with pytest.raises(InvalidEnvironmentTransitionError):
        await service.stop_environment(
            environment_id=environment.id,
            learner_id=environment.learner_id,
        )

    assert runtime.stopped_machines == []


@pytest.mark.asyncio
async def test_stop_environment_wraps_runtime_failure() -> None:
    class FailingRuntime(FakeLifecycleRuntime):
        def stop_machine(self, *, machine_id: str) -> None:
            raise RuntimeError("runtime stop failed")

    from app.models.sandbox import EnvironmentMachine, MachineRole

    environment = make_environment(EnvironmentState.ACTIVE)

    environment.machines = [
        EnvironmentMachine(
            environment_id=environment.id,
            name="attack-machine",
            role=MachineRole.ATTACK,
            image="nightbreach/attack-machine:latest",
            runtime_machine_id="runtime-machine-1",
        ),
    ]

    service = EnvironmentService.__new__(EnvironmentService)
    service.runtime = FailingRuntime()

    async def fake_get_environment(
        *,
        environment_id,
        learner_id,
    ):
        return environment

    service.get_environment = fake_get_environment

    with pytest.raises(
        EnvironmentProvisioningError,
        match="Failed to stop environment machines",
    ):
        await service.stop_environment(
            environment_id=environment.id,
            learner_id=environment.learner_id,
        )

    assert environment.state == EnvironmentState.ACTIVE


class FakeStartRuntime:
    def __init__(self) -> None:
        self.started_machines: list[str] = []

    def start_machine(self, *, machine_id: str) -> None:
        self.started_machines.append(machine_id)


class FailingStartRuntime(FakeStartRuntime):
    def start_machine(self, *, machine_id: str) -> None:
        raise RuntimeError("runtime start failed")


@pytest.mark.asyncio
async def test_start_environment_starts_runtime_machines_and_transitions():
    learner_id = uuid4()
    environment_id = uuid4()

    environment = SimpleNamespace(
        id=environment_id,
        learner_id=learner_id,
        state=EnvironmentState.STOPPED,
        state_version=4,
        machines=[
            SimpleNamespace(runtime_machine_id="runtime-machine-1"),
            SimpleNamespace(runtime_machine_id="runtime-machine-2"),
            SimpleNamespace(runtime_machine_id=None),
        ],
    )

    runtime = FakeStartRuntime()
    service = EnvironmentService(session=None, runtime=runtime)

    async def fake_get_environment(*, environment_id, learner_id):
        return environment

    async def fake_transition(
        *,
        environment_id,
        learner_id,
        target_state,
    ):
        environment.state = target_state
        environment.state_version += 1
        return environment

    service.get_environment = fake_get_environment
    service.transition = fake_transition

    result = await service.start_environment(
        environment_id=environment_id,
        learner_id=learner_id,
    )

    assert runtime.started_machines == [
        "runtime-machine-1",
        "runtime-machine-2",
    ]
    assert result.state == EnvironmentState.READY
    assert result.state_version == 5


@pytest.mark.asyncio
async def test_start_environment_rejects_invalid_state():
    learner_id = uuid4()
    environment_id = uuid4()

    environment = SimpleNamespace(
        id=environment_id,
        learner_id=learner_id,
        state=EnvironmentState.ACTIVE,
        state_version=2,
        machines=[],
    )

    runtime = FakeStartRuntime()
    service = EnvironmentService(session=None, runtime=runtime)

    async def fake_get_environment(*, environment_id, learner_id):
        return environment

    service.get_environment = fake_get_environment

    with pytest.raises(InvalidEnvironmentTransitionError):
        await service.start_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

    assert runtime.started_machines == []


@pytest.mark.asyncio
async def test_start_environment_wraps_runtime_failure():
    learner_id = uuid4()
    environment_id = uuid4()

    environment = SimpleNamespace(
        id=environment_id,
        learner_id=learner_id,
        state=EnvironmentState.STOPPED,
        state_version=3,
        machines=[
            SimpleNamespace(runtime_machine_id="runtime-machine-1"),
        ],
    )

    runtime = FailingStartRuntime()
    service = EnvironmentService(session=None, runtime=runtime)

    async def fake_get_environment(*, environment_id, learner_id):
        return environment

    service.get_environment = fake_get_environment

    with pytest.raises(EnvironmentProvisioningError):
        await service.start_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )


class FakeResetRuntime:
    def __init__(self):
        self.stopped_machines = []
        self.removed_machines = []
        self.removed_networks = []
        self.created_networks = []
        self.created_machines = []
        self.started_machines = []

    def stop_machine(self, *, machine_id):
        self.stopped_machines.append(machine_id)

    def remove_machine(self, *, machine_id):
        self.removed_machines.append(machine_id)

    def remove_network(self, *, network_id):
        self.removed_networks.append(network_id)

    def create_network(self, *, name, subnet, gateway):
        runtime_id = f"new-net-{name}"
        self.created_networks.append(
            {
                "id": runtime_id,
                "name": name,
                "subnet": subnet,
                "gateway": gateway,
            }
        )
        return SimpleNamespace(id=runtime_id, name=name)

    def create_machine(self, *, name, image, network_attachments):
        runtime_id = f"new-machine-{name}"
        self.created_machines.append(
            {
                "id": runtime_id,
                "name": name,
                "image": image,
                "network_attachments": network_attachments,
            }
        )
        return SimpleNamespace(id=runtime_id, name=name)

    def start_machine(self, *, machine_id):
        self.started_machines.append(machine_id)


@pytest.mark.asyncio
async def test_reset_environment_rebuilds_runtime_and_returns_ready():
    environment_id = uuid4()
    learner_id = uuid4()

    network_id = uuid4()
    machine_id = uuid4()
    interface_id = uuid4()

    environment = Environment(
        id=environment_id,
        learner_id=learner_id,
        activity_id="RESET-01",
        state=EnvironmentState.ACTIVE,
        state_version=4,
    )

    network = EnvironmentNetwork(
        id=network_id,
        environment_id=environment_id,
        name="lab",
        subnet="10.10.0.0/24",
        gateway="10.10.0.1",
        runtime_network_id="old-network",
    )

    machine = EnvironmentMachine(
        id=machine_id,
        environment_id=environment_id,
        name="target",
        role=MachineRole.TARGET,
        image="ubuntu:24.04",
        runtime_machine_id="old-machine",
    )

    interface = MachineInterface(
        id=interface_id,
        machine_id=machine_id,
        network_id=network_id,
        name="eth0",
        address="10.10.0.10",
    )

    network.environment = environment
    machine.environment = environment
    interface.machine = machine
    interface.network = network

    environment.networks = [network]
    environment.machines = [machine]
    machine.interfaces = [interface]

    runtime = FakeResetRuntime()
    service = EnvironmentService(
        session=SimpleNamespace(),
        runtime=runtime,
    )

    async def fake_get_environment(*, environment_id, learner_id):
        return environment

    transitions = []

    async def fake_transition(
        *,
        environment_id,
        learner_id,
        target_state,
    ):
        transitions.append(target_state)
        environment.state = target_state
        environment.state_version += 1
        return environment

    service.get_environment = fake_get_environment
    service.transition = fake_transition

    class FakeRepository:
        async def commit(self):
            return None

        async def rollback(self):
            return None

    service.repository = FakeRepository()

    result = await service.reset_environment(
        environment_id=environment_id,
        learner_id=learner_id,
    )

    assert result is environment
    assert transitions == [
        EnvironmentState.RESETTING,
        EnvironmentState.READY,
    ]

    assert runtime.stopped_machines == ["old-machine"]
    assert runtime.removed_machines == ["old-machine"]
    assert runtime.removed_networks == ["old-network"]

    assert len(runtime.created_networks) == 1
    assert runtime.created_networks[0]["subnet"] == "10.10.0.0/24"
    assert runtime.created_networks[0]["gateway"] == "10.10.0.1"

    assert len(runtime.created_machines) == 1
    assert runtime.created_machines[0]["image"] == "ubuntu:24.04"

    attachments = runtime.created_machines[0]["network_attachments"]
    assert len(attachments) == 1
    assert attachments[0].ipv4_address == "10.10.0.10"

    assert runtime.started_machines == [
        runtime.created_machines[0]["id"]
    ]

    assert network.runtime_network_id == runtime.created_networks[0]["id"]
    assert machine.runtime_machine_id == runtime.created_machines[0]["id"]


@pytest.mark.asyncio
async def test_reset_environment_rejects_stopped_environment():
    environment_id = uuid4()
    learner_id = uuid4()

    environment = Environment(
        id=environment_id,
        learner_id=learner_id,
        activity_id="RESET-02",
        state=EnvironmentState.STOPPED,
        state_version=2,
    )

    runtime = FakeResetRuntime()
    service = EnvironmentService(
        session=SimpleNamespace(),
        runtime=runtime,
    )

    async def fake_get_environment(*, environment_id, learner_id):
        return environment

    service.get_environment = fake_get_environment

    with pytest.raises(InvalidEnvironmentTransitionError):
        await service.reset_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )
