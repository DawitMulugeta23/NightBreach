from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field, replace
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sandbox import (
    Environment,
    EnvironmentMachine,
    EnvironmentNetwork,
    EnvironmentState,
    MachineInterface,
    MachineRole,
    MachineRoute,
    MachineService,
    MachineState,
)

from ..repositories.environment_repository import EnvironmentRepository
from ..labs.flags import plant_lab_flags
from ..labs.registry import get_lab
from ..runtime.provider import (
    RuntimeMachineLimits,
    RuntimeNetworkAttachment,
    RuntimeProvider,
)
from ..validators.environment import (
    EnvironmentValidationResult,
    validate_environment,
    validate_targets,
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


_HOSTNAME_PATTERN = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
_SUPPORTED_SERVICE_PROTOCOLS = ("tcp", "udp")


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
class RouteSpec:
    """A route the Sandbox must configure on a machine."""

    destination: str
    gateway: str | None = None
    network_name: str | None = None


@dataclass(frozen=True)
class ServiceSpec:
    """A service a machine's runtime specification requires to be ready."""

    name: str
    port: int
    protocol: str = "tcp"
    required: bool = True


@dataclass(frozen=True)
class MachineSpec:
    """Logical machine definition owned by the Sandbox.

    Fully describes a machine independently from Docker: identity, role,
    image, hostname, interfaces, routes, services and resource limits. The
    runtime adapter translates it into runtime operations.
    """

    name: str
    role: MachineRole
    image: str
    interfaces: tuple[InterfaceSpec, ...] = field(default_factory=tuple)
    limits: RuntimeMachineLimits | None = None
    hostname: str | None = None
    routes: tuple[RouteSpec, ...] = field(default_factory=tuple)
    services: tuple[ServiceSpec, ...] = field(default_factory=tuple)


def _validate_definition(
    networks: tuple[NetworkSpec, ...],
    machines: tuple[MachineSpec, ...],
) -> list[str]:
    """Validate the logical environment definition before any runtime work."""
    errors: list[str] = []

    network_names: set[str] = set()
    parsed_subnets: dict[str, ipaddress.IPv4Network | ipaddress.IPv6Network] = {}

    for network in networks:
        if network.name in network_names:
            errors.append(f"Duplicate network '{network.name}'.")
            continue

        network_names.add(network.name)

        try:
            subnet = ipaddress.ip_network(network.subnet, strict=False)
        except ValueError:
            errors.append(
                f"Network '{network.name}' has an invalid subnet "
                f"'{network.subnet}'."
            )
            continue

        parsed_subnets[network.name] = subnet

        try:
            gateway = ipaddress.ip_address(network.gateway)
        except ValueError:
            errors.append(
                f"Network '{network.name}' has an invalid gateway "
                f"'{network.gateway}'."
            )
            continue

        if gateway not in subnet:
            errors.append(
                f"Gateway '{network.gateway}' is outside network "
                f"'{network.name}'."
            )

    attack_count = sum(
        1 for machine in machines if machine.role == MachineRole.ATTACK
    )

    if attack_count != 1:
        errors.append(
            "An environment must define exactly one attack machine."
        )

    machine_names: set[str] = set()

    for machine in machines:
        if machine.name in machine_names:
            errors.append(f"Duplicate machine '{machine.name}'.")

        machine_names.add(machine.name)

        hostname = machine.hostname or machine.name

        if not _HOSTNAME_PATTERN.fullmatch(hostname):
            errors.append(
                f"Machine '{machine.name}' has an invalid hostname "
                f"'{hostname}'."
            )

        if not machine.interfaces:
            errors.append(
                f"Machine '{machine.name}' requires at least one interface."
            )

        interface_networks: set[str] = set()

        for interface in machine.interfaces:
            if interface.network_name in interface_networks:
                errors.append(
                    f"Machine '{machine.name}' cannot have multiple "
                    "interfaces on the same network."
                )

            interface_networks.add(interface.network_name)

            if interface.network_name not in network_names:
                errors.append(
                    f"Unknown network '{interface.network_name}' "
                    f"for interface '{interface.name}' "
                    f"on machine '{machine.name}'."
                )
                continue

            subnet = parsed_subnets.get(interface.network_name)

            if subnet is None:
                continue

            try:
                address = ipaddress.ip_address(interface.address)
            except ValueError:
                errors.append(
                    f"Interface '{interface.name}' on machine "
                    f"'{machine.name}' has an invalid address "
                    f"'{interface.address}'."
                )
                continue

            if address not in subnet:
                errors.append(
                    f"Address '{interface.address}' of interface "
                    f"'{interface.name}' on machine '{machine.name}' is "
                    f"outside network '{interface.network_name}'."
                )

        route_destinations: set[str] = set()

        for route in machine.routes:
            if route.destination in route_destinations:
                errors.append(
                    f"Machine '{machine.name}' has a duplicate route to "
                    f"'{route.destination}'."
                )

            route_destinations.add(route.destination)

            try:
                ipaddress.ip_network(route.destination, strict=False)
            except ValueError:
                errors.append(
                    f"Machine '{machine.name}' has an invalid route "
                    f"destination '{route.destination}'."
                )

            if (
                route.network_name is not None
                and route.network_name not in network_names
            ):
                errors.append(
                    f"Route '{route.destination}' on machine "
                    f"'{machine.name}' references unknown network "
                    f"'{route.network_name}'."
                )

            if route.gateway is not None:
                try:
                    ipaddress.ip_address(route.gateway)
                except ValueError:
                    errors.append(
                        f"Route '{route.destination}' on machine "
                        f"'{machine.name}' has an invalid gateway "
                        f"'{route.gateway}'."
                    )

        service_names: set[str] = set()
        service_ports: set[tuple[str, int]] = set()

        for service in machine.services:
            if service.name in service_names:
                errors.append(
                    f"Machine '{machine.name}' declares service "
                    f"'{service.name}' more than once."
                )

            service_names.add(service.name)

            if service.protocol not in _SUPPORTED_SERVICE_PROTOCOLS:
                errors.append(
                    f"Service '{service.name}' on machine "
                    f"'{machine.name}' has an unsupported protocol "
                    f"'{service.protocol}'."
                )

            if not 1 <= service.port <= 65535:
                errors.append(
                    f"Service '{service.name}' on machine "
                    f"'{machine.name}' has an invalid port "
                    f"'{service.port}'."
                )

            key = (service.protocol, service.port)

            if key in service_ports:
                errors.append(
                    f"Machine '{machine.name}' declares service "
                    f"'{service.protocol}/{service.port}' more than once."
                )

            service_ports.add(key)

    return errors


class EnvironmentService:
    """Application service for Sandbox environment lifecycle and provisioning.

    Provisioning follows a deterministic order: validate the definition,
    create networks, create machines (attack + targets), start targets,
    validate targets, start the attack machine, validate everything, and
    only then mark the environment READY. Docker RUNNING is never READY.
    """

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
            EnvironmentState.FAILED,
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

    @staticmethod
    def _limits_for(
        environment: Environment,
        machine_name: str,
    ) -> RuntimeMachineLimits | None:
        """Per-machine limits for lab environments, from the trusted registry."""
        if environment.lab_slug is None:
            return None

        lab = get_lab(environment.lab_slug)

        if lab is None:
            return None

        for lab_machine in lab.machines:
            if lab_machine.name == machine_name:
                return lab_machine.limits

        return None

    @staticmethod
    def _with_route_capability(
        limits: RuntimeMachineLimits | None,
        routes,
    ) -> RuntimeMachineLimits | None:
        """Machines carrying routes need CAP_NET_ADMIN to program them."""
        if not routes:
            return limits

        base = limits or RuntimeMachineLimits()

        if "NET_ADMIN" in base.capabilities:
            return base

        return replace(
            base,
            capabilities=base.capabilities + ("NET_ADMIN",),
        )

    @staticmethod
    def _ordered_for_start(
        machines,
    ) -> list[EnvironmentMachine]:
        """Targets and support machines start before the attack machine."""
        machines = list(machines)
        targets = [m for m in machines if m.role == MachineRole.TARGET]
        others = [
            m
            for m in machines
            if m.role not in (MachineRole.TARGET, MachineRole.ATTACK)
        ]
        attacks = [m for m in machines if m.role == MachineRole.ATTACK]
        return targets + others + attacks

    @staticmethod
    def _machine_runtime_name(environment_id: UUID, name: str) -> str:
        return f"nb-env-{environment_id}-machine-{name}"

    @staticmethod
    def _network_runtime_name(environment_id: UUID, name: str) -> str:
        return f"nb-env-{environment_id}-net-{name}"

    def _start_runtime_machine(self, machine: EnvironmentMachine) -> None:
        if machine.runtime_machine_id is None:
            raise EnvironmentProvisioningError(
                f"Machine '{machine.name}' has no runtime machine."
            )

        machine.state = MachineState.STARTING

        try:
            self.runtime.start_machine(
                machine_id=machine.runtime_machine_id,
            )
        except Exception:
            machine.state = MachineState.FAILED
            raise

        machine.state = MachineState.RUNNING

    def _stop_runtime_machine(self, machine: EnvironmentMachine) -> None:
        if machine.runtime_machine_id is None:
            return

        machine.state = MachineState.STOPPING

        try:
            self.runtime.stop_machine(
                machine_id=machine.runtime_machine_id,
            )
        except Exception:
            machine.state = MachineState.FAILED
            raise

        machine.state = MachineState.STOPPED

    def _configure_spec_routes(
        self,
        machine: EnvironmentMachine,
        machine_spec: MachineSpec,
        network_rows: dict[str, EnvironmentNetwork],
    ) -> None:
        if not machine.routes and not machine_spec.routes:
            return

        if machine.runtime_machine_id is None:
            return

        for route in machine_spec.routes:
            interface_name = None

            if route.network_name is not None:
                interface_name = next(
                    (
                        interface.name
                        for interface in machine_spec.interfaces
                        if interface.network_name == route.network_name
                    ),
                    None,
                )

            self.runtime.configure_route(
                machine_id=machine.runtime_machine_id,
                destination=route.destination,
                gateway=route.gateway,
                interface=interface_name,
            )

    def _configure_persisted_routes(
        self,
        machine: EnvironmentMachine,
    ) -> None:
        if not machine.routes or machine.runtime_machine_id is None:
            return

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

            self.runtime.configure_route(
                machine_id=machine.runtime_machine_id,
                destination=route.destination,
                gateway=route.gateway,
                interface=interface_name,
            )

    async def _record_failure(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
        reason: str,
    ) -> None:
        """Persist a learner-facing failure reason. Never raises."""
        try:
            environment = await self.get_environment(
                environment_id=environment_id,
                learner_id=learner_id,
            )
            environment.failure_reason = reason[:1000]
            await self.repository.commit()
        except Exception:
            pass

    @staticmethod
    def _failure_reason(exc: Exception, fallback: str) -> str:
        if isinstance(exc, SandboxServiceError):
            return str(exc)[:1000]
        return fallback

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

        # Return the graph with networks and machines eagerly loaded so API
        # serialization never triggers lazy loads.
        return await self.get_environment(
            environment_id=created.id,
            learner_id=learner_id,
        )

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

                self._stop_runtime_machine(machine)

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

        started: list[EnvironmentMachine] = []

        try:
            for machine in self._ordered_for_start(environment.machines):
                self._start_runtime_machine(machine)
                started.append(machine)
                # Container routes live in the network namespace, which is
                # recreated on start; program them again.
                self._configure_persisted_routes(machine)

        except Exception as exc:
            for machine in reversed(started):
                try:
                    self.runtime.stop_machine(
                        machine_id=machine.runtime_machine_id,
                    )
                except Exception:
                    pass

            for machine in environment.machines:
                if machine.state in (
                    MachineState.STARTING,
                    MachineState.RUNNING,
                ):
                    machine.state = MachineState.STOPPED

            raise EnvironmentProvisioningError(
                "Failed to start environment machines."
            ) from exc

        result = validate_environment(
            environment=environment,
            runtime=self.runtime,
        )

        if not result.valid:
            for machine in started:
                try:
                    self.runtime.stop_machine(
                        machine_id=machine.runtime_machine_id,
                    )
                except Exception:
                    pass

                machine.state = MachineState.FAILED

            reason = (
                "Environment failed its readiness validation: "
                + "; ".join(result.errors)
            )

            await self._record_failure(
                environment_id=environment_id,
                learner_id=learner_id,
                reason=reason,
            )

            await self.transition(
                environment_id=environment_id,
                learner_id=learner_id,
                target_state=EnvironmentState.FAILED,
            )

            raise EnvironmentProvisioningError(reason)

        for machine in environment.machines:
            machine.state = MachineState.READY

        environment.failure_reason = None

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

        # Runtime resources created during this reset attempt; removed again
        # if any step fails so nothing is left unmanaged.
        new_machine_ids: list[str] = []
        new_network_ids: list[str] = []

        try:
            # Remove the current runtime machines first so their network
            # attachments no longer prevent network removal. The persisted
            # logical definition stays authoritative; stale runtime state is
            # never reused.
            for machine in environment.machines:
                if machine.runtime_machine_id is not None:
                    machine.state = MachineState.RESETTING

            for machine_id in reversed(old_machine_ids):
                self.runtime.stop_machine(machine_id=machine_id)
                self.runtime.remove_machine(machine_id=machine_id)

            for network_id in reversed(old_network_ids):
                self.runtime.remove_network(network_id=network_id)

            # Recreate the networks from the persisted environment topology.
            runtime_network_ids: dict[UUID, str] = {}

            for network in environment.networks:
                runtime_network = self.runtime.create_network(
                    name=self._network_runtime_name(
                        environment_id, network.name
                    ),
                    subnet=network.subnet,
                    gateway=network.gateway,
                )

                runtime_network_ids[network.id] = runtime_network.id
                new_network_ids.append(runtime_network.id)
                network.runtime_network_id = runtime_network.id

            # Recreate every machine using its persisted identity, image and
            # interface configuration.
            for machine in environment.machines:
                attachments = tuple(
                    RuntimeNetworkAttachment(
                        network_id=runtime_network_ids[interface.network_id],
                        ipv4_address=interface.address,
                    )
                    for interface in machine.interfaces
                )

                machine.state = MachineState.CREATING

                limits = self._with_route_capability(
                    self._limits_for(environment, machine.name),
                    machine.routes,
                )

                runtime_machine = self.runtime.create_machine(
                    name=self._machine_runtime_name(
                        environment_id, machine.name
                    ),
                    image=machine.image,
                    network_attachments=attachments,
                    limits=limits,
                    hostname=machine.hostname or machine.name,
                )

                machine.runtime_machine_id = runtime_machine.id
                machine.state = MachineState.CREATED
                new_machine_ids.append(runtime_machine.id)

            targets = [
                machine
                for machine in environment.machines
                if machine.role == MachineRole.TARGET
            ]

            for machine in self._ordered_for_start(environment.machines):
                if machine.role == MachineRole.ATTACK:
                    continue

                self._start_runtime_machine(machine)
                self._configure_persisted_routes(machine)

            if targets:
                target_result = validate_targets(
                    environment=environment,
                    runtime=self.runtime,
                    machines=targets,
                    networks=environment.networks,
                )

                if not target_result.valid:
                    raise EnvironmentProvisioningError(
                        "Target validation failed: "
                        + "; ".join(target_result.errors)
                    )

            for machine in environment.machines:
                if machine.role != MachineRole.ATTACK:
                    continue

                self._start_runtime_machine(machine)
                self._configure_persisted_routes(machine)

            result = validate_environment(
                environment=environment,
                runtime=self.runtime,
            )

            if not result.valid:
                raise EnvironmentProvisioningError(
                    "Environment validation failed: "
                    + "; ".join(result.errors)
                )

            for machine in environment.machines:
                machine.state = MachineState.READY

            if environment.lab_slug is not None:
                await plant_lab_flags(self.runtime, environment)

            environment.failure_reason = None

            await self.repository.commit()

            return await self.transition(
                environment_id=environment_id,
                learner_id=learner_id,
                target_state=EnvironmentState.READY,
            )

        except Exception as exc:
            # Runtime resources created by this attempt cannot be restored by
            # a database rollback; remove them so no orphaned containers or
            # networks remain.
            for machine_id in reversed(new_machine_ids):
                try:
                    self.runtime.stop_machine(machine_id=machine_id)
                except Exception:
                    pass

                try:
                    self.runtime.remove_machine(machine_id=machine_id)
                except Exception:
                    pass

            for network_id in reversed(new_network_ids):
                try:
                    self.runtime.remove_network(network_id=network_id)
                except Exception:
                    pass

            await self.repository.rollback()

            await self._record_failure(
                environment_id=environment_id,
                learner_id=learner_id,
                reason=self._failure_reason(
                    exc, "Environment reset failed."
                ),
            )

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
                machine.state = MachineState.DESTROYED
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
            machine.state = MachineState.DESTROYED

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
            await self._record_failure(
                environment_id=environment_id,
                learner_id=learner_id,
                reason=(
                    "Environment termination failed for one or more "
                    "runtime resources."
                ),
            )

            await self.transition(
                environment_id=environment_id,
                learner_id=learner_id,
                target_state=EnvironmentState.FAILED,
            )

            raise EnvironmentProvisioningError(
                "Environment termination failed for one or more runtime resources."
            ) from errors[0]

        environment.failure_reason = None

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
        network_rows: dict[str, EnvironmentNetwork] = {}
        spec_by_machine: dict[str, MachineSpec] = {
            machine.name: machine for machine in machines
        }

        try:
            # 1. Validate the logical definition before touching the runtime.
            definition_errors = _validate_definition(networks, machines)

            if definition_errors:
                raise EnvironmentProvisioningError(
                    "; ".join(definition_errors)
                )

            # 2. Create the practical networks.
            for network_spec in networks:
                runtime_network = self.runtime.create_network(
                    name=self._network_runtime_name(
                        environment_id, network_spec.name
                    ),
                    subnet=network_spec.subnet,
                    gateway=network_spec.gateway,
                )

                runtime_network_ids[network_spec.name] = runtime_network.id

                network_row = await self.repository.add_network(
                    EnvironmentNetwork(
                        environment_id=environment_id,
                        name=network_spec.name,
                        subnet=network_spec.subnet,
                        gateway=network_spec.gateway,
                        runtime_network_id=runtime_network.id,
                    )
                )

                network_rows[network_spec.name] = network_row

            # 3. Create the attack machine and target machines. Creation
            #    attaches exactly the declared interfaces with the declared
            #    addresses; nothing else.
            for machine_spec in machines:
                network_attachments: list[RuntimeNetworkAttachment] = []

                for interface_spec in machine_spec.interfaces:
                    network = network_rows.get(interface_spec.network_name)

                    if network is None:
                        raise EnvironmentProvisioningError(
                            f"Unknown network '{interface_spec.network_name}' "
                            f"for interface '{interface_spec.name}' "
                            f"on machine '{machine_spec.name}'."
                        )

                    network_attachments.append(
                        RuntimeNetworkAttachment(
                            network_id=runtime_network_ids[
                                interface_spec.network_name
                            ],
                            ipv4_address=interface_spec.address,
                        )
                    )

                limits = self._with_route_capability(
                    machine_spec.limits,
                    machine_spec.routes,
                )

                runtime_machine = self.runtime.create_machine(
                    name=self._machine_runtime_name(
                        environment_id, machine_spec.name
                    ),
                    image=machine_spec.image,
                    network_attachments=tuple(network_attachments),
                    limits=limits,
                    hostname=machine_spec.hostname or machine_spec.name,
                )

                runtime_machine_ids.append(runtime_machine.id)

                machine = EnvironmentMachine(
                    environment_id=environment_id,
                    name=machine_spec.name,
                    role=machine_spec.role,
                    image=machine_spec.image,
                    hostname=machine_spec.hostname or machine_spec.name,
                    runtime_machine_id=runtime_machine.id,
                    state=MachineState.CREATING,
                )

                await self.repository.add_machine(machine)
                machine.state = MachineState.CREATED

                for interface_spec in machine_spec.interfaces:
                    network = network_rows[interface_spec.network_name]

                    await self.repository.add_interface(
                        MachineInterface(
                            machine=machine,
                            network=network,
                            name=interface_spec.name,
                            address=interface_spec.address,
                        )
                    )

                for route_spec in machine_spec.routes:
                    network = (
                        network_rows.get(route_spec.network_name)
                        if route_spec.network_name is not None
                        else None
                    )

                    await self.repository.add_route(
                        MachineRoute(
                            machine=machine,
                            network=network,
                            destination=route_spec.destination,
                            gateway=route_spec.gateway,
                        )
                    )

                for service_spec in machine_spec.services:
                    await self.repository.add_service(
                        MachineService(
                            machine=machine,
                            name=service_spec.name,
                            protocol=service_spec.protocol,
                            port=service_spec.port,
                            required=service_spec.required,
                        )
                    )

            # Reload the persisted graph so validation reads exactly what the
            # database holds (interfaces, routes and services included).
            environment = await self.get_environment(
                environment_id=environment_id,
                learner_id=learner_id,
            )

            targets = [
                machine
                for machine in environment.machines
                if machine.role == MachineRole.TARGET
            ]

            # 4. Start target machines (and any support machines) first,
            #    then program their routes.
            for machine in self._ordered_for_start(environment.machines):
                if machine.role == MachineRole.ATTACK:
                    continue

                self._start_runtime_machine(machine)
                self._configure_spec_routes(
                    machine,
                    spec_by_machine[machine.name],
                    network_rows,
                )

            # 5. Validate the target machines before the attack machine
            #    starts, so a broken target never reaches READY.
            if targets:
                target_result = validate_targets(
                    environment=environment,
                    runtime=self.runtime,
                    machines=targets,
                    networks=environment.networks,
                )

                if not target_result.valid:
                    raise EnvironmentProvisioningError(
                        "Target validation failed: "
                        + "; ".join(target_result.errors)
                    )

            # 6. Start the attack machine and program its routes.
            for machine in self._ordered_for_start(environment.machines):
                if machine.role != MachineRole.ATTACK:
                    continue

                self._start_runtime_machine(machine)
                self._configure_spec_routes(
                    machine,
                    spec_by_machine[machine.name],
                    network_rows,
                )

            # 7. Full validation: runtime state, addresses, routes, target
            #    services, attack-to-target reachability and terminal access.
            result = validate_environment(
                environment=environment,
                runtime=self.runtime,
            )

            if not result.valid:
                raise EnvironmentProvisioningError(
                    "Environment validation failed: "
                    + "; ".join(result.errors)
                )

            # 8. Only now are the machines READY and the environment READY.
            for machine in environment.machines:
                machine.state = MachineState.READY

            environment.failure_reason = None

            await self.repository.commit()

            return await self.transition(
                environment_id=environment_id,
                learner_id=learner_id,
                target_state=EnvironmentState.READY,
            )

        except Exception as exc:
            # Roll back partially-created runtime resources so nothing is
            # left unmanaged.
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

            await self._record_failure(
                environment_id=environment_id,
                learner_id=learner_id,
                reason=self._failure_reason(
                    exc, "Environment provisioning failed."
                ),
            )

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
