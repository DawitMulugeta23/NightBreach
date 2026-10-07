from __future__ import annotations

import asyncio
import codecs
import json
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User

from ..dependencies import get_runtime_provider
from ..repositories.environment_repository import EnvironmentRepository
from ..runtime.provider import RuntimeProvider
from .service import TerminalService
from .tickets import ticket_store

router = APIRouter()

IDLE_TIMEOUT_SECONDS = 15 * 60
MAX_MESSAGE_CHARS = 8192
MAX_SESSIONS_PER_LEARNER = 3
MAX_TOTAL_SESSIONS = 48

# Every open terminal pins one thread in a blocking read. A dedicated pool keeps
# that from starving the shared default executor used by lab launch and reset.
_SHELL_EXECUTOR = ThreadPoolExecutor(
    max_workers=MAX_TOTAL_SESSIONS,
    thread_name_prefix="terminal-read",
)

_active_sessions: dict[UUID, int] = defaultdict(int)


class TerminalSessionResponse(BaseModel):
    session_id: str
    expires_in: int


@router.post(
    "/environments/{environment_id}/machines/{machine_name}/terminal-sessions",
    response_model=TerminalSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_terminal_session(
    environment_id: UUID,
    machine_name: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> TerminalSessionResponse:
    created = await TerminalService(
        store=ticket_store,
        repository=EnvironmentRepository(session),
    ).create_session(
        learner_id=current_user.id,
        # The prompt identity is derived server-side from the authenticated
        # learner; the client never supplies it.
        learner_username=current_user.username,
        environment_id=environment_id,
        machine_name=machine_name,
    )
    return TerminalSessionResponse(
        session_id=created.session_id,
        expires_in=created.expires_in,
    )


def _origin_allowed(origin: str | None) -> bool:
    # Browsers always send Origin on WebSocket handshakes; refusing unknown
    # origins stops other websites from driving a learner's terminal. Clients
    # without an Origin still need a valid single-use ticket.
    if origin is None:
        return True

    allowed = {
        item.strip().rstrip("/")
        for item in get_settings().cors_origins.split(",")
        if item.strip()
    }
    return origin.rstrip("/") in allowed


async def _pump_output(websocket: WebSocket, shell) -> None:
    decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")

    while True:
        chunk = await asyncio.get_running_loop().run_in_executor(
            _SHELL_EXECUTOR, shell.read
        )

        if chunk is None:
            await websocket.send_json({"type": "exit"})
            return

        text = decoder.decode(chunk)

        if text:
            await websocket.send_json({"type": "output", "data": text})


async def _pump_input(websocket: WebSocket, shell) -> None:
    while True:
        raw = await asyncio.wait_for(
            websocket.receive_text(),
            timeout=IDLE_TIMEOUT_SECONDS,
        )

        if len(raw) > MAX_MESSAGE_CHARS:
            continue

        try:
            message = json.loads(raw)
        except ValueError:
            continue

        if not isinstance(message, dict):
            continue

        kind = message.get("type")

        if kind == "input":
            data = message.get("data")

            if isinstance(data, str) and data:
                await asyncio.to_thread(shell.write, data.encode("utf-8"))

        elif kind == "resize":
            cols, rows = message.get("cols"), message.get("rows")

            if (
                type(cols) is int
                and type(rows) is int
            ):
                await asyncio.to_thread(
                    shell.resize,
                    min(max(cols, 20), 500),
                    min(max(rows, 5), 200),
                )


async def _close_quietly(websocket: WebSocket, code: int) -> None:
    try:
        await websocket.close(code=code)
    except Exception:
        pass


@router.websocket("/terminal/{ticket_id}")
async def terminal_socket(
    websocket: WebSocket,
    ticket_id: str,
    runtime: RuntimeProvider = Depends(get_runtime_provider),
) -> None:
    if not _origin_allowed(websocket.headers.get("origin")):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    ticket = ticket_store.redeem(ticket_id)

    if ticket is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if (
        _active_sessions.get(ticket.learner_id, 0) >= MAX_SESSIONS_PER_LEARNER
        or sum(_active_sessions.values()) >= MAX_TOTAL_SESSIONS
    ):
        await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
        return

    # Count the session before the first await so concurrent connections
    # cannot slip past the limits.
    _active_sessions[ticket.learner_id] += 1
    shell = None

    try:
        await websocket.accept()

        try:
            # The shell inherits the Attack Machine's identity and network
            # context; the ticket carries the learner prompt username.
            shell = await asyncio.to_thread(
                runtime.open_shell,
                machine_id=ticket.runtime_machine_id,
                username=ticket.learner_username,
            )
        except Exception:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "Could not open a shell on this machine.",
                }
            )
            return

        reader = asyncio.create_task(_pump_output(websocket, shell))
        writer = asyncio.create_task(_pump_input(websocket, shell))

        done, pending = await asyncio.wait(
            {reader, writer},
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        # Closing the shell wakes a thread that is blocked reading it.
        await asyncio.to_thread(shell.close)
        await asyncio.gather(*pending, return_exceptions=True)

        for task in done:
            error = task.exception()

            if isinstance(error, asyncio.TimeoutError):
                try:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Session closed due to inactivity.",
                        }
                    )
                except Exception:
                    pass
    except WebSocketDisconnect:
        pass
    finally:
        _active_sessions[ticket.learner_id] -= 1

        if _active_sessions[ticket.learner_id] <= 0:
            _active_sessions.pop(ticket.learner_id, None)

        if shell is not None:
            await asyncio.to_thread(shell.close)

        await _close_quietly(websocket, status.WS_1000_NORMAL_CLOSURE)
