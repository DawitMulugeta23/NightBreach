from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User

from .schemas import (
    CompletedModuleResponse,
    CompletedRoomResponse,
    CompletionStateResponse,
    LearningPathProgressResponse,
    LessonProgressResponse,
    ModuleProgressResponse,
    RoomProgressResponse,
)
from .service import ProgressService


router = APIRouter(prefix="/progress", tags=["progress"])


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonProgressResponse | None,
    status_code=status.HTTP_200_OK,
)
async def get_lesson_progress(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LessonProgressResponse | None:
    service = ProgressService(session=session)

    progress = await service.get_lesson_progress(
        learner_id=current_user.id,
        lesson_id=lesson_id,
    )

    if progress is None:
        return None

    return LessonProgressResponse.model_validate(progress)


@router.get(
    "/rooms/{room_id}",
    response_model=RoomProgressResponse | None,
    status_code=status.HTTP_200_OK,
)
async def get_room_progress(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RoomProgressResponse | None:
    service = ProgressService(session=session)

    progress = await service.get_room_progress(
        learner_id=current_user.id,
        room_id=room_id,
    )

    if progress is None:
        return None

    return RoomProgressResponse.model_validate(progress)


@router.get(
    "/modules/{module_id}",
    response_model=ModuleProgressResponse | None,
    status_code=status.HTTP_200_OK,
)
async def get_module_progress(
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ModuleProgressResponse | None:
    service = ProgressService(session=session)

    progress = await service.get_module_progress(
        learner_id=current_user.id,
        module_id=module_id,
    )

    if progress is None:
        return None

    return ModuleProgressResponse.model_validate(progress)


@router.get(
    "/learning-paths/{learning_path_id}",
    response_model=LearningPathProgressResponse | None,
    status_code=status.HTTP_200_OK,
)
async def get_learning_path_progress(
    learning_path_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LearningPathProgressResponse | None:
    service = ProgressService(session=session)

    progress = await service.get_learning_path_progress(
        learner_id=current_user.id,
        learning_path_id=learning_path_id,
    )

    if progress is None:
        return None

    return LearningPathProgressResponse.model_validate(progress)


@router.post(
    "/lessons/{lesson_id}/complete",
    response_model=LessonProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def record_lesson_completion(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LessonProgressResponse:
    service = ProgressService(session=session)

    progress = await service.record_lesson_completion(
        learner_id=current_user.id,
        lesson_id=lesson_id,
    )

    await session.commit()

    return LessonProgressResponse.model_validate(progress)


@router.post(
    "/rooms/{room_id}/complete",
    response_model=RoomProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def record_room_completion(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RoomProgressResponse:
    service = ProgressService(session=session)

    progress = await service.record_room_completion(
        learner_id=current_user.id,
        room_id=room_id,
    )

    await session.commit()

    return RoomProgressResponse.model_validate(progress)


@router.post(
    "/modules/{module_id}/complete",
    response_model=ModuleProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def record_module_completion(
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ModuleProgressResponse:
    service = ProgressService(session=session)

    progress = await service.record_module_completion(
        learner_id=current_user.id,
        module_id=module_id,
    )

    await session.commit()

    return ModuleProgressResponse.model_validate(progress)


@router.post(
    "/learning-paths/{learning_path_id}/complete",
    response_model=LearningPathProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def record_learning_path_completion(
    learning_path_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> LearningPathProgressResponse:
    service = ProgressService(session=session)

    progress = await service.record_learning_path_completion(
        learner_id=current_user.id,
        learning_path_id=learning_path_id,
    )

    await session.commit()

    return LearningPathProgressResponse.model_validate(progress)


@router.get(
    "/completed/rooms",
    response_model=list[CompletedRoomResponse],
    status_code=status.HTTP_200_OK,
)
async def list_completed_rooms(
    module_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[CompletedRoomResponse]:
    service = ProgressService(session=session)

    progress_records = await service.list_completed_rooms(
        learner_id=current_user.id,
        module_id=module_id,
    )

    return [
        CompletedRoomResponse.model_validate(progress)
        for progress in progress_records
    ]


@router.get(
    "/completed/modules",
    response_model=list[CompletedModuleResponse],
    status_code=status.HTTP_200_OK,
)
async def list_completed_modules(
    learning_path_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[CompletedModuleResponse]:
    service = ProgressService(session=session)

    progress_records = await service.list_completed_modules(
        learner_id=current_user.id,
        learning_path_id=learning_path_id,
    )

    return [
        CompletedModuleResponse.model_validate(progress)
        for progress in progress_records
    ]


@router.get(
    "/lessons/{lesson_id}/completion-state",
    response_model=CompletionStateResponse,
    status_code=status.HTTP_200_OK,
)
async def get_completion_state(
    lesson_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CompletionStateResponse:
    service = ProgressService(session=session)

    state = await service.get_completion_state(
        learner_id=current_user.id,
        lesson_id=lesson_id,
    )

    return CompletionStateResponse(**state)
