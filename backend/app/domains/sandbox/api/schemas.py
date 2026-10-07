from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.sandbox import Environment, EnvironmentState, MachineRole, MachineState

from ..validators.environment import (
    EnvironmentValidationResult,
    MachineValidationResult,
)


class CreateEnvironmentRequest(BaseModel):
    activity_id: str = Field(min_length=1, max_length=255)


class InterfaceSpecRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    network_name: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=64)


class NetworkSpecRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    subnet: str = Field(min_length=1, max_length=64)
    gateway: str = Field(min_length=1, max_length=64)


class RouteSpecRequest(BaseModel):
    destination: str = Field(min_length=1, max_length=64)
    gateway: str | None = Field(default=None, max_length=64)
    network_name: str | None = Field(default=None, max_length=100)


class ServiceSpecRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    port: int = Field(ge=1, le=65535)
    protocol: str = Field(default="tcp", max_length=10)
    required: bool = True


class MachineSpecRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    role: MachineRole
    image: str = Field(min_length=1, max_length=500)
    interfaces: list[InterfaceSpecRequest] = Field(min_length=1)
    hostname: str | None = Field(default=None, max_length=63)
    routes: list[RouteSpecRequest] = Field(default_factory=list)
    services: list[ServiceSpecRequest] = Field(default_factory=list)


class ProvisionEnvironmentRequest(BaseModel):
    networks: list[NetworkSpecRequest] = Field(min_length=1)
    machines: list[MachineSpecRequest] = Field(min_length=1)


class MachineServiceStatus(BaseModel):
    name: str
    protocol: str
    port: int
    required: bool
    ready: bool


class MachineStatusResponse(BaseModel):
    """Logical machine status derived from the Sandbox database.

    ``state`` only reaches READY after runtime validation succeeded; Docker's
    container state alone never makes a machine READY.
    """

    id: UUID
    name: str
    role: MachineRole
    image: str
    state: MachineState
    hostname: str | None = None
    terminal_ready: bool = False
    services: list[MachineServiceStatus] = Field(default_factory=list)

    @classmethod
    def from_machine(cls, machine) -> "MachineStatusResponse":
        ready = machine.state == MachineState.READY

        return cls(
            id=machine.id,
            name=machine.name,
            role=machine.role,
            image=machine.image,
            state=machine.state,
            hostname=machine.hostname,
            terminal_ready=(
                machine.role == MachineRole.ATTACK and ready
            ),
            services=[
                MachineServiceStatus(
                    name=service.name,
                    protocol=service.protocol,
                    port=service.port,
                    required=service.required,
                    ready=ready,
                )
                for service in sorted(
                    machine.services,
                    key=lambda service: (service.protocol, service.port),
                )
            ],
        )


class NetworkStatusResponse(BaseModel):
    id: UUID
    name: str
    subnet: str | None = None
    gateway: str | None = None
    ready: bool = False


class EnvironmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    learner_id: UUID
    activity_id: str
    state: EnvironmentState
    state_version: int
    failure_reason: str | None = None

    # Readiness information for the frontend: the learner-controlled attack
    # machine, the platform-controlled targets and the practical networks.
    networks: list[NetworkStatusResponse] = Field(default_factory=list)
    attack_machine: MachineStatusResponse | None = None
    targets: list[MachineStatusResponse] = Field(default_factory=list)

    @classmethod
    def from_environment(cls, environment: Environment) -> "EnvironmentResponse":
        attack_machine = next(
            (
                machine
                for machine in environment.machines
                if machine.role == MachineRole.ATTACK
            ),
            None,
        )

        return cls(
            id=environment.id,
            learner_id=environment.learner_id,
            activity_id=environment.activity_id,
            state=environment.state,
            state_version=environment.state_version,
            failure_reason=environment.failure_reason,
            networks=[
                NetworkStatusResponse(
                    id=network.id,
                    name=network.name,
                    subnet=network.subnet,
                    gateway=network.gateway,
                    ready=network.runtime_network_id is not None,
                )
                for network in environment.networks
            ],
            attack_machine=(
                MachineStatusResponse.from_machine(attack_machine)
                if attack_machine is not None
                else None
            ),
            targets=[
                MachineStatusResponse.from_machine(machine)
                for machine in environment.machines
                if machine.role == MachineRole.TARGET
            ],
        )


class NetworkReadinessResponse(BaseModel):
    id: UUID
    name: str
    ready: bool = False
    errors: list[str] = Field(default_factory=list)


class MachineReadinessResponse(BaseModel):
    id: UUID
    name: str
    role: MachineRole
    state: MachineState | None = None
    ready: bool = False
    terminal_ready: bool = False
    services: list[MachineServiceStatus] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @classmethod
    def from_result(
        cls, result: MachineValidationResult
    ) -> "MachineReadinessResponse":
        return cls(
            id=result.machine_id,
            name=result.name,
            role=result.role,
            state=result.state,
            ready=result.ready,
            terminal_ready=result.terminal_ready,
            services=[
                MachineServiceStatus(
                    name=service.name,
                    protocol=service.protocol,
                    port=service.port,
                    required=service.required,
                    ready=service.ready,
                )
                for service in result.services
            ],
            errors=list(result.errors),
        )


class EnvironmentValidationResponse(BaseModel):
    environment_id: UUID
    valid: bool
    errors: list[str] = Field(default_factory=list)

    networks: list[NetworkReadinessResponse] = Field(default_factory=list)
    attack_machine: MachineReadinessResponse | None = None
    targets: list[MachineReadinessResponse] = Field(default_factory=list)

    @classmethod
    def from_result(
        cls,
        *,
        environment_id: UUID,
        result: EnvironmentValidationResult,
    ) -> "EnvironmentValidationResponse":
        return cls(
            environment_id=environment_id,
            valid=result.valid,
            errors=list(result.errors),
            networks=[
                NetworkReadinessResponse(
                    id=network.network_id,
                    name=network.name,
                    ready=network.ready,
                    errors=list(network.errors),
                )
                for network in result.networks
            ],
            attack_machine=(
                MachineReadinessResponse.from_result(result.attack_machine)
                if result.attack_machine is not None
                else None
            ),
            targets=[
                MachineReadinessResponse.from_result(target)
                for target in result.targets
            ],
        )
