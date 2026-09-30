from __future__ import annotations

from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
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

    runtime_machine_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    environment: Mapped[Environment] = relationship(
        back_populates="machines",
    )

    interfaces: Mapped[list["MachineInterface"]] = relationship(
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
