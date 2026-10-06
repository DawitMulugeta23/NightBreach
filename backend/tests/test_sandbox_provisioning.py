from collections.abc import Sequence
from uuid import uuid4

import pytest

from app.domains.sandbox.runtime.provider import (
    RuntimeCommandResult,
    RuntimeMachine,
    RuntimeNetwork,
    RuntimeNetworkAttachment,
    RuntimeProvider,
)
from app.domains.sandbox.services.environment_service import (
    EnvironmentProvisioningError,
    EnvironmentService,
    InterfaceSpec,
    MachineSpec,
    NetworkSpec,
)
from app.models.sandbox import Environment, EnvironmentState, MachineRole


class FakeRuntimeProvider(RuntimeProvider):
    def __init__(self) -> None:
        self.networks: list[RuntimeNetwork] = []
        self.machines: list[RuntimeMachine] = []
        self.attachments: list[
            tuple[str, tuple[RuntimeNetworkAttachment, ...]]
        ] = []
        self.started_machines: list[str] = []
        self.stopped_machines: list[str] = []
        self.removed_machines: list[str] = []
        self.removed_networks: list[str] = []
        self.fail_on_create_machine = False
        self.fail_on_start_machine = False

    def create_network(
        self,
        *,
        name: str,
        subnet: str | None = None,
        gateway: str | None = None,
    ) -> RuntimeNetwork:
        network = RuntimeNetwork(
            id=f"net-{len(self.networks) + 1}",
            name=name,
        )
        self.networks.append(network)
        return network

    def remove_network(self, *, network_id: str) -> None:
        self.removed_networks.append(network_id)

    def create_machine(
        self,
        *,
        name: str,
        image: str,
        network_attachments: Sequence[RuntimeNetworkAttachment],
        limits=None,
        command=None,
    ) -> RuntimeMachine:
        if self.fail_on_create_machine:
            raise RuntimeError("machine creation failed")

        machine = RuntimeMachine(
            id=f"machine-{len(self.machines) + 1}",
            name=name,
        )
        self.machines.append(machine)
        self.attachments.append((machine.id, tuple(network_attachments)))
        return machine

    def start_machine(self, *, machine_id: str) -> None:
        if self.fail_on_start_machine:
            raise RuntimeError("machine start failed")

        self.started_machines.append(machine_id)

    def stop_machine(self, *, machine_id: str) -> None:
        self.stopped_machines.append(machine_id)

    def remove_machine(self, *, machine_id: str) -> None:
        self.removed_machines.append(machine_id)

    def inspect_machine(self, *, machine_id: str) -> dict:
        return {}

    def inspect_network(self, *, network_id: str) -> dict:
        return {}

    def execute_command(
        self,
        *,
        machine_id: str,
        command: Sequence[str],
        timeout: int | None = None,
    ) -> RuntimeCommandResult:
        return RuntimeCommandResult(
            exit_code=0,
            stdout="",
            stderr="",
        )


class FakeRepository:
    def __init__(self) -> None:
        self.networks = []
        self.machines = []
        self.interfaces = []
        self.committed = False
        self.rolled_back = False

    async def get_for_learner(
        self,
        *,
        environment_id,
        learner_id,
    ):
        return self.environment

    async def add_network(self, network):
        self.networks.append(network)
        return network

    async def get_network_by_name(
        self,
        *,
        environment_id,
        name,
    ):
        for network in self.networks:
            if (
                network.environment_id == environment_id
                and network.name == name
            ):
                return network

        return None

    async def add_machine(self, machine):
        self.machines.append(machine)
        return machine

    async def add_interface(self, interface):
        self.interfaces.append(interface)
        return interface

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def make_environment() -> Environment:
    return Environment(
        id=uuid4(),
        learner_id=uuid4(),
        activity_id="WEB-01",
        state=EnvironmentState.REQUESTED,
        state_version=1,
    )


def make_service(
    environment: Environment,
    runtime: RuntimeProvider,
) -> EnvironmentService:
    service = EnvironmentService.__new__(EnvironmentService)

    repository = FakeRepository()
    repository.environment = environment

    service.repository = repository
    service.runtime = runtime
    service.session = None

    return service


def specs():
    return (
        NetworkSpec(
            name="lab-network",
            subnet="10.10.0.0/24",
            gateway="10.10.0.1",
        ),
    ), (
        MachineSpec(
            name="attack-machine",
            role=MachineRole.ATTACK,
            image="nightbreach/attack-machine:latest",
            interfaces=(
                InterfaceSpec(
                    name="eth0",
                    network_name="lab-network",
                    address="10.10.0.10",
                ),
            ),
        ),
    )


@pytest.mark.asyncio
async def test_provision_creates_runtime_graph_and_reaches_ready() -> None:
    environment = make_environment()
    runtime = FakeRuntimeProvider()
    service = make_service(environment, runtime)

    networks, machines = specs()

    result = await service.provision_environment(
        environment_id=environment.id,
        learner_id=environment.learner_id,
        networks=networks,
        machines=machines,
    )

    assert result.state == EnvironmentState.READY
    assert result.state_version == 3

    assert len(runtime.networks) == 1
    assert len(runtime.machines) == 1
    assert runtime.started_machines == ["machine-1"]

    assert service.repository.networks[0].runtime_network_id == "net-1"
    assert service.repository.machines[0].runtime_machine_id == "machine-1"

    assert len(service.repository.interfaces) == 1
    assert service.repository.interfaces[0].name == "eth0"
    assert service.repository.interfaces[0].address == "10.10.0.10"

    assert runtime.attachments[0][0] == "machine-1"
    assert runtime.attachments[0][1] == (
        RuntimeNetworkAttachment(
            network_id="net-1",
            ipv4_address="10.10.0.10",
        ),
    )


