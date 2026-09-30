from __future__ import annotations

from dataclasses import dataclass, field

from app.models.sandbox import Environment

from ..runtime.provider import RuntimeProvider


@dataclass
class EnvironmentValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


def validate_environment(
    *,
    environment: Environment,
    runtime: RuntimeProvider,
) -> EnvironmentValidationResult:
    errors: list[str] = []

    networks_by_id = {
        network.id: network
        for network in environment.networks
    }

    runtime_network_ids: set[str] = set()

    if not environment.networks:
        errors.append("Environment has no networks.")

    for network in environment.networks:
        runtime_network_id = network.runtime_network_id

        if runtime_network_id is None:
            errors.append(
                f"Network '{network.name}' has no runtime network."
            )
            continue

        try:
            inspected = runtime.inspect_network(
                network_id=runtime_network_id,
            )
        except Exception:
            errors.append(
                f"Runtime network for '{network.name}' "
                "could not be inspected."
            )
            continue

        runtime_network_ids.add(runtime_network_id)

        if inspected.get("Id") != runtime_network_id:
            errors.append(
                f"Runtime network ID mismatch for '{network.name}'."
            )

    if not environment.machines:
        errors.append("Environment has no machines.")

    for machine in environment.machines:
        runtime_machine_id = machine.runtime_machine_id

        if runtime_machine_id is None:
            errors.append(
                f"Machine '{machine.name}' has no runtime machine."
            )
            continue

        try:
            inspected = runtime.inspect_machine(
                machine_id=runtime_machine_id,
            )
        except Exception:
            errors.append(
                f"Runtime machine for '{machine.name}' "
                "could not be inspected."
            )
            continue

        if inspected.get("Id") != runtime_machine_id:
            errors.append(
                f"Runtime machine ID mismatch for '{machine.name}'."
            )

        state = inspected.get("State") or {}
        running = state.get("Running")

        if running is None:
            running = inspected.get("Running", False)

        if not running:
            errors.append(
                f"Machine '{machine.name}' is not running."
            )

        if not machine.interfaces:
            errors.append(
                f"Machine '{machine.name}' has no interfaces."
            )
            continue

        network_settings = inspected.get("NetworkSettings") or {}
        runtime_networks = network_settings.get("Networks") or {}

        interface_network_ids: set = set()

        for interface in machine.interfaces:
            if interface.network_id not in networks_by_id:
                errors.append(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' references an unknown network."
                )
                continue

            if interface.network_id in interface_network_ids:
                errors.append(
                    f"Machine '{machine.name}' has multiple interfaces "
                    "on the same network."
                )

            interface_network_ids.add(interface.network_id)

            network = networks_by_id[interface.network_id]
            runtime_network_id = network.runtime_network_id

            if runtime_network_id is None:
                errors.append(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' references a network without "
                    "a runtime network."
                )
                continue

            if runtime_network_id not in runtime_network_ids:
                errors.append(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' references an unavailable "
                    "runtime network."
                )
                continue

            if not interface.address:
                errors.append(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' has no address."
                )
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
                errors.append(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' is not attached to runtime "
                    f"network '{network.name}'."
                )
                continue

            runtime_network_id_from_attachment = runtime_attachment.get(
                "NetworkID"
            )

            if runtime_network_id_from_attachment != runtime_network_id:
                errors.append(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' has the wrong runtime network."
                )

            runtime_address = runtime_attachment.get("IPAddress")

            if runtime_address != interface.address:
                errors.append(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' has runtime address "
                    f"'{runtime_address}' instead of "
                    f"'{interface.address}'."
                )

    return EnvironmentValidationResult(
        valid=not errors,
        errors=errors,
    )
