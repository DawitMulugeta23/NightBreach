import asyncio

import docker
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from db.session import AsyncSessionLocal
from db.models import Container, ContainerStatus, User
from core.security import decode_access_token
from orchestrator.session_manager import get_or_create_session
from orchestrator.provisioning import provision_container, stop_container
from orchestrator.terminal import create_exec_socket
from orchestrator.teardown_registry import schedule_teardown, cancel_teardown

router = APIRouter()

TEARDOWN_GRACE_SECONDS = 60

_docker_client = docker.from_env()


def _container_still_exists(container_id: str) -> bool:
    """Return True only if Docker still knows about this container."""
    if not container_id:
        return False
    try:
        _docker_client.containers.get(container_id)
        return True
    except docker.errors.NotFound:
        return False
    except Exception as e:
        print(f"WARNING: docker lookup failed for {container_id}: {e}")
        return False


async def _get_or_provision_running_container(db, session, username):
    """
    Finds the session's running container if it still exists in Docker;
    otherwise marks the stale row stopped, releases its port, and provisions
    a fresh container.
    """
    for c in session.containers:
        if c.status == ContainerStatus.running:
            if _container_still_exists(c.docker_container_id):
                return c
            # Stale DB row — container no longer exists in Docker
            print(f"WARNING: container {c.docker_container_id[:12] if c.docker_container_id else '?'} "
                  f"marked running but missing in Docker; cleaning up")
            await stop_container(db, c)
            # stop_container raises on Docker errors? no — it logs and continues.

    # No valid running container — provision a new one
    return await provision_container(db, session, username)


@router.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket, token: str):
    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    loop = asyncio.get_event_loop()

    async with AsyncSessionLocal() as db:
        session = await get_or_create_session(db, user_id)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        username = user.username if user else "player"

        try:
            container = await _get_or_provision_running_container(db, session, username)
        except Exception as e:
            print(f"ERROR: failed to provision container: {e}")
            await websocket.send_text(f"\r\n\x1b[31mFailed to start container: {e}\x1b[0m\r\n")
            await websocket.close()
            return

    cancel_teardown(str(session.id))

    try:
        sock = await loop.run_in_executor(
            None, create_exec_socket, container.docker_container_id, username
        )
    except Exception as e:
        print(f"ERROR: create_exec_socket failed for {container.docker_container_id}: {e}")
        await websocket.send_text(f"\r\n\x1b[31mFailed to attach to container: {e}\x1b[0m\r\n")
        await websocket.close()
        return

    async def read_from_container():
        try:
            while True:
                data = await loop.run_in_executor(None, sock.recv, 4096)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception:
            pass

    reader_task = asyncio.create_task(read_from_container())

    try:
        while True:
            data = await websocket.receive_text()
            await loop.run_in_executor(None, sock.send, data.encode())
    except WebSocketDisconnect:
        pass
    finally:
        reader_task.cancel()
        try:
            sock.close()
        except Exception:
            pass

        async def _do_teardown():
            async with AsyncSessionLocal() as db:
                await stop_container(db, container)

        schedule_teardown(str(session.id), _do_teardown, TEARDOWN_GRACE_SECONDS)
