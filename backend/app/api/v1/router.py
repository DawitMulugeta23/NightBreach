from fastapi import APIRouter

from app.domains.identity.router import router as identity_router
from app.domains.learning.router import (
    lesson_router,
    module_router,
    room_router,
    router as learning_router,
)
from app.domains.practice.router import router as practice_router
from app.domains.ctf.router import router as ctf_router
from app.domains.sandbox.router import router as sandbox_router
from app.domains.progress.router import router as progress_router


router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "nightbreach-backend",
    }


router.include_router(identity_router)
router.include_router(sandbox_router)
router.include_router(progress_router)
router.include_router(practice_router)
router.include_router(ctf_router)
router.include_router(learning_router)
router.include_router(module_router)
router.include_router(room_router)
router.include_router(lesson_router)