@pytest.mark.asyncio
async def test_provision_supports_machine_interfaces_on_multiple_networks() -> None:
    environment = make_environment()
    runtime = FakeRuntimeProvider()
    service = make_service(environment, runtime)

    networks = (
        NetworkSpec(
            name="attack-network",
            subnet="10.10.0.0/24",
            gateway="10.10.0.1",
        ),
        NetworkSpec(
            name="target-network",
            subnet="10.20.0.0/24",
            gateway="10.20.0.1",
        ),
    )

    machines = (
        MachineSpec(
            name="attack-machine",
            role=MachineRole.ATTACK,
            image="nightbreach/attack-machine:latest",
            interfaces=(
                InterfaceSpec(
                    name="eth0",
                    network_name="attack-network",
                    address="10.10.0.10",
                ),
                InterfaceSpec(
                    name="eth1",
                    network_name="target-network",
                    address="10.20.0.10",
                ),
            ),
        ),
    )

    result = await service.provision_environment(
        environment_id=environment.id,
        learner_id=environment.learner_id,
        networks=networks,
        machines=machines,
    )

    assert result.state == EnvironmentState.READY

    assert len(runtime.networks) == 2
    assert [network.id for network in runtime.networks] == [
        "net-1",
        "net-2",
    ]

    assert len(runtime.machines) == 1
    assert runtime.started_machines == ["machine-1"]

    assert len(runtime.attachments) == 1
    assert runtime.attachments[0] == (
        "machine-1",
        (
            RuntimeNetworkAttachment(
                network_id="net-1",
                ipv4_address="10.10.0.10",
            ),
            RuntimeNetworkAttachment(
                network_id="net-2",
                ipv4_address="10.20.0.10",
            ),
        ),
    )

    assert len(service.repository.networks) == 2
    assert {
        network.name: network.runtime_network_id
        for network in service.repository.networks
    } == {
        "attack-network": "net-1",
        "target-network": "net-2",
    }

    assert len(service.repository.machines) == 1
    assert service.repository.machines[0].runtime_machine_id == "machine-1"

    assert len(service.repository.interfaces) == 2
    assert {
        interface.name: (
            interface.address,
            interface.network_id,
        )
        for interface in service.repository.interfaces
    } == {
        "eth0": (
            "10.10.0.10",
            service.repository.networks[0].id,
        ),
        "eth1": (
            "10.20.0.10",
            service.repository.networks[1].id,
        ),
    }


@pytest.mark.asyncio
async def test_provision_failure_cleans_up_created_resources() -> None:
    environment = make_environment()
    runtime = FakeRuntimeProvider()
    runtime.fail_on_start_machine = True

    service = make_service(environment, runtime)

    networks, machines = specs()

    with pytest.raises(EnvironmentProvisioningError):
        await service.provision_environment(
            environment_id=environment.id,
            learner_id=environment.learner_id,
            networks=networks,
            machines=machines,
        )

    assert environment.state == EnvironmentState.FAILED
    assert runtime.stopped_machines == ["machine-1"]
    assert runtime.removed_machines == ["machine-1"]
    assert runtime.removed_networks == ["net-1"]
    assert service.repository.rolled_back is True


@pytest.mark.asyncio
async def test_provision_failure_during_machine_creation_cleans_networks() -> None:
    environment = make_environment()
    runtime = FakeRuntimeProvider()
    runtime.fail_on_create_machine = True

    service = make_service(environment, runtime)

    networks, machines = specs()

    with pytest.raises(EnvironmentProvisioningError):
        await service.provision_environment(
            environment_id=environment.id,
            learner_id=environment.learner_id,
            networks=networks,
            machines=machines,
        )

    assert environment.state == EnvironmentState.FAILED
    assert runtime.removed_machines == []
    assert runtime.removed_networks == ["net-1"]
    assert service.repository.rolled_back is True


@pytest.mark.asyncio
async def test_provision_rejects_missing_network() -> None:
    environment = make_environment()
    runtime = FakeRuntimeProvider()
    service = make_service(environment, runtime)

    networks = (
        NetworkSpec(
            name="lab-network",
            subnet="10.10.0.0/24",
            gateway="10.10.0.1",
        ),
    )

    machines = (
        MachineSpec(
            name="attack-machine",
            role=MachineRole.ATTACK,
            image="nightbreach/attack-machine:latest",
            interfaces=(
                InterfaceSpec(
                    name="eth0",
                    network_name="missing-network",
                    address="10.10.0.10",
                ),
            ),
        ),
    )

    with pytest.raises(EnvironmentProvisioningError):
        await service.provision_environment(
            environment_id=environment.id,
            learner_id=environment.learner_id,
            networks=networks,
            machines=machines,
        )

    assert environment.state == EnvironmentState.FAILED
    assert runtime.removed_networks == ["net-1"]


@pytest.mark.asyncio
async def test_provision_rejects_machine_without_interface() -> None:
    environment = make_environment()
    runtime = FakeRuntimeProvider()
    service = make_service(environment, runtime)

    networks = (
        NetworkSpec(
            name="lab-network",
            subnet="10.10.0.0/24",
            gateway="10.10.0.1",
        ),
    )

    machines = (
        MachineSpec(
            name="attack-machine",
            role=MachineRole.ATTACK,
            image="nightbreach/attack-machine:latest",
            interfaces=(),
        ),
    )

    with pytest.raises(EnvironmentProvisioningError):
        await service.provision_environment(
            environment_id=environment.id,
            learner_id=environment.learner_id,
            networks=networks,
            machines=machines,
        )

    assert environment.state == EnvironmentState.FAILED
    assert len(runtime.networks) == 1
    assert runtime.removed_networks == ["net-1"]
