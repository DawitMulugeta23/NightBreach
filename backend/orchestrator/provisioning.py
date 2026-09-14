import asyncio

import docker
from docker.errors import DockerException, NotFound
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Container, ContainerStatus, Session
from orchestrator.ports import claim_port, release_port

BASE_IMAGE = "mde-base:v1"
CONTAINER_INTERNAL_PORT = "22/tcp"

MAX_PORT_CLAIM_RETRIES = 5
RETRY_DELAY_SECONDS = 1.0

_docker_client = docker.from_env()


async def _claim_port_with_retry(db: AsyncSession) -> int:
    for attempt in range(1, MAX_PORT_CLAIM_RETRIES + 1):
        port = await claim_port(db)
        if port is not None:
            return port
        if attempt < MAX_PORT_CLAIM_RETRIES:
            await asyncio.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError("Port pool exhausted after retries — no free port available")


async def provision_container(
    db: AsyncSession, session: Session, username: str, command: list[str] | None = None
) -> Container:
    port_number = await _claim_port_with_retry(db)

    container_row = Container(
        session_id=session.id,
        image=BASE_IMAGE,
        status=ContainerStatus.provisioning,
        port_number=port_number,
    )
    db.add(container_row)
    await db.commit()
    await db.refresh(container_row)

    try:
        run_kwargs = dict(
            detach=True,
            tty=True,
            ports={CONTAINER_INTERNAL_PORT: port_number},
            name=f"mde-session-{session.id}",
        )
        if command is not None:
            run_kwargs["command"] = command

        docker_container = _docker_client.containers.run(BASE_IMAGE, **run_kwargs)
    except DockerException as e:
        await release_port(db, port_number)
        container_row.status = ContainerStatus.error
        await db.commit()
        raise RuntimeError(f"Failed to start container: {e}") from e

    container_row.docker_container_id = docker_container.id
    container_row.status = ContainerStatus.running
    await db.commit()
    await db.refresh(container_row)

    ensure_user_account(docker_container.id, username)

    return container_row


async def stop_container(db: AsyncSession, container: Container) -> None:
    """
    Stops and removes the Docker container (if it still exists), releases its
    port back to the pool, and marks the row stopped. Idempotent — safe to
    call on already-stopped or already-deleted containers.
    """
    if container.docker_container_id is not None:
        try:
            docker_container = _docker_client.containers.get(container.docker_container_id)
            docker_container.stop(timeout=5)
            docker_container.remove()
        except NotFound:
            # Container already gone — that's fine, just update the DB.
            pass
        except DockerException as e:
            print(f"WARNING: failed to stop/remove container {container.docker_container_id}: {e}")

    if container.port_number is not None:
        await release_port(db, container.port_number)

    container.status = ContainerStatus.stopped
    await db.commit()


def ensure_user_account(container_id: str, username: str) -> None:
    exec_id = _docker_client.api.exec_create(
        container_id,
        ["useradd", "-m", "-s", "/bin/bash", username],
        user="root",
    )["Id"]
    _docker_client.api.exec_start(exec_id)

    exec_id = _docker_client.api.exec_create(
        container_id,
        ["usermod", "-aG", "sudo", username],
        user="root",
    )["Id"]
    _docker_client.api.exec_start(exec_id)
