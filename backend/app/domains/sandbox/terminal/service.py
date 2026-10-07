from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.errors import ConflictError, NotFoundError
from app.models.sandbox import EnvironmentState, MachineRole, MachineState

from .tickets import TerminalTicketStore, TicketLimitError

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
        *,
        store: TerminalTicketStore,
        repository,
    ) -> None:
        self._store = store
        self._repository = repository

    async def create_session(
        self,
        *,
        learner_id: UUID,
        environment_id: UUID,
        machine_name: str,
        learner_username: str | None = None,
    ) -> TerminalSession:
        environment = await self._repository.get_for_learner(
            environment_id=environment_id,
            learner_id=learner_id,
        )

        if environment is None:
            raise NotFoundError("Environment not found.")

        if environment.state not in (
            EnvironmentState.READY,
            EnvironmentState.ACTIVE,
        ):
            raise ConflictError("Environment is not running.")

        machine = next(
            (
                item
                for item in environment.machines
                if item.name == machine_name
                and item.role == MachineRole.ATTACK
            ),
            None,
        )

        if machine is None:
            raise NotFoundError("Attack machine not found.")

        if not machine.runtime_machine_id:
            raise ConflictError("The attack machine is not available.")

        # Runtime RUNNING is not READY: the machine may only be used after
        # the Sandbox has validated its runtime conditions.
        if machine.state != MachineState.READY:
            raise ConflictError(
                "The attack machine is not ready yet. Try again shortly."
            )

        try:
            ticket_id = self._store.issue(
                learner_id=learner_id,
                learner_username=learner_username,
                environment_id=environment_id,
                machine_name=machine.name,
                runtime_machine_id=machine.runtime_machine_id,
            )
        except TicketLimitError as error:
            raise ConflictError(str(error)) from error

        return TerminalSession(
            session_id=ticket_id,
            expires_in=self._store.ttl_seconds,
        )