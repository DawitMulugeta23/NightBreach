from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class EnvironmentState(str, Enum):
    REQUESTED = "requested"
    PROVISIONING = "provisioning"
    READY = "ready"
    ACTIVE = "active"
    RESETTING = "resetting"
    STOPPED = "stopped"
    TERMINATING = "terminating"
    DESTROYED = "destroyed"
    FAILED = "failed"


class MachineRole(str, Enum):
    ATTACK = "attack"
    TARGET = "target"
    GATEWAY = "gateway"


class MachineState(str, Enum):
    """Lifecycle of a logical Sandbox machine.

    RUNNING means the runtime container was started. READY means the Sandbox
    has validated the machine's runtime conditions (interfaces, addresses,
    routes, services, terminal access). Docker RUNNING is never READY.
    """

    CREATING = "creating"
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    RESETTING = "resetting"
    FAILED = "failed"
    DESTROYED = "destroyed"


class Environment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sandbox_environments"

    learner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    activity_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    state: Mapped[EnvironmentState] = mapped_column(
        SAEnum(
            EnvironmentState,
            name="sandbox_environment_state",
            native_enum=False,
        ),
        nullable=False,
        default=EnvironmentState.REQUESTED,
        server_default=EnvironmentState.REQUESTED.value,
    )

    state_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    # Set only for environments launched from the trusted lab registry.
    lab_slug: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # Per-environment secret used to derive flags. Never returned by the API.
    lab_secret: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    # Learner-facing reason for the last FAILED transition. Cleared on
    # successful provisioning/start/reset. Never contains secrets.
    failure_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    networks: Mapped[list["EnvironmentNetwork"]] = relationship(
        back_populates="environment",
        cascade="all, delete-orphan",
    )

    machines: Mapped[list["EnvironmentMachine"]] = relationship(
        back_populates="environment",
        cascade="all, delete-orphan",
    )


class EnvironmentNetwork(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sandbox_environment_networks"

    environment_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sandbox_environments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    subnet: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    gateway: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    runtime_network_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    environment: Mapped[Environment] = relationship(
        back_populates="networks",
    )

    interfaces: Mapped[list["MachineInterface"]] = relationship(
        back_populates="network",
    )


class EnvironmentMachine(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sandbox_environment_machines"

    environment_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sandbox_environments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    role: Mapped[MachineRole] = mapped_column(
        SAEnum(
            MachineRole,
            name="sandbox_machine_role",
            native_enum=False,
        ),
        nullable=False,
    )

    image: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # Docker container ID (or equivalent). Runtime information only; the
    # database UUID above is the authoritative machine identity.
    runtime_machine_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Logical hostname inside the practical network. Defaults to the machine
    # name; never derived from Docker identifiers.
    hostname: Mapped[str | None] = mapped_column(
        String(63),
        nullable=True,
    )

    state: Mapped[MachineState] = mapped_column(
        SAEnum(
            MachineState,
            name="sandbox_machine_state",
            native_enum=False,
        ),
        nullable=False,
        default=MachineState.CREATING,
        server_default=MachineState.CREATING.value,
    )

    environment: Mapped[Environment] = relationship(
        back_populates="machines",
    )

    interfaces: Mapped[list["MachineInterface"]] = relationship(
        back_populates="machine",
        cascade="all, delete-orphan",
    )

    routes: Mapped[list["MachineRoute"]] = relationship(
        back_populates="machine",
        cascade="all, delete-orphan",
    )

    services: Mapped[list["MachineService"]] = relationship(
        back_populates="machine",
        cascade="all, delete-orphan",
    )


class MachineInterface(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sandbox_machine_interfaces"

    __table_args__ = (
        UniqueConstraint(
            "machine_id",
            "name",
            name="uq_sandbox_machine_interface_name",
        ),
        UniqueConstraint(
            "machine_id",
            "network_id",
            name="uq_sandbox_machine_network",
        ),
    )

    machine_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sandbox_environment_machines.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    network_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sandbox_environment_networks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    machine: Mapped[EnvironmentMachine] = relationship(
        back_populates="interfaces",
    )

    network: Mapped[EnvironmentNetwork] = relationship(
        back_populates="interfaces",
    )


class MachineRoute(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A route the Sandbox configures on a logical machine.

    Routes come from the environment/Target definition, never from client
    runtime identifiers.
    """

    __tablename__ = "sandbox_machine_routes"

    __table_args__ = (
        UniqueConstraint(
            "machine_id",
            "destination",
            name="uq_sandbox_machine_route_destination",
        ),
    )

    machine_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sandbox_environment_machines.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # The environment network this route is reachable through (its interface
    # carries the route). Optional for routes that only name a gateway.
    network_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "sandbox_environment_networks.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    # CIDR destination, e.g. "10.30.0.0/24".
    destination: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    gateway: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    machine: Mapped[EnvironmentMachine] = relationship(
        back_populates="routes",
    )

    network: Mapped[EnvironmentNetwork | None] = relationship()


class MachineService(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A service a machine's runtime specification requires.

    Describes WHAT must be reachable so the Sandbox can validate readiness.
    Building the service into the image belongs to the Target Build System.
    """

    __tablename__ = "sandbox_machine_services"

    __table_args__ = (
        UniqueConstraint(
            "machine_id",
            "protocol",
            "port",
            name="uq_sandbox_machine_service_port",
        ),
    )

    machine_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sandbox_environment_machines.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    protocol: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="tcp",
        server_default="tcp",
    )

    port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    machine: Mapped[EnvironmentMachine] = relationship(
        back_populates="services",
    )
