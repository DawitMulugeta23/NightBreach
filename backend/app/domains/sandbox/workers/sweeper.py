"""Background cleanup of expired and stuck lab environments.

Cleanup goes through EnvironmentService.terminate_environment, the same path
as a learner pressing "End lab", so containers, networks and state are handled
in exactly one place.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Protocol
from uuid import UUID

from sqlalchemy import and_, or_, select

from app.models.sandbox import Environment, EnvironmentState

from ..runtime.provider import RuntimeProvider
from ..services.environment_service import EnvironmentService

logger = logging.getLogger("nightbreach.sandbox.sweeper")

BATCH_SIZE = 50

# States from which terminate_environment is allowed.
CLEANUP_STATES = (
    EnvironmentState.REQUESTED,
    EnvironmentState.PROVISIONING,
    EnvironmentState.READY,
    EnvironmentState.ACTIVE,
    EnvironmentState.RESETTING,
    EnvironmentState.STOPPED,
    EnvironmentState.FAILED,
)

# States that should never last long. If one has not changed for a while the
# request that owned it has died, so the environment is cleaned up.
STUCK_STATES = (
    EnvironmentState.REQUESTED,
    EnvironmentState.PROVISIONING,
    EnvironmentState.RESETTING,
    EnvironmentState.FAILED,
)


@dataclass(frozen=True)
class DueEnvironment:
    environment_id: UUID
    learner_id: UUID


@dataclass(frozen=True)
class SweepResult:
    terminated: int
    failed: int


class SweepTarget(Protocol):
    async def find_due(self, *, now: datetime) -> list[DueEnvironment]: ...

    async def terminate(self, due: DueEnvironment) -> None: ...


class LabSweeper:
    def __init__(
        self,
        target: SweepTarget,
        *,
        interval_seconds: float = 60,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.target = target
        self.interval_seconds = interval_seconds
        self._clock = clock

    async def sweep_once(self) -> SweepResult:
        terminated = failed = 0

        for due in await self.target.find_due(now=self._clock()):
            try:
                await self.target.terminate(due)
                terminated += 1
                logger.info("Terminated lab environment %s", due.environment_id)
            except Exception:
                failed += 1
                logger.exception(
                    "Could not terminate lab environment %s", due.environment_id
                )

        return SweepResult(terminated=terminated, failed=failed)

    async def run(self) -> None:
        logger.info("Lab sweeper started (every %ss)", self.interval_seconds)

        while True:
            try:
                await self.sweep_once()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Lab sweep failed")

            await asyncio.sleep(self.interval_seconds)


class DatabaseSweepTarget:
    def __init__(
        self,
        session_factory,
        runtime_factory: Callable[[], RuntimeProvider],
        *,
        stuck_after: timedelta = timedelta(minutes=15),
    ) -> None:
        self._session_factory = session_factory
        self._runtime_factory = runtime_factory
        self._stuck_after = stuck_after
        self._runtime: RuntimeProvider | None = None

    def _get_runtime(self) -> RuntimeProvider:
        if self._runtime is None:
            self._runtime = self._runtime_factory()
        return self._runtime

    async def find_due(self, *, now: datetime) -> list[DueEnvironment]:
        stuck_before = now - self._stuck_after

        statement = (
            select(Environment.id, Environment.learner_id)
            .where(
                Environment.lab_slug.is_not(None),
                Environment.state.in_(CLEANUP_STATES),
                or_(
                    Environment.expires_at <= now,
                    and_(
                        Environment.state.in_(STUCK_STATES),
                        Environment.updated_at <= stuck_before,
                    ),
                ),
            )
            .order_by(Environment.created_at)
            .limit(BATCH_SIZE)
        )

        async with self._session_factory() as session:
            rows = (await session.execute(statement)).all()

        return [DueEnvironment(row.id, row.learner_id) for row in rows]

    async def terminate(self, due: DueEnvironment) -> None:
        async with self._session_factory() as session:
            service = EnvironmentService(
                session=session,
                runtime=self._get_runtime(),
            )
            await service.terminate_environment(
                environment_id=due.environment_id,
                learner_id=due.learner_id,
            )
