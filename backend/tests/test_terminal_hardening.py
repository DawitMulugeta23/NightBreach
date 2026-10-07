from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import ConflictError
from app.domains.sandbox.terminal.service import TerminalService
from app.domains.sandbox.terminal.tickets import TerminalTicketStore, TicketLimitError
from app.models.sandbox import EnvironmentState, MachineRole, MachineState


def issue(store, learner):
    return store.issue(
        learner_id=learner,
        environment_id=uuid4(),
        machine_name="attacker",
        runtime_machine_id="rt-1",
    )


def test_one_learner_cannot_exhaust_the_ticket_store():
    store = TerminalTicketStore(max_per_learner=2, max_outstanding=100)
    learner = uuid4()
    issue(store, learner)
    issue(store, learner)

    with pytest.raises(TicketLimitError):
        issue(store, learner)

    issue(store, uuid4())  # other learners are unaffected


def test_redeeming_a_ticket_frees_capacity():
    store = TerminalTicketStore(max_per_learner=1)
    learner = uuid4()
    ticket = issue(store, learner)

    assert store.redeem(ticket) is not None
    issue(store, learner)


def test_expired_tickets_do_not_count_against_the_limit():
    now = [0.0]
    store = TerminalTicketStore(max_per_learner=1, ttl_seconds=30, clock=lambda: now[0])
    learner = uuid4()
    issue(store, learner)

    now[0] = 31.0
    issue(store, learner)


def test_global_limit_is_still_enforced():
    store = TerminalTicketStore(max_outstanding=2, max_per_learner=10)
    issue(store, uuid4())
    issue(store, uuid4())

    with pytest.raises(TicketLimitError):
        issue(store, uuid4())


class FakeRepository:
    def __init__(self, environment):
        self.environment = environment

    async def get_for_learner(self, *, environment_id, learner_id):
        return self.environment


@pytest.mark.asyncio
async def test_service_reports_the_ticket_limit_as_a_conflict():
    learner = uuid4()
    environment = SimpleNamespace(
        id=uuid4(),
        state=EnvironmentState.READY,
        machines=[
            SimpleNamespace(
                name="attacker",
                role=MachineRole.ATTACK,
                runtime_machine_id="rt-1",
                state=MachineState.READY,
            )
        ],
    )
    service = TerminalService(
        store=TerminalTicketStore(max_per_learner=1),
        repository=FakeRepository(environment),
    )

    await service.create_session(
        learner_id=learner, environment_id=environment.id, machine_name="attacker"
    )

    with pytest.raises(ConflictError):
        await service.create_session(
            learner_id=learner, environment_id=environment.id, machine_name="attacker"
        )
