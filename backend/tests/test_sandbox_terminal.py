import queue
import time
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from docker.errors import APIError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.errors import ConflictError, NotFoundError
from app.domains.sandbox.dependencies import get_runtime_provider
from app.domains.sandbox.runtime.docker import (
    DockerRuntimeError,
    DockerRuntimeProvider,
)
from app.domains.sandbox.runtime.provider import RuntimeShell
from app.domains.sandbox.terminal import router as terminal_module
from app.domains.sandbox.terminal.service import TerminalService
from app.domains.sandbox.terminal.tickets import TerminalTicketStore
from app.models.sandbox import EnvironmentState, MachineRole

LEARNER = uuid4()


# --------------------------- ticket store ---------------------------------

class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def issue(store, **overrides):
    values = dict(
        learner_id=LEARNER, environment_id=uuid4(),
        machine_name="attacker", runtime_machine_id="container-1",
    )
    values.update(overrides)
    return store.issue(**values)

def test_terminal_opens_with_learner_username(terminal_app):
    client, runtime = terminal_app
    ticket = new_ticket(learner_username="prog_user")
    with client.websocket_connect(f"/sandbox/terminal/{ticket}"):
        pass
    assert runtime.opened_usernames == ["prog_user"]
def test_ticket_is_single_use():
    store = TerminalTicketStore()
    ticket_id = issue(store)

    assert store.redeem(ticket_id) is not None
    assert store.redeem(ticket_id) is None


def test_ticket_expires():
    clock = Clock()
    store = TerminalTicketStore(ttl_seconds=30, clock=clock)
    ticket_id = issue(store)

    clock.now += 31
    assert store.redeem(ticket_id) is None


def test_unknown_ticket_is_rejected():
    assert TerminalTicketStore().redeem("not-a-ticket") is None


def test_ticket_issue_is_capped():
    store = TerminalTicketStore(max_outstanding=2)
    issue(store)
    issue(store)

    with pytest.raises(RuntimeError):
        issue(store)


def test_expired_tickets_free_capacity():
    clock = Clock()
    store = TerminalTicketStore(ttl_seconds=10, max_outstanding=1, clock=clock)
    issue(store)

    clock.now += 11
    issue(store)


# --------------------------- service authorisation ------------------------

class FakeRepository:
    def __init__(self, environment):
        self.environment = environment

    async def get_for_learner(self, *, environment_id, learner_id):
        env = self.environment
        if env.id == environment_id and env.learner_id == learner_id:
            return env
        return None


def make_environment(state=EnvironmentState.READY, runtime_id="c-attacker"):
    return SimpleNamespace(
        id=uuid4(), learner_id=LEARNER, state=state,
        machines=[
            SimpleNamespace(name="attacker", role=MachineRole.ATTACK, runtime_machine_id=runtime_id),
            SimpleNamespace(name="target", role=MachineRole.TARGET, runtime_machine_id="c-target"),
        ],
    )


def make_service(environment):
    store = TerminalTicketStore()
    return TerminalService(repository=FakeRepository(environment), store=store), store


@pytest.mark.asyncio
async def test_owner_gets_a_ticket_for_the_attack_machine():
    environment = make_environment()
    service, store = make_service(environment)

    created = await service.create_session(
        learner_id=LEARNER, environment_id=environment.id, machine_name="attacker"
    )

    ticket = store.redeem(created.session_id)
    assert ticket.learner_id == LEARNER
    assert ticket.environment_id == environment.id
    assert ticket.runtime_machine_id == "c-attacker"
    assert created.expires_in == store.ttl_seconds


