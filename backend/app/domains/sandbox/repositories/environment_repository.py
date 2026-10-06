from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sandbox import (
    Environment,
    EnvironmentMachine,
    EnvironmentNetwork,
    EnvironmentState,
    MachineInterface,
)


class EnvironmentRepository:
    """Persistence operations for Sandbox environments."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        environment_id: UUID,
    ) -> Environment | None:
        result = await self.session.execute(
            select(Environment).where(
                Environment.id == environment_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_for_learner(
        self,
        *,
        environment_id: UUID,
        learner_id: UUID,
    ) -> Environment | None:
        result = await self.session.execute(
            select(Environment)
            .execution_options(populate_existing=True)
            .options(
                selectinload(Environment.networks),
                selectinload(Environment.machines).selectinload(
                    EnvironmentMachine.interfaces
                ),
            )
            .where(
                Environment.id == environment_id,
                Environment.learner_id == learner_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        environment: Environment,
    ) -> Environment:
        self.session.add(environment)
        await self.session.flush()
        await self.session.refresh(environment)
        return environment

    async def add_network(
        self,
        network: EnvironmentNetwork,
    ) -> EnvironmentNetwork:
        self.session.add(network)
        await self.session.flush()
        await self.session.refresh(network)
        return network

    async def get_network_by_name(
        self,
        *,
        environment_id: UUID,
        name: str,
    ) -> EnvironmentNetwork | None:
        result = await self.session.execute(
            select(EnvironmentNetwork).where(
                EnvironmentNetwork.environment_id == environment_id,
                EnvironmentNetwork.name == name,
            )
        )
        return result.scalar_one_or_none()

    async def add_machine(
        self,
        machine: EnvironmentMachine,
    ) -> EnvironmentMachine:
        self.session.add(machine)
        await self.session.flush()
        await self.session.refresh(machine)
        return machine

    async def add_interface(
        self,
        interface: MachineInterface,
    ) -> MachineInterface:
        self.session.add(interface)
        await self.session.flush()
        await self.session.refresh(interface)
        return interface

    async def list_live_lab_environments(
        self,
        *,
        learner_id: UUID,
    ) -> list[Environment]:
        result = await self.session.execute(
            select(Environment).where(
                Environment.learner_id == learner_id,
                Environment.lab_slug.is_not(None),
                Environment.state.not_in(
                    (
                        EnvironmentState.DESTROYED,
                        EnvironmentState.FAILED,
                        EnvironmentState.TERMINATING,
                    )
                ),
            )
        )
        return list(result.scalars().all())

    async def list_allocated_subnets(self) -> set[str]:
        """Subnets whose runtime network still exists."""
        result = await self.session.execute(
            select(EnvironmentNetwork.subnet).where(
                EnvironmentNetwork.runtime_network_id.is_not(None),
                EnvironmentNetwork.subnet.is_not(None),
            )
        )
        return set(result.scalars().all())

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
