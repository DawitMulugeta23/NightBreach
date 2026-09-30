from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User

from .schemas import (
    PracticeAttemptResponse,
    StartAttemptRequest,
    StartAttemptResponse,
    SubmitActivityRequest,
    SubmitActivityResponse,
)
from .service import PracticeService


router = APIRouter(prefix="/practice", tags=["practice"])


@router.post(
    "/activities/{activity_id}/attempts",
    response_model=StartAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_attempt(
    activity_id: UUID,
    request: StartAttemptRequest | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> StartAttemptResponse:
    service = PracticeService(session=session)

    attempt = await service.start_attempt(
        activity_id=activity_id,
        learner_id=current_user.id,
        environment_id=request.environment_id if request else None,
        session_id=request.session_id if request else None,
    )

    await session.commit()

    return StartAttemptResponse.model_validate(attempt)


@router.get(
    "/attempts/{attempt_id}",
    response_model=PracticeAttemptResponse,
    status_code=status.HTTP_200_OK,
)
async def get_attempt(
    attempt_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> PracticeAttemptResponse:
    service = PracticeService(session=session)
    attempt = await service.get_attempt(
        attempt_id=attempt_id,
        learner_id=current_user.id,
    )
    return PracticeAttemptResponse.model_validate(attempt)


@router.get(
    "/activities/{activity_id}/attempts",
    response_model=list[PracticeAttemptResponse],
    status_code=status.HTTP_200_OK,
)
async def list_attempts(
    activity_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[PracticeAttemptResponse]:
    service = PracticeService(session=session)

    attempts = await service.list_attempts(
        activity_id=activity_id,
        learner_id=current_user.id,
    )

    return [
        PracticeAttemptResponse.model_validate(attempt)
        for attempt in attempts
    ]


@router.post(
    "/attempts/{attempt_id}/submit",
    response_model=SubmitActivityResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_attempt(
    attempt_id: UUID,
    request: SubmitActivityRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> SubmitActivityResponse:
    service = PracticeService(session=session)

    attempt = await service.submit_attempt(
        attempt_id=attempt_id,
        learner_id=current_user.id,
        submission=request.submission,
    )

    await session.commit()

    return SubmitActivityResponse.model_validate(attempt)
