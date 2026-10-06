from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI

from app.config import get_settings
from app.db.session import AsyncSessionLocal
from app.domains.sandbox.runtime.docker import DockerRuntimeProvider
from app.domains.sandbox.workers.sweeper import DatabaseSweepTarget, LabSweeper

logger = logging.getLogger("nightbreach.lifespan")


def build_lab_sweeper() -> LabSweeper:
    settings = get_settings()

    return LabSweeper(
        DatabaseSweepTarget(
            AsyncSessionLocal,
            DockerRuntimeProvider,
            stuck_after=timedelta(minutes=settings.lab_stuck_minutes),
        ),
        interval_seconds=settings.lab_sweep_interval_seconds,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = None

    if get_settings().lab_sweep_enabled:
        task = asyncio.create_task(build_lab_sweeper().run(), name="lab-sweeper")
    else:
        logger.info("Lab sweeper is disabled")

    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
