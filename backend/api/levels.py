import hashlib

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.models import Level, UserProgress, ContainerStatus, User
from core.security import decode_access_token
from orchestrator.session_manager import get_or_create_session
from orchestrator.provisioning import provision_container
from orchestrator.terminal import get_docker_client

_docker_client = get_docker_client()

router = APIRouter(prefix="/levels", tags=["levels"])


def _hash_flag(flag: str) -> str:
    return hashlib.sha256(flag.strip().encode()).hexdigest()


async def _get_current_user_id(token: str) -> str:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return user_id


class LevelSummary(BaseModel):
    id: str
    tier: int
    level_number: int
    title: str
    completed: bool


class LevelDetail(BaseModel):
    id: str
    tier: int
    level_number: int
    title: str
    description: str
    completed: bool


class FlagSubmission(BaseModel):
    flag: str


@router.get("", response_model=list[LevelSummary])
async def list_levels(token: str, db: AsyncSession = Depends(get_db)):
    user_id = await _get_current_user_id(token)

    result = await db.execute(select(Level).order_by(Level.tier, Level.level_number))
    levels = result.scalars().all()

    result = await db.execute(select(UserProgress.level_id).where(UserProgress.user_id == user_id))
    completed_ids = {row[0] for row in result.all()}

    return [
        LevelSummary(
            id=str(lvl.id),
            tier=lvl.tier,
            level_number=lvl.level_number,
            title=lvl.title,
            completed=lvl.id in completed_ids,
        )
        for lvl in levels
    ]


@router.post("/{level_id}/start", response_model=LevelDetail)
async def start_level(level_id: str, token: str, db: AsyncSession = Depends(get_db)):
    user_id = await _get_current_user_id(token)

    result = await db.execute(select(Level).where(Level.id == level_id))
    level = result.scalar_one_or_none()
    if level is None:
        raise HTTPException(status_code=404, detail="Level not found")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    username = user.username if user else "player"

    session = await get_or_create_session(db, user_id)
    container = None
    for c in session.containers:
        if c.status == ContainerStatus.running:
            container = c
            break
    if container is None:
        container = await provision_container(db, session, username)

    setup_script = level.setup_script.replace("/home/player", f"/home/{username}").replace("player:player", f"{username}:{username}")

    exec_id = _docker_client.api.exec_create(
        container.docker_container_id,
        ["/bin/bash", "-c", setup_script],
        user="root",
    )["Id"]
    output = _docker_client.api.exec_start(exec_id)
    inspect = _docker_client.api.exec_inspect(exec_id)
    exit_code = inspect.get("ExitCode")
    print(f"LEVEL SETUP: level={level.level_number} container={container.docker_container_id[:12]} exit_code={exit_code} output={output!r}")

    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id, UserProgress.level_id == level.id)
    )
    completed = result.scalar_one_or_none() is not None

    return LevelDetail(
        id=str(level.id),
        tier=level.tier,
        level_number=level.level_number,
        title=level.title,
        description=level.description,
        completed=completed,
    )


@router.post("/{level_id}/submit")
async def submit_flag(level_id: str, token: str, payload: FlagSubmission, db: AsyncSession = Depends(get_db)):
    user_id = await _get_current_user_id(token)

    result = await db.execute(select(Level).where(Level.id == level_id))
    level = result.scalar_one_or_none()
    if level is None:
        raise HTTPException(status_code=404, detail="Level not found")

    if _hash_flag(payload.flag) != level.flag_hash:
        return {"correct": False}

    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id, UserProgress.level_id == level.id)
    )
    if result.scalar_one_or_none() is None:
        db.add(UserProgress(user_id=user_id, level_id=level.id))
        await db.commit()

    return {"correct": True}
