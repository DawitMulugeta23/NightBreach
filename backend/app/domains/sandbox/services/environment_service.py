from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sandbox import (
    Environment,
    EnvironmentMachine,
    EnvironmentNetwork,
    EnvironmentState,
    MachineInterface,
    MachineRole,
)

from ..repositories.environment_repository import EnvironmentRepository
from ..runtime.provider import (
    RuntimeNetworkAttachment,
    RuntimeProvider,
)
from ..validators.environment import (
    EnvironmentValidationResult,
    validate_environment,
)

from app.core.errors import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


class SandboxServiceError(Exception):
    """Base error for Sandbox service operations."""


class EnvironmentNotFoundError(
    SandboxServiceError,
    NotFoundError,
):
    """Requested Sandbox environment does not exist."""


class InvalidEnvironmentTransitionError(
    SandboxServiceError,
    ConflictError,
):
    """Sandbox environment cannot perform the requested state transition."""


class EnvironmentOwnershipError(
    SandboxServiceError,
    AuthorizationError,
):
    """The current learner does not own the Sandbox environment."""


class EnvironmentProvisioningError(
    SandboxServiceError,
    ValidationError,
):
    """Sandbox environment provisioning failed or was invalid."""


@dataclass(frozen=True)
class InterfaceSpec:
    name: str
    network_name: str
    address: str


@dataclass(frozen=True)
class NetworkSpec:
    name: str
    subnet: str
    gateway: str


@dataclass(frozen=True)
class MachineSpec:
    name: str
    role: MachineRole
    image: str
    interfaces: tuple[InterfaceSpec, ...] = field(default_factory=tuple)


