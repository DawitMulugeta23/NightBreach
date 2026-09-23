from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db, AsyncSessionLocal
from db.models import Container, ContainerStatus
from orchestrator.session_manager import get_or_create_session
from orchestrator.provisioning import stop_container
from api.terminal import router as terminal_router
from api.auth import router as auth_router
from api.learning import router as learning_router

# Explicit allowlist of origins permitted to make credentialed requests.
# Add production domains here once deployed — never use "*" with
# allow_credentials=True; browsers reject that combination anyway, and
# an explicit list is the only correct fix.
ALLOWED_ORIGINS = [
    "http://192.168.180.129:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


async def _reconcile_orphaned_containers():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Container).where(Container.status == ContainerStatus.running))
        orphans = result.scalars().all()
        for container in orphans:
            print(f"Reconciling orphaned container {container.id} (port {container.port_number})")
            await stop_container(db, container)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _reconcile_orphaned_containers()
    yield


app = FastAPI(title="NightBreach", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(terminal_router)
app.include_router(auth_router)
app.include_router(learning_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db_status": "ok", "result": result.scalar()}
