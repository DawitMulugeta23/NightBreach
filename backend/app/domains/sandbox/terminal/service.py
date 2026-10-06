from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.models.sandbox import EnvironmentState, MachineRole

from ..repositories.environment_repository import EnvironmentRepository
from .tickets import TerminalTicketStore, TicketLimitError, ticket_store

# Learners get a shell on the attack machine only. They reach the target the
# way an attacker would: over the lab network.
TERMINAL_ROLE = MachineRole.ATTACK
RUNNING_STATES = (EnvironmentState.READY, EnvironmentState.ACTIVE)


@dataclass(frozen=True)
class TerminalSession:
    session_id: str
    expires_in: int


class TerminalService:
    def __init__(
        self,
        session: AsyncSession | None = None,
        *,
        store: TerminalTicketStore = ticket_store,
        repository=None,
    ) -> None:
        self.repository = repository or EnvironmentRepository(session)
        self.store = store

    async def create_session(
        self,
        *,
        learner_id: UUID,
        environment_id: UUID,
        machine_name: str,
    ) -> TerminalSession:
        # Scoped to the learner: a foreign environment looks like a missing one.
        environment = await self.repository.get_for_learner(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment is None:
            raise NotFoundError("Environment not found.")

        machine = next(
            (m for m in environment.machines if m.name == machine_name),
            None,
        )

        if machine is None or machine.role != TERMINAL_ROLE:
            raise NotFoundError("Machine not found.")

        if environment.state not in RUNNING_STATES:
            raise ConflictError("The environment is not running.")

        if machine.runtime_machine_id is None:
            raise ConflictError("The machine is not available.")

        try:
            ticket_id = self.store.issue(
                learner_id=learner_id,
                environment_id=environment.id,
                machine_name=machine.name,
                runtime_machine_id=machine.runtime_machine_id,
            )
        except TicketLimitError as exc:
            raise ConflictError("Too many terminal sessions. Try again shortly.") from exc

        return TerminalSession(
            session_id=ticket_id,
            expires_in=self.store.ttl_seconds,
        )