class EnvironmentService:
    """Application service for Sandbox environment lifecycle and provisioning."""

    _ALLOWED_TRANSITIONS: dict[EnvironmentState, set[EnvironmentState]] = {
        EnvironmentState.REQUESTED: {
            EnvironmentState.PROVISIONING,
            EnvironmentState.TERMINATING,
        },
        EnvironmentState.PROVISIONING: {
            EnvironmentState.READY,
            EnvironmentState.FAILED,
            EnvironmentState.TERMINATING,
        },
        EnvironmentState.READY: {
            EnvironmentState.ACTIVE,
            EnvironmentState.RESETTING,
            EnvironmentState.STOPPED,
            EnvironmentState.TERMINATING,
        },
        EnvironmentState.ACTIVE: {
            EnvironmentState.RESETTING,
            EnvironmentState.STOPPED,
            EnvironmentState.TERMINATING,
        },
        EnvironmentState.RESETTING: {
            EnvironmentState.READY,
            EnvironmentState.FAILED,
            EnvironmentState.TERMINATING,
        },
        EnvironmentState.STOPPED: {
            EnvironmentState.READY,
            EnvironmentState.PROVISIONING,
            EnvironmentState.TERMINATING,
        },
        EnvironmentState.FAILED: {
            EnvironmentState.PROVISIONING,
            EnvironmentState.TERMINATING,
        },
        EnvironmentState.TERMINATING: {
            EnvironmentState.DESTROYED,
            EnvironmentState.FAILED,
        },
        EnvironmentState.DESTROYED: set(),
    }

    def __init__(
        self,
        session: AsyncSession,
        runtime: RuntimeProvider | None = None,
    ) -> None:
        self.session = session
        self.repository = EnvironmentRepository(session)
        self.runtime = runtime

    async def create_environment(
        self,
        *,
        learner_id: UUID,
        activity_id: str,
    ) -> Environment:
        environment = Environment(
            learner_id=learner_id,
            activity_id=activity_id,
            state=EnvironmentState.REQUESTED,
            state_version=1,
        )

        created = await self.repository.create(environment)
        await self.repository.commit()
        return created

    async def get_environment(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
    ) -> Environment:
        environment = await self.repository.get_for_learner(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment is None:
            raise EnvironmentNotFoundError(
                "Environment was not found for the authenticated learner."
            )

        return environment

    async def validate_environment(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
    ) -> EnvironmentValidationResult:
        if self.runtime is None:
            raise EnvironmentProvisioningError(
                "A runtime provider is required to validate an environment."
            )

        environment = await self.get_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        return validate_environment(
            environment=environment,
            runtime=self.runtime,
        )

    async def transition(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
        target_state: EnvironmentState,
    ) -> Environment:
        environment = await self.get_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        current_state = environment.state

        if target_state == current_state:
            return environment

        allowed_states = self._ALLOWED_TRANSITIONS[current_state]

        if target_state not in allowed_states:
            raise InvalidEnvironmentTransitionError(
                f"Invalid environment transition: "
                f"{current_state.value} -> {target_state.value}."
            )

        environment.state = target_state
        environment.state_version += 1

        await self.repository.commit()

        return environment

    async def stop_environment(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
    ) -> Environment:
        if self.runtime is None:
            raise EnvironmentProvisioningError(
                "A runtime provider is required to stop an environment."
            )

        environment = await self.get_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment.state not in {
            EnvironmentState.READY,
            EnvironmentState.ACTIVE,
        }:
            raise InvalidEnvironmentTransitionError(
                "Only READY or ACTIVE environments can be stopped."
            )

        try:
            for machine in environment.machines:
                if machine.runtime_machine_id is None:
                    continue

                self.runtime.stop_machine(
                    machine_id=machine.runtime_machine_id,
                )

        except Exception as exc:
            raise EnvironmentProvisioningError(
                "Failed to stop environment machines."
            ) from exc

        return await self.transition(
            environment_id=environment_id,
            learner_id=learner_id,
            target_state=EnvironmentState.STOPPED,
        )

    async def start_environment(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
    ) -> Environment:
        if self.runtime is None:
            raise EnvironmentProvisioningError(
                "A runtime provider is required to start an environment."
            )

        environment = await self.get_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment.state != EnvironmentState.STOPPED:
            raise InvalidEnvironmentTransitionError(
                "Only STOPPED environments can be started."
            )

        try:
            for machine in environment.machines:
                if machine.runtime_machine_id is None:
                    continue

                self.runtime.start_machine(
                    machine_id=machine.runtime_machine_id,
                )

        except Exception as exc:
            raise EnvironmentProvisioningError(
                "Failed to start environment machines."
            ) from exc

        return await self.transition(
            environment_id=environment_id,
            learner_id=learner_id,
            target_state=EnvironmentState.READY,
        )

    async def reset_environment(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
    ) -> Environment:
        if self.runtime is None:
            raise EnvironmentProvisioningError(
                "A runtime provider is required to reset an environment."
            )

        environment = await self.get_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment.state not in {
            EnvironmentState.READY,
            EnvironmentState.ACTIVE,
        }:
            raise InvalidEnvironmentTransitionError(
                "Only READY or ACTIVE environments can be reset."
            )

        await self.transition(
            environment_id=environment_id,
            learner_id=learner_id,
            target_state=EnvironmentState.RESETTING,
        )

        old_machine_ids = [
            machine.runtime_machine_id
            for machine in environment.machines
            if machine.runtime_machine_id is not None
        ]

        old_network_ids = [
            network.runtime_network_id
            for network in environment.networks
            if network.runtime_network_id is not None
        ]

        try:
            # Remove the current runtime machines first so their network
            # attachments no longer prevent network removal.
            for machine_id in reversed(old_machine_ids):
                self.runtime.stop_machine(machine_id=machine_id)
                self.runtime.remove_machine(machine_id=machine_id)

            for network_id in reversed(old_network_ids):
                self.runtime.remove_network(network_id=network_id)

            # Recreate the networks from the persisted environment topology.
            runtime_network_ids: dict[UUID, str] = {}

            for network in environment.networks:
                runtime_network = self.runtime.create_network(
                    name=(
                        f"nb-env-{environment_id}-"
                        f"net-{network.name}"
                    ),
                    subnet=network.subnet,
                    gateway=network.gateway,
                )

                runtime_network_ids[network.id] = runtime_network.id
                network.runtime_network_id = runtime_network.id

            # Recreate every machine using its persisted image and interface
            # configuration.
            for machine in environment.machines:
                attachments = tuple(
                    RuntimeNetworkAttachment(
                        network_id=runtime_network_ids[interface.network_id],
                        ipv4_address=interface.address,
                    )
                    for interface in machine.interfaces
                )

                runtime_machine = self.runtime.create_machine(
                    name=(
                        f"nb-env-{environment_id}-"
                        f"machine-{machine.name}"
                    ),
                    image=machine.image,
                    network_attachments=attachments,
                )

                machine.runtime_machine_id = runtime_machine.id

                self.runtime.start_machine(
                    machine_id=runtime_machine.id,
                )

            await self.repository.commit()

            return await self.transition(
                environment_id=environment_id,
                learner_id=learner_id,
                target_state=EnvironmentState.READY,
            )

        except Exception as exc:
            await self.repository.rollback()

            try:
                await self.transition(
                    environment_id=environment_id,
                    learner_id=learner_id,
                    target_state=EnvironmentState.FAILED,
                )
            except Exception:
                pass

            if isinstance(exc, SandboxServiceError):
                raise

            raise EnvironmentProvisioningError(
                "Environment reset failed."
            ) from exc

    async def terminate_environment(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
    ) -> Environment:
        if self.runtime is None:
            raise EnvironmentProvisioningError(
                "A runtime provider is required to terminate an environment."
            )

        environment = await self.get_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment.state not in {
            EnvironmentState.REQUESTED,
            EnvironmentState.PROVISIONING,
            EnvironmentState.READY,
            EnvironmentState.ACTIVE,
            EnvironmentState.RESETTING,
            EnvironmentState.STOPPED,
            EnvironmentState.FAILED,
        }:
            raise InvalidEnvironmentTransitionError(
                "This environment cannot be terminated from its current state."
            )

        await self.transition(
            environment_id=environment_id,
            learner_id=learner_id,
            target_state=EnvironmentState.TERMINATING,
        )

        errors: list[Exception] = []

        # Remove machines first so their network attachments are gone
        # before the runtime networks are removed.
        for machine in reversed(environment.machines):
            runtime_machine_id = machine.runtime_machine_id

            if runtime_machine_id is None:
                continue

            try:
                try:
                    self.runtime.stop_machine(
                        machine_id=runtime_machine_id,
                    )
                except Exception:
                    # Stopping is best-effort during termination. The
                    # authoritative cleanup operation is machine removal.
                    pass

                self.runtime.remove_machine(
                    machine_id=runtime_machine_id,
                )
            except Exception as exc:
                errors.append(exc)
                continue

            machine.runtime_machine_id = None

        # Only remove networks after machine removal has succeeded for the
        # machines that still reference them.
        for network in reversed(environment.networks):
            runtime_network_id = network.runtime_network_id

            if runtime_network_id is None:
                continue

            try:
                self.runtime.remove_network(
                    network_id=runtime_network_id,
                )
            except Exception as exc:
                errors.append(exc)
                continue

            network.runtime_network_id = None

        # Runtime resources cannot be restored by a database rollback. Persist
        # the successful cleanup so the remaining runtime IDs accurately
        # describe what a subsequent termination retry still needs to remove.
        await self.repository.commit()

        if errors:
            await self.transition(
                environment_id=environment_id,
                learner_id=learner_id,
                target_state=EnvironmentState.FAILED,
            )

            raise EnvironmentProvisioningError(
                "Environment termination failed for one or more runtime resources."
            ) from errors[0]

        return await self.transition(
            environment_id=environment_id,
            learner_id=learner_id,
            target_state=EnvironmentState.DESTROYED,
        )

    async def provision_environment(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
        networks: tuple[NetworkSpec, ...],
        machines: tuple[MachineSpec, ...],
    ) -> Environment:
        if self.runtime is None:
            raise EnvironmentProvisioningError(
                "A runtime provider is required for environment provisioning."
            )

        environment = await self.get_environment(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment.state != EnvironmentState.REQUESTED:
            raise InvalidEnvironmentTransitionError(
                "Only REQUESTED environments can be provisioned."
            )

        if not networks:
            raise EnvironmentProvisioningError(
                "At least one network is required."
            )

        if not machines:
            raise EnvironmentProvisioningError(
                "At least one machine is required."
            )

        await self.transition(
            environment_id=environment_id,
            learner_id=learner_id,
            target_state=EnvironmentState.PROVISIONING,
        )

        runtime_network_ids: dict[str, str] = {}
        runtime_machine_ids: list[str] = []

        try:
            for network_spec in networks:
                runtime_network = self.runtime.create_network(
                    name=(
                        f"nb-env-{environment_id}-"
                        f"net-{network_spec.name}"
                    ),
                    subnet=network_spec.subnet,
                    gateway=network_spec.gateway,
                )

                runtime_network_ids[network_spec.name] = runtime_network.id

                await self.repository.add_network(
                    EnvironmentNetwork(
                        environment_id=environment_id,
                        name=network_spec.name,
                        subnet=network_spec.subnet,
                        gateway=network_spec.gateway,
                        runtime_network_id=runtime_network.id,
                    )
                )

            for machine_spec in machines:
                interface_specs = machine_spec.interfaces

                if not interface_specs:
                    raise EnvironmentProvisioningError(
                        f"Machine '{machine_spec.name}' requires "
                        "at least one interface."
                    )

                interface_network_names = [
                    interface_spec.network_name
                    for interface_spec in interface_specs
                ]

                if len(interface_network_names) != len(
                    set(interface_network_names)
                ):
                    raise EnvironmentProvisioningError(
                        f"Machine '{machine_spec.name}' cannot have "
                        "multiple interfaces on the same network."
                    )

                network_attachments: list[RuntimeNetworkAttachment] = []
                interface_networks: dict[str, EnvironmentNetwork] = {}

                for interface_spec in interface_specs:
                    network_name = interface_spec.network_name

                    if network_name not in runtime_network_ids:
                        raise EnvironmentProvisioningError(
                            f"Unknown network '{network_name}' "
                            f"for interface '{interface_spec.name}' "
                            f"on machine '{machine_spec.name}'."
                        )

                    network = await self.repository.get_network_by_name(
                        environment_id=environment_id,
                        name=network_name,
                    )

                    if network is None:
                        raise EnvironmentProvisioningError(
                            f"Network '{network_name}' was not found "
                            f"for machine '{machine_spec.name}'."
                        )

                    interface_networks[interface_spec.name] = network

                    network_attachments.append(
                        RuntimeNetworkAttachment(
                            network_id=runtime_network_ids[network_name],
                            ipv4_address=interface_spec.address,
                        )
                    )

                runtime_machine = self.runtime.create_machine(
                    name=(
                        f"nb-env-{environment_id}-"
                        f"machine-{machine_spec.name}"
                    ),
                    image=machine_spec.image,
                    network_attachments=tuple(network_attachments),
                )

                runtime_machine_ids.append(runtime_machine.id)

                machine = EnvironmentMachine(
                    environment_id=environment_id,
                    name=machine_spec.name,
                    role=machine_spec.role,
                    image=machine_spec.image,
                    runtime_machine_id=runtime_machine.id,
                )

                await self.repository.add_machine(machine)

                for interface_spec in interface_specs:
                    network = interface_networks[interface_spec.name]

                    await self.repository.add_interface(
                        MachineInterface(
                            machine_id=machine.id,
                            network_id=network.id,
                            name=interface_spec.name,
                            address=interface_spec.address,
                        )
                    )

                self.runtime.start_machine(
                    machine_id=runtime_machine.id,
                )

            await self.repository.commit()

            return await self.transition(
                environment_id=environment_id,
                learner_id=learner_id,
                target_state=EnvironmentState.READY,
            )

        except Exception as exc:
            for machine_id in reversed(runtime_machine_ids):
                try:
                    self.runtime.stop_machine(machine_id=machine_id)
                except Exception:
                    pass

                try:
                    self.runtime.remove_machine(machine_id=machine_id)
                except Exception:
                    pass

            for network_id in reversed(list(runtime_network_ids.values())):
                try:
                    self.runtime.remove_network(network_id=network_id)
                except Exception:
                    pass

            await self.repository.rollback()

            try:
                await self.transition(
                    environment_id=environment_id,
                    learner_id=learner_id,
                    target_state=EnvironmentState.FAILED,
                )
            except Exception:
                pass

            if isinstance(exc, SandboxServiceError):
                raise

            raise EnvironmentProvisioningError(
                "Environment provisioning failed."
            ) from exc
