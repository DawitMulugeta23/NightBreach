from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from app.domains.sandbox.runtime.provider import (
    RuntimeCommandResult,
    RuntimeMachine,
    RuntimeNetwork,
    RuntimeNetworkAttachment,
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
    network_attachments: list[RuntimeNetworkAttachment] = field(
        default_factory=list
    )


class FakeRuntime(RuntimeProvider):
    def __init__(self) -> None:
        self.networks: dict[str, FakeNetwork] = {}
        self.machines: dict[str, FakeMachine] = {}

        self.removed_networks: list[str] = []
        self.removed_machines: list[str] = []

        self.created_networks: list[RuntimeNetwork] = []
        self.created_machines: list[RuntimeMachine] = []

        self.machine_limits: dict[str, object | None] = {}
        self.fail_create_machine = False
        self.fail_start_machine = False
        self.fail_execute_command = False

        self.fail_remove_machine_ids: set[str] = set()
        self.fail_remove_network_ids: set[str] = set()

        self.executed_commands: list[tuple[str, list[str]]] = []

        self.command_results: dict[
            tuple[str, tuple[str, ...]],
            RuntimeCommandResult,
        ] = {}

        self._next_network_id = 1
        self._next_machine_id = 1

    def create_network(
        self,
        *,
        name: str,
        subnet: str | None = None,
        gateway: str | None = None,
        internal: bool = True,
    ) -> RuntimeNetwork:
        network_id = f"network-{self._next_network_id}"
        self._next_network_id += 1

        network = FakeNetwork(
            id=network_id,
            name=name,
        )

        self.networks[network_id] = network

        result = RuntimeNetwork(
            id=network_id,
            name=name,
        )

        self.created_networks.append(result)

        return result

    def remove_network(self, *, network_id: str) -> None:
        if network_id in self.fail_remove_network_ids:
            raise RuntimeError(
                f"Fake network removal failed for '{network_id}'."
            )

        self.networks.pop(network_id, None)
        self.removed_networks.append(network_id)

    def create_machine(
        self,
        *,
        name: str,
        image: str,
        network_attachments: Sequence[RuntimeNetworkAttachment],
        limits: object | None = None,
        command: Sequence[str] | None = None,
    ) -> RuntimeMachine:
        self.machine_limits[name] = limits

        if self.fail_create_machine:
            raise RuntimeError("Fake machine creation failed.")

        machine_id = f"machine-{self._next_machine_id}"
        self._next_machine_id += 1

        machine = FakeMachine(
            id=machine_id,
            name=name,
            network_attachments=list(network_attachments),
        )

        self.machines[machine_id] = machine

        result = RuntimeMachine(
            id=machine_id,
            name=name,
        )

        self.created_machines.append(result)

        return result

    def start_machine(self, *, machine_id: str) -> None:
        if self.fail_start_machine:
            raise RuntimeError("Fake machine start failed.")

        machine = self.machines[machine_id]
        machine.running = True

    def stop_machine(self, *, machine_id: str) -> None:
        machine = self.machines.get(machine_id)

        if machine is not None:
            machine.running = False

    def remove_machine(self, *, machine_id: str) -> None:
        if machine_id in self.fail_remove_machine_ids:
            raise RuntimeError(
                f"Fake machine removal failed for '{machine_id}'."
            )

        self.machines.pop(machine_id, None)
        self.removed_machines.append(machine_id)

    def inspect_machine(self, *, machine_id: str) -> dict:
        machine = self.machines[machine_id]

        networks: dict[str, dict[str, str | None]] = {}

        for attachment in machine.network_attachments:
            network = self.networks.get(attachment.network_id)

            if network is None:
                continue

            networks[network.name] = {
                "NetworkID": network.id,
                "IPAddress": attachment.ipv4_address,
            }

        return {
            "Id": machine.id,
            "Name": machine.name,
            "Running": machine.running,
            "State": {
                "Running": machine.running,
            },
            "NetworkSettings": {
                "Networks": networks,
            },
        }

    def inspect_network(self, *, network_id: str) -> dict:
        network = self.networks[network_id]

        return {
            "Id": network.id,
            "Name": network.name,
        }

    def execute_command(
        self,
        *,
        machine_id: str,
        command: Sequence[str],
        timeout: int | None = None,
    ) -> RuntimeCommandResult:
        if self.fail_execute_command:
            raise RuntimeError("Fake command execution failed.")

        if machine_id not in self.machines:
            raise RuntimeError(
                f"Unknown fake machine '{machine_id}'."
            )

        command_list = list(command)

        if not command_list:
            raise RuntimeError(
                "A command is required for runtime execution."
            )

        self.executed_commands.append(
            (machine_id, command_list)
        )

        key = (
            machine_id,
            tuple(command_list),
        )

        configured_result = self.command_results.get(key)

        if configured_result is not None:
            return configured_result

        return RuntimeCommandResult(
            exit_code=0,
            stdout="",
            stderr="",
        )
