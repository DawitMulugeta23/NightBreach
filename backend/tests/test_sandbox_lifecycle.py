from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domains.sandbox.services.environment_service import (
    EnvironmentProvisioningError,
    EnvironmentService,
    InvalidEnvironmentTransitionError,
)
from app.models.sandbox import (
    Environment,
    EnvironmentMachine,
    EnvironmentNetwork,
    EnvironmentState,
    MachineInterface,
    MachineRole,
    MachineState,
)
from sandbox_test_helpers import FakeMachine, FakeNetwork, FakeRuntime

from app.domains.sandbox.runtime.provider import RuntimeNetworkAttachment


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


def stopped_environment() -> Environment:
    """A stopped one-machine environment backed by fake runtime state."""
    environment_id = uuid4()
    learner_id = uuid4()

    environment = Environment(
        id=environment_id,
        learner_id=learner_id,
        activity_id="WEB-01",
        state=EnvironmentState.STOPPED,
        state_version=4,
    )

    network = EnvironmentNetwork(
        id=uuid4(),
        environment_id=environment_id,
        name="lab",
        subnet="10.10.0.0/24",
        gateway="10.10.0.1",
        runtime_network_id="net-old",
    )

    machine = EnvironmentMachine(
        id=uuid4(),
        environment_id=environment_id,
        name="attacker",
        role=MachineRole.ATTACK,
        image="ubuntu:24.04",
        hostname="attacker",
        runtime_machine_id="machine-1",
        state=MachineState.STOPPED,
    )

    interface = MachineInterface(
        id=uuid4(),
        machine_id=machine.id,
        network_id=network.id,
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

    return environment


def fake_runtime_for(
    environment: Environment,
    runtime: FakeRuntime | None = None,
) -> FakeRuntime:
    """FakeRuntime whose runtime state matches the environment rows."""
    runtime = runtime or FakeRuntime()

    for network in environment.networks:
        runtime.networks[network.runtime_network_id] = FakeNetwork(
            id=network.runtime_network_id,
            name=f"nb-env-{environment.id}-net-{network.name}",
            subnet=network.subnet,
            gateway=network.gateway,
        )

    networks_by_id = {
        network.id: network for network in environment.networks
    }

    for machine in environment.machines:
        runtime.machines[machine.runtime_machine_id] = FakeMachine(
            id=machine.runtime_machine_id,
            name=f"nb-env-{environment.id}-machine-{machine.name}",
            network_attachments=[
                RuntimeNetworkAttachment(
                    network_id=networks_by_id[
                        interface.network_id
                    ].runtime_network_id,
                    ipv4_address=interface.address,
                )
                for interface in machine.interfaces
            ],
        )

    return runtime


@pytest.mark.asyncio
async def test_start_environment_starts_runtime_machines_and_transitions():
    environment = stopped_environment()
    runtime = fake_runtime_for(environment)

    service = EnvironmentService(session=SimpleNamespace(), runtime=runtime)

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

    result = await service.start_environment(
        environment_id=environment.id,
        learner_id=environment.learner_id,
    )

    assert runtime.started_machines == ["machine-1"]
    assert transitions == [EnvironmentState.READY]
    assert result.state == EnvironmentState.READY
    assert result.state_version == 5
    # READY is only reachable after validation passed.
    assert environment.machines[0].state == MachineState.READY
    assert environment.failure_reason is None


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
    environment = stopped_environment()

    runtime = FailingStartRuntime()
    service = EnvironmentService(session=SimpleNamespace(), runtime=runtime)

    async def fake_get_environment(*, environment_id, learner_id):
        return environment

    async def fake_transition(*, environment_id, learner_id, target_state):
        environment.state = target_state
        environment.state_version += 1
        return environment

    service.get_environment = fake_get_environment
    service.transition = fake_transition

    with pytest.raises(
        EnvironmentProvisioningError,
        match="Failed to start environment machines",
    ):
        await service.start_environment(
            environment_id=environment.id,
            learner_id=environment.learner_id,
        )

    assert environment.state == EnvironmentState.STOPPED
    assert environment.machines[0].state == MachineState.FAILED


@pytest.mark.asyncio
async def test_start_environment_fails_validation_and_records_failure():
    environment = stopped_environment()

    # The attack machine starts but its terminal can never be established.
    class NoTerminalRuntime(FakeRuntime):
        def open_shell(self, **kwargs):
            raise RuntimeError("no shell")

    runtime = fake_runtime_for(environment, NoTerminalRuntime())

    service = EnvironmentService(session=SimpleNamespace(), runtime=runtime)

    async def fake_get_environment(*, environment_id, learner_id):
        return environment

    transitions = []

    async def fake_transition(*, environment_id, learner_id, target_state):
        transitions.append(target_state)
        environment.state = target_state
        environment.state_version += 1
        return environment

    service.get_environment = fake_get_environment
    service.transition = fake_transition

    with pytest.raises(EnvironmentProvisioningError):
        await service.start_environment(
            environment_id=environment.id,
            learner_id=environment.learner_id,
        )

    assert transitions == [EnvironmentState.FAILED]
    assert environment.state == EnvironmentState.FAILED
    assert environment.machines[0].state == MachineState.FAILED
    assert environment.failure_reason is not None
    assert "terminal" in environment.failure_reason.lower()


class FakeResetRuntime:
    def __init__(self):
        self.stopped_machines = []
        self.removed_machines = []
        self.removed_networks = []
        self.created_networks = []
        self.created_machines = []
        self.started_machines = []
        self.configured_routes = []
        self.networks_by_id = {}
        self.machines_by_id = {}
        self.fail_start = False
        self.fail_route_configuration = False
        self.opened_shells = []

    def stop_machine(self, *, machine_id):
        self.stopped_machines.append(machine_id)
        machine = self.machines_by_id.get(machine_id)
        if machine is not None:
            machine["running"] = False

    def remove_machine(self, *, machine_id):
        self.removed_machines.append(machine_id)
        self.machines_by_id.pop(machine_id, None)

    def remove_network(self, *, network_id):
        self.removed_networks.append(network_id)
        self.networks_by_id.pop(network_id, None)

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
        self.networks_by_id[runtime_id] = name
        return SimpleNamespace(id=runtime_id, name=name)

    def create_machine(
        self,
        *,
        name,
        image,
        network_attachments,
        limits=None,
        command=None,
        hostname=None,
    ):
        runtime_id = f"new-machine-{name}"
        self.created_machines.append(
            {
                "id": runtime_id,
                "name": name,
                "image": image,
                "network_attachments": network_attachments,
                "hostname": hostname,
            }
        )
        self.machines_by_id[runtime_id] = {
            "running": False,
            "attachments": list(network_attachments),
        }
        return SimpleNamespace(id=runtime_id, name=name)

    def start_machine(self, *, machine_id):
        if self.fail_start:
            raise RuntimeError("runtime start failed")
        self.started_machines.append(machine_id)
        self.machines_by_id[machine_id]["running"] = True

    def inspect_machine(self, *, machine_id):
        machine = self.machines_by_id[machine_id]

        networks = {}

        for attachment in machine["attachments"]:
            name = self.networks_by_id.get(
                attachment.network_id,
                attachment.network_id,
            )
            networks[name] = {
                "NetworkID": attachment.network_id,
                "IPAddress": attachment.ipv4_address,
            }

        return {
            "Id": machine_id,
            "Running": machine["running"],
            "State": {"Running": machine["running"]},
            "NetworkSettings": {"Networks": networks},
        }

    def inspect_network(self, *, network_id):
        return {
            "Id": network_id,
            "Name": self.networks_by_id[network_id],
        }

    def configure_route(
        self,
        *,
        machine_id,
        destination,
        gateway=None,
        interface=None,
    ):
        if self.fail_route_configuration:
            raise RuntimeError("route configuration failed")
        self.configured_routes.append(
            (machine_id, destination, gateway, interface)
        )

    def inspect_routes(self, *, machine_id):
        return ()

    def probe_service(
        self,
        *,
        machine_id,
        host,
        port,
        protocol="tcp",
    ):
        return True

    def ping(self, *, machine_id, host):
        return True

    def open_shell(self, *, machine_id, username=None, **kwargs):
        self.opened_shells.append(machine_id)
        return SimpleNamespace(close=lambda: None)


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


@pytest.mark.asyncio
async def test_reset_failure_cleans_up_new_runtime_resources():
    environment_id = uuid4()
    learner_id = uuid4()

    environment = Environment(
        id=environment_id,
        learner_id=learner_id,
        activity_id="RESET-03",
        state=EnvironmentState.READY,
        state_version=3,
    )

    network = EnvironmentNetwork(
        id=uuid4(),
        environment_id=environment_id,
        name="lab",
        subnet="10.30.0.0/24",
        gateway="10.30.0.1",
        runtime_network_id="old-network",
    )

    machine = EnvironmentMachine(
        id=uuid4(),
        environment_id=environment_id,
        name="target",
        role=MachineRole.TARGET,
        image="ubuntu:24.04",
        runtime_machine_id="old-machine",
        state=MachineState.READY,
    )

    interface = MachineInterface(
        id=uuid4(),
        machine_id=machine.id,
        network_id=network.id,
        name="eth0",
        address="10.30.0.20",
    )

    network.environment = environment
    machine.environment = environment
    interface.machine = machine
    interface.network = network

    environment.networks = [network]
    environment.machines = [machine]
    machine.interfaces = [interface]

    runtime = FakeResetRuntime()
    # The recreated target fails to start after the old runtime is gone.
    runtime.fail_start = True

    service = EnvironmentService(
        session=SimpleNamespace(),
        runtime=runtime,
    )

    async def fake_get_environment(*, environment_id, learner_id):
        return environment

    transitions = []

    async def fake_transition(*, environment_id, learner_id, target_state):
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

    with pytest.raises(EnvironmentProvisioningError):
        await service.reset_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

    new_machine_id = (
        f"new-machine-nb-env-{environment_id}-machine-target"
    )
    new_network_id = f"new-net-nb-env-{environment_id}-net-lab"

    # The old runtime was removed, and the partially-recreated runtime was
    # cleaned up again: no orphaned resources remain.
    assert "old-machine" in runtime.removed_machines
    assert "old-network" in runtime.removed_networks
    assert new_machine_id in runtime.removed_machines
    assert new_network_id in runtime.removed_networks

    assert transitions == [
        EnvironmentState.RESETTING,
        EnvironmentState.FAILED,
    ]
    assert environment.state == EnvironmentState.FAILED
    assert environment.failure_reason == "Environment reset failed."
