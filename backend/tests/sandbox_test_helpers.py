from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.domains.sandbox.runtime.provider import (
    RuntimeMachine,
    RuntimeNetwork,
    RuntimeProvider,
)


@dataclass
class FakeNetwork:
    id: str
    name: str


@dataclass
class FakeMachine:
    id: str
    name: str
    running: bool = False


class FakeRuntime(RuntimeProvider):
    def __init__(self) -> None:
        self.networks = {}
        self.machines = {}
        self.removed_networks = []
        self.removed_machines = []
        self.created_networks = []
        self.created_machines = []
        self.fail_create_machine = False
        self.fail_start_machine = False

    def create_network(
        self,
        *,
        name: str,
        subnet: str | None = None,
        gateway: str | None = None,
    ) -> RuntimeNetwork:
        network_id = f"net-{uuid4().hex}"

        self.networks[network_id] = FakeNetwork(
            id=network_id,
            name=name,
        )

        self.created_networks.append(
            {
                "id": network_id,
                "name": name,
                "subnet": subnet,
                "gateway": gateway,
            }
        )

        return RuntimeNetwork(
            id=network_id,
            name=name,
        )

    def remove_network(self, *, network_id: str) -> None:
        self.networks.pop(network_id, None)
        self.removed_networks.append(network_id)

    def create_machine(
        self,
        *,
        name: str,
        image: str,
        network_attachments,
    ) -> RuntimeMachine:
        if self.fail_create_machine:
            raise RuntimeError("fake machine creation failure")

        machine_id = f"machine-{uuid4().hex}"

        self.machines[machine_id] = FakeMachine(
            id=machine_id,
            name=name,
        )

        self.created_machines.append(
            {
                "id": machine_id,
                "name": name,
                "image": image,
                "network_attachments": tuple(network_attachments),
            }
        )

        return RuntimeMachine(
            id=machine_id,
            name=name,
        )

    def start_machine(self, *, machine_id: str) -> None:
        if self.fail_start_machine:
            raise RuntimeError("fake machine start failure")

        self.machines[machine_id].running = True

    def stop_machine(self, *, machine_id: str) -> None:
        machine = self.machines.get(machine_id)

        if machine is not None:
            machine.running = False

    def remove_machine(self, *, machine_id: str) -> None:
        self.machines.pop(machine_id, None)
        self.removed_machines.append(machine_id)

    def inspect_machine(self, *, machine_id: str) -> dict:
        machine = self.machines[machine_id]

        return {
            "Id": machine.id,
            "Name": machine.name,
            "Running": machine.running,
        }

    def inspect_network(self, *, network_id: str) -> dict:
        network = self.networks[network_id]

        return {
            "Id": network.id,
            "Name": network.name,
        }
