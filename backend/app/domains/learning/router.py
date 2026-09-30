from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.errors import NotFoundError
from app.db.session import get_db_session
from app.models.user import User

from .schemas import (
    LearningPathDetail,
    LearningPathSummary,
    LessonDetail,
    ModuleDetail,
    RoomDetail,
)
from .service import LearningService


router = APIRouter(
    prefix="/learning-paths",
    tags=["learning"],
)


@router.get(
    "",
    response_model=list[LearningPathSummary],
)
async def list_learning_paths(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[LearningPathSummary]:
    service = LearningService(session)

    paths = await service.list_learning_paths()

    return [
        LearningPathSummary.model_validate(path)
        for path in paths
    ]


@router.get(
    "/{learning_path_id}",
    response_model=LearningPathDetail,
)
async def get_learning_path(
    learning_path_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LearningPathDetail:
    service = LearningService(session)

    learning_path = await service.get_learning_path(learning_path_id)

    if learning_path is None:
        raise NotFoundError("Learning path not found.")

    return LearningPathDetail.model_validate(learning_path)


module_router = APIRouter(
    prefix="/modules",
    tags=["learning"],
)


@module_router.get(
    "/{module_id}",
    response_model=ModuleDetail,
)
async def get_module(
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ModuleDetail:
    service = LearningService(session)

    module = await service.get_module(module_id)

    if module is None:
        raise NotFoundError("Module not found.")

    return ModuleDetail.model_validate(module)


room_router = APIRouter(
    prefix="/rooms",
    tags=["learning"],
)


@room_router.get(
    "/{room_id}",
    response_model=RoomDetail,
)
async def get_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RoomDetail:
    service = LearningService(session)

    room = await service.get_room(room_id)

    if room is None:
        raise NotFoundError("Room not found.")

    return RoomDetail.model_validate(room)


lesson_router = APIRouter(
    prefix="/lessons",
    tags=["learning"],
)


@lesson_router.get(
    "/{lesson_id}",
    response_model=LessonDetail,
)
async def get_lesson(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LessonDetail:
    service = LearningService(session)

    lesson = await service.get_lesson(lesson_id)

    if lesson is None:
        raise NotFoundError("Lesson not found.")

    return LessonDetail.from_lesson(lesson)