@pytest.mark.asyncio
async def test_other_learners_environment_looks_missing():
    environment = make_environment()
    service, _ = make_service(environment)

    with pytest.raises(NotFoundError):
        await service.create_session(
            learner_id=uuid4(), environment_id=environment.id, machine_name="attacker"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("machine_name", ["target", "no-such-machine"])
async def test_learner_cannot_open_a_shell_on_the_target_or_unknown_machines(machine_name):
    environment = make_environment()
    service, store = make_service(environment)

    with pytest.raises(NotFoundError):
        await service.create_session(
            learner_id=LEARNER, environment_id=environment.id, machine_name=machine_name
        )

    assert store._tickets == {}


@pytest.mark.asyncio
@pytest.mark.parametrize("state", [
    EnvironmentState.STOPPED, EnvironmentState.PROVISIONING,
    EnvironmentState.FAILED, EnvironmentState.TERMINATING,
])
async def test_terminal_requires_a_running_environment(state):
    environment = make_environment(state=state)
    service, _ = make_service(environment)

    with pytest.raises(ConflictError):
        await service.create_session(
            learner_id=LEARNER, environment_id=environment.id, machine_name="attacker"
        )


@pytest.mark.asyncio
async def test_terminal_requires_a_runtime_machine():
    environment = make_environment(runtime_id=None)
    service, _ = make_service(environment)

    with pytest.raises(ConflictError):
        await service.create_session(
            learner_id=LEARNER, environment_id=environment.id, machine_name="attacker"
        )


# --------------------------- DockerShell ----------------------------------

def make_docker_provider():
    client = Mock()
    client.containers.get.return_value = Mock(id="container-1")
    client.api.exec_create.return_value = {"Id": "exec-1"}
    stream = Mock()
    stream._sock = Mock()
    client.api.exec_start.return_value = stream
    return DockerRuntimeProvider(client=client), client, stream


def test_open_shell_creates_a_tty_exec_with_stdin():
    provider, client, _ = make_docker_provider()

    provider.open_shell(machine_id="container-1")

    args, kwargs = client.api.exec_create.call_args
    assert args == ("container-1", ["/bin/bash", "-i"])
    assert kwargs["tty"] is True and kwargs["stdin"] is True
    assert kwargs["environment"]["TERM"] == "xterm-256color"
    client.api.exec_start.assert_called_once_with("exec-1", tty=True, socket=True)


def test_open_shell_wraps_docker_errors():
    provider, client, _ = make_docker_provider()
    client.api.exec_create.side_effect = APIError("boom")

    with pytest.raises(DockerRuntimeError, match="Failed to open a shell"):
        provider.open_shell(machine_id="container-1")


def test_docker_shell_reads_writes_resizes_and_closes():
    provider, client, stream = make_docker_provider()
    stream._sock.recv.side_effect = [b"hello", b""]
    shell = provider.open_shell(machine_id="container-1")

    assert shell.read() == b"hello"
    assert shell.read() is None

    shell.write(b"ls\n")
    stream._sock.sendall.assert_called_once_with(b"ls\n")

    shell.resize(120, 40)
    client.api.exec_resize.assert_called_once_with("exec-1", height=40, width=120)

    shell.close()
    shell.close()
    stream._sock.shutdown.assert_called_once()
    assert shell.read() is None


# --------------------------- WebSocket ------------------------------------

class FakeShell(RuntimeShell):
    def __init__(self):
        self.output = queue.Queue()
        self.resizes = []
        self.closed = False

    def read(self):
        return self.output.get()

    def write(self, data):
        self.output.put(b"echo:" + data)

    def resize(self, cols, rows):
        self.resizes.append((cols, rows))

    def close(self):
        self.closed = True
        self.output.put(None)


class FakeTerminalRuntime:
    def __init__(self, fail=False):
        self.fail = fail
        self.shell = FakeShell()
        self.opened = []
        self.opened_usernames = []

    def open_shell(self, *, machine_id, username=None, **kwargs):
        if self.fail:
            raise RuntimeError("no such container")
        self.opened.append(machine_id)
        self.opened_usernames.append(username)
        return self.shell


@pytest.fixture
def terminal_app():
    terminal_module.ticket_store.clear()
    terminal_module._active_sessions.clear()
    runtime = FakeTerminalRuntime()
    app = FastAPI()
    app.include_router(terminal_module.router, prefix="/sandbox")
    app.dependency_overrides[get_runtime_provider] = lambda: runtime
    yield TestClient(app), runtime
    terminal_module.ticket_store.clear()
    terminal_module._active_sessions.clear()


def new_ticket(**overrides):
    values = dict(
        learner_id=LEARNER, environment_id=uuid4(),
        machine_name="attacker", runtime_machine_id="container-1",
    )
    values.update(overrides)
    return terminal_module.ticket_store.issue(**values)


def wait_until(predicate, timeout=3.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return predicate()


def test_websocket_relays_input_and_output(terminal_app):
    client, runtime = terminal_app

    with client.websocket_connect(f"/sandbox/terminal/{new_ticket()}") as ws:
        ws.send_json({"type": "input", "data": "ls\n"})
        assert ws.receive_json() == {"type": "output", "data": "echo:ls\n"}

        ws.send_json({"type": "resize", "cols": 100, "rows": 30})
        assert wait_until(lambda: runtime.shell.resizes == [(100, 30)])

    assert runtime.opened == ["container-1"]
    assert wait_until(lambda: runtime.shell.closed)


def test_websocket_clamps_resize_and_ignores_garbage(terminal_app):
    client, runtime = terminal_app

    with client.websocket_connect(f"/sandbox/terminal/{new_ticket()}") as ws:
        ws.send_text("not json")
        ws.send_text("[1, 2]")
        ws.send_json({"type": "resize", "cols": 99999, "rows": 1})
        ws.send_json({"type": "resize", "cols": "wide", "rows": 10})
        ws.send_json({"type": "input", "data": "x"})
        assert ws.receive_json() == {"type": "output", "data": "echo:x"}

    assert runtime.shell.resizes == [(500, 5)]


def test_websocket_rejects_unknown_ticket(terminal_app):
    client, runtime = terminal_app

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/sandbox/terminal/not-a-ticket"):
            pass

    assert runtime.opened == []


def test_websocket_ticket_cannot_be_reused(terminal_app):
    client, _ = terminal_app
    ticket_id = new_ticket()

    with client.websocket_connect(f"/sandbox/terminal/{ticket_id}"):
        pass

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/sandbox/terminal/{ticket_id}"):
            pass


def test_websocket_rejects_foreign_origin(terminal_app):
    client, runtime = terminal_app

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            f"/sandbox/terminal/{new_ticket()}",
            headers={"origin": "http://evil.example"},
        ):
            pass

    assert runtime.opened == []


def test_websocket_limits_sessions_per_learner(terminal_app):
    client, _ = terminal_app
    terminal_module._active_sessions[LEARNER] = terminal_module.MAX_SESSIONS_PER_LEARNER

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/sandbox/terminal/{new_ticket()}"):
            pass


def test_websocket_reports_a_shell_that_cannot_open(terminal_app):
    client, runtime = terminal_app
    runtime.fail = True

    with client.websocket_connect(f"/sandbox/terminal/{new_ticket()}") as ws:
        message = ws.receive_json()

    assert message["type"] == "error"
    assert "container" not in message["message"]


def test_websocket_reports_when_the_shell_exits(terminal_app):
    client, runtime = terminal_app

    with client.websocket_connect(f"/sandbox/terminal/{new_ticket()}") as ws:
        runtime.shell.output.put(None)
        assert ws.receive_json() == {"type": "exit"}

    assert wait_until(lambda: terminal_module._active_sessions.get(LEARNER) is None)
