from __future__ import annotations

import ipaddress
import time
from dataclasses import dataclass, field
from uuid import UUID

from app.models.sandbox import (
    Environment,
    EnvironmentMachine,
    EnvironmentNetwork,
    MachineRole,
    MachineState,
)

from ..runtime.provider import RuntimeProvider, RuntimeRoute

# Probes are retried because services may still be coming up right after a
# machine starts.
PROBE_ATTEMPTS = 3
PROBE_RETRY_DELAY_SECONDS = 0.2


@dataclass
class ServiceValidationResult:
    name: str
    protocol: str
    port: int
    required: bool
    ready: bool


@dataclass
class MachineValidationResult:
    machine_id: UUID
    name: str
    role: MachineRole
    # Persisted lifecycle state at validation time (validation itself never
    # mutates state).
    state: MachineState | None = None
    ready: bool = False
    terminal_ready: bool = False
    services: list[ServiceValidationResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class NetworkValidationResult:
    network_id: UUID
    name: str
    ready: bool = False
    errors: list[str] = field(default_factory=list)


@dataclass
class EnvironmentValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    networks: list[NetworkValidationResult] = field(default_factory=list)
    machines: list[MachineValidationResult] = field(default_factory=list)

    @property
    def attack_machine(self) -> MachineValidationResult | None:
        for machine in self.machines:
            if machine.role == MachineRole.ATTACK:
                return machine
        return None

    @property
    def targets(self) -> list[MachineValidationResult]:
        return [
            machine
            for machine in self.machines
            if machine.role == MachineRole.TARGET
        ]


def validate_environment(
    *,
    environment: Environment,
    runtime: RuntimeProvider,
    machines: list[EnvironmentMachine] | None = None,
    networks: list[EnvironmentNetwork] | None = None,
    include_services: bool = True,
    include_connectivity: bool = True,
    include_terminal: bool = True,
) -> EnvironmentValidationResult:
    """Full readiness validation: runtime state, routes, target services,
    attack-to-target reachability and terminal access."""
    return _validate(
        runtime=runtime,
        networks=list(environment.networks if networks is None else networks),
        machines=list(environment.machines if machines is None else machines),
        include_services=include_services,
        include_connectivity=include_connectivity,
        include_terminal=include_terminal,
    )


def validate_targets(
    *,
    environment: Environment,
    runtime: RuntimeProvider,
    machines: list[EnvironmentMachine],
    networks: list[EnvironmentNetwork],
) -> EnvironmentValidationResult:
    """Target-machine validation used before the attack machine is started.

    Checks that every target exists, runs, is attached with the expected
    addresses and carries its required routes. Service and reachability
    probes need a source machine on the network and run in the full
    validation pass.
    """
    return _validate(
        runtime=runtime,
        networks=networks,
        machines=machines,
        include_services=False,
        include_connectivity=False,
        include_terminal=False,
    )


def _normalize_destination(value: str) -> str:
    try:
        return str(ipaddress.ip_network(value, strict=False))
    except ValueError:
        return value


def _route_present(
    runtime_routes: tuple[RuntimeRoute, ...],
    *,
    destination: str,
    gateway: str | None,
    interface: str | None,
) -> bool:
    wanted = _normalize_destination(destination)

    for route in runtime_routes:
        if _normalize_destination(route.destination) != wanted:
            continue

        if gateway is not None and (route.gateway or None) != gateway:
            continue

        if interface is not None and route.interface not in (None, interface):
            continue

        return True

    return False


def _probe_with_retries(probe, *args, **kwargs) -> bool:
    for attempt in range(PROBE_ATTEMPTS):
        try:
            if probe(*args, **kwargs):
                return True
        except Exception:
            pass

        if attempt < PROBE_ATTEMPTS - 1:
            time.sleep(PROBE_RETRY_DELAY_SECONDS)

    return False


def _pick_service_source(
    target: EnvironmentMachine,
    machines: list[EnvironmentMachine],
    runtime_machines: dict[UUID, EnvironmentMachine],
) -> EnvironmentMachine | None:
    """Choose the machine a target's services are probed from.

    Prefers the attack machine (the learner's viewpoint), then any other
    running machine that shares a network with the target, then the target
    itself (services are still running locally).
    """
    if target.id not in runtime_machines:
        return None

    target_networks = {interface.network_id for interface in target.interfaces}

    def shares_network(candidate: EnvironmentMachine) -> bool:
        return any(
            interface.network_id in target_networks
            for interface in candidate.interfaces
        )

    for machine in machines:
        if (
            machine.id != target.id
            and machine.role == MachineRole.ATTACK
            and machine.id in runtime_machines
            and shares_network(machine)
        ):
            return machine

    for machine in machines:
        if (
            machine.id != target.id
            and machine.id in runtime_machines
            and shares_network(machine)
        ):
            return machine

    return target


def _pick_probe_host(
    source: EnvironmentMachine,
    target: EnvironmentMachine,
) -> str | None:
    source_networks = {interface.network_id for interface in source.interfaces}

    for interface in target.interfaces:
        if interface.network_id in source_networks:
            return interface.address

    if target.interfaces:
        return target.interfaces[0].address

    return None


def _validate(
    *,
    runtime: RuntimeProvider,
    networks: list[EnvironmentNetwork],
    machines: list[EnvironmentMachine],
    include_services: bool,
    include_connectivity: bool,
    include_terminal: bool,
) -> EnvironmentValidationResult:
    errors: list[str] = []

    network_results: dict[UUID, NetworkValidationResult] = {}
    machine_results: dict[UUID, MachineValidationResult] = {}

    # Machines whose runtime exists and is running: probes only make sense
    # for those.
    probeable: dict[UUID, EnvironmentMachine] = {}

    def add_error(
        message: str,
        *,
        machine: MachineValidationResult | None = None,
        network: NetworkValidationResult | None = None,
    ) -> None:
        errors.append(message)

        if machine is not None:
            machine.errors.append(message)

        if network is not None:
            network.errors.append(message)

    networks_by_id = {network.id: network for network in networks}

    if not networks:
        errors.append("Environment has no networks.")

    runtime_network_ids: set[str] = set()

    for network in networks:
        result = NetworkValidationResult(
            network_id=network.id,
            name=network.name,
        )
        network_results[network.id] = result

        runtime_network_id = network.runtime_network_id

        if runtime_network_id is None:
            add_error(
                f"Network '{network.name}' has no runtime network.",
                network=result,
            )
            continue

        try:
            inspected = runtime.inspect_network(
                network_id=runtime_network_id,
            )
        except Exception:
            add_error(
                f"Runtime network for '{network.name}' "
                "could not be inspected.",
                network=result,
            )
            continue

        runtime_network_ids.add(runtime_network_id)

        if inspected.get("Id") != runtime_network_id:
            add_error(
                f"Runtime network ID mismatch for '{network.name}'.",
                network=result,
            )
            continue

        result.ready = True

    if not machines:
        errors.append("Environment has no machines.")

    for machine in machines:
        result = MachineValidationResult(
            machine_id=machine.id,
            name=machine.name,
            role=machine.role,
            state=machine.state,
        )
        machine_results[machine.id] = result

        runtime_machine_id = machine.runtime_machine_id

        if runtime_machine_id is None:
            add_error(
                f"Machine '{machine.name}' has no runtime machine.",
                machine=result,
            )
            continue

        try:
            inspected = runtime.inspect_machine(
                machine_id=runtime_machine_id,
            )
        except Exception:
            add_error(
                f"Runtime machine for '{machine.name}' "
                "could not be inspected.",
                machine=result,
            )
            continue

        if inspected.get("Id") != runtime_machine_id:
            add_error(
                f"Runtime machine ID mismatch for '{machine.name}'.",
                machine=result,
            )
            continue

        state = inspected.get("State") or {}
        running = state.get("Running")

        if running is None:
            running = inspected.get("Running", False)

        if not running:
            add_error(
                f"Machine '{machine.name}' is not running.",
                machine=result,
            )
            continue

        if not machine.interfaces:
            add_error(
                f"Machine '{machine.name}' has no interfaces.",
                machine=result,
            )
            continue

        network_settings = inspected.get("NetworkSettings") or {}
        runtime_networks = network_settings.get("Networks") or {}

        interface_network_ids: set = set()
        interfaces_ok = True

        for interface in machine.interfaces:
            if interface.network_id not in networks_by_id:
                add_error(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' references an unknown network.",
                    machine=result,
                )
                interfaces_ok = False
                continue

            if interface.network_id in interface_network_ids:
                add_error(
                    f"Machine '{machine.name}' has multiple interfaces "
                    "on the same network.",
                    machine=result,
                )

            interface_network_ids.add(interface.network_id)

            network = networks_by_id[interface.network_id]
            runtime_network_id = network.runtime_network_id

            if runtime_network_id is None:
                add_error(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' references a network without "
                    "a runtime network.",
                    machine=result,
                )
                interfaces_ok = False
                continue

            if runtime_network_id not in runtime_network_ids:
                add_error(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' references an unavailable "
                    "runtime network.",
                    machine=result,
                )
                interfaces_ok = False
                continue

            if not interface.address:
                add_error(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' has no address.",
                    machine=result,
                )
                interfaces_ok = False
                continue

            runtime_attachment = None

            for attachment_name, attachment in runtime_networks.items():
                if attachment_name == network.name:
                    runtime_attachment = attachment
                    break

                if attachment.get("NetworkID") == runtime_network_id:
                    runtime_attachment = attachment
                    break

            if runtime_attachment is None:
                add_error(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' is not attached to runtime "
                    f"network '{network.name}'.",
                    machine=result,
                )
                interfaces_ok = False
                continue

            runtime_network_id_from_attachment = runtime_attachment.get(
                "NetworkID"
            )

            if runtime_network_id_from_attachment != runtime_network_id:
                add_error(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' has the wrong runtime network.",
                    machine=result,
                )
                interfaces_ok = False

            runtime_address = runtime_attachment.get("IPAddress")

            if runtime_address != interface.address:
                add_error(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' has runtime address "
                    f"'{runtime_address}' instead of "
                    f"'{interface.address}'.",
                    machine=result,
                )
                interfaces_ok = False

        if interfaces_ok:
            probeable[machine.id] = machine

    # ---- routes -----------------------------------------------------------
    for machine in machines:
        result = machine_results[machine.id]

        if machine.id not in probeable or not machine.routes:
            continue

        try:
            runtime_routes = runtime.inspect_routes(
                machine_id=machine.runtime_machine_id,
            )
        except Exception:
            add_error(
                f"Routes for machine '{machine.name}' could not be inspected.",
                machine=result,
            )
            continue

        for route in machine.routes:
            interface_name = None

            if route.network_id is not None:
                interface_name = next(
                    (
                        interface.name
                        for interface in machine.interfaces
                        if interface.network_id == route.network_id
                    ),
                    None,
                )

            if not _route_present(
                runtime_routes,
                destination=route.destination,
                gateway=route.gateway,
                interface=interface_name,
            ):
                add_error(
                    f"Machine '{machine.name}' is missing route to "
                    f"'{route.destination}'.",
                    machine=result,
                )

    # ---- target services --------------------------------------------------
    if include_services:
        for machine in machines:
            result = machine_results[machine.id]

            if not machine.services or machine.id not in probeable:
                continue

            source = _pick_service_source(machine, machines, probeable)

            if source is None or source.runtime_machine_id is None:
                continue

            host = _pick_probe_host(source, machine)

            if host is None:
                continue

            for service in machine.services:
                ready = _probe_with_retries(
                    runtime.probe_service,
                    machine_id=source.runtime_machine_id,
                    host=host,
                    port=service.port,
                    protocol=service.protocol,
                )

                result.services.append(
                    ServiceValidationResult(
                        name=service.name,
                        protocol=service.protocol,
                        port=service.port,
                        required=service.required,
                        ready=ready,
                    )
                )

                if not ready and service.required:
                    source_label = (
                        "the attack machine"
                        if source.id != machine.id
                        else "itself"
                    )
                    add_error(
                        f"Service '{service.name}' "
                        f"({service.protocol}/{service.port}) on machine "
                        f"'{machine.name}' is not reachable from "
                        f"{source_label}.",
                        machine=result,
                    )

    # ---- attack-to-target connectivity -----------------------------------
    if include_connectivity:
        attack = next(
            (
                machine
                for machine in machines
                if machine.role == MachineRole.ATTACK
                and machine.id in probeable
            ),
            None,
        )

        if attack is not None and attack.runtime_machine_id is not None:
            for machine in machines:
                if machine.role != MachineRole.TARGET:
                    continue

                if machine.id not in probeable:
                    continue

                host = _pick_probe_host(attack, machine)

                if host is None:
                    continue

                reachable = _probe_with_retries(
                    runtime.ping,
                    machine_id=attack.runtime_machine_id,
                    host=host,
                )

                if not reachable:
                    add_error(
                        f"Machine '{machine.name}' is not reachable "
                        "from the attack machine.",
                        machine=machine_results[machine.id],
                    )

    # ---- attack machine terminal ------------------------------------------
    if include_terminal:
        attack = next(
            (
                machine
                for machine in machines
                if machine.role == MachineRole.ATTACK
                and machine.id in probeable
            ),
            None,
        )

        if attack is not None and attack.runtime_machine_id is not None:
            result = machine_results[attack.id]

            terminal_ready = False

            try:
                shell = runtime.open_shell(
                    machine_id=attack.runtime_machine_id,
                )
                terminal_ready = True

                try:
                    shell.close()
                except Exception:
                    pass
            except Exception:
                terminal_ready = False

            result.terminal_ready = terminal_ready

            if not terminal_ready:
                add_error(
                    f"Terminal access to attack machine '{attack.name}' "
                    "could not be established.",
                    machine=result,
                )

    for machine in machines:
        result = machine_results[machine.id]
        result.ready = not result.errors

    return EnvironmentValidationResult(
        valid=not errors,
        errors=errors,
        networks=list(network_results.values()),
        machines=list(machine_results.values()),
    )
