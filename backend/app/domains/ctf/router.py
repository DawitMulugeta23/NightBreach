from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.errors import NotFoundError
from app.db.session import get_db_session
from app.domains.ctf.evaluator import CTFEvaluationConfigurationError
from app.domains.ctf.repository import CTFRepository
from app.domains.ctf.schemas import (
    CTFAttemptListResponse,
    CTFAttemptResponse,
    CTFChallengeListResponse,
    CTFChallengeResponse,
    CTFStartAttemptRequest,
    CTFSubmissionListResponse,
    CTFSubmissionResponse,
    CTFSubmitRequest,
    CTFSubmitResponse,
)
from app.domains.ctf.service import (
    CTFAttemptNotActiveError,
    CTFService,
)
from app.domains.ctf.state_machine import InvalidCTFAttemptTransition
from app.models.user import User


router = APIRouter(
    prefix="/ctf",
    tags=["ctf"],
)


def get_ctf_service(
    session: AsyncSession,
) -> CTFService:
    return CTFService(
        repository=CTFRepository(session),
    )


@router.get(
    "/challenges",
    response_model=CTFChallengeListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_challenges(
    group_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFChallengeListResponse:
    service = get_ctf_service(session)

    challenges = await service.list_challenges(
        group_id=group_id,
    )

    return CTFChallengeListResponse(
        items=[
            CTFChallengeResponse.model_validate(challenge)
            for challenge in challenges
        ]
    )


@router.get(
    "/challenges/slug/{slug}",
    response_model=CTFChallengeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_challenge_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFChallengeResponse:
    service = get_ctf_service(session)

    try:
        challenge = await service.get_challenge_by_slug(
            slug=slug,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CTFChallengeResponse.model_validate(
        challenge,
    )


@router.get(
    "/challenges/{challenge_id}",
    response_model=CTFChallengeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_challenge(
    challenge_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFChallengeResponse:
    service = get_ctf_service(session)

    try:
        challenge = await service.get_challenge(
            challenge_id=challenge_id,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CTFChallengeResponse.model_validate(
        challenge,
    )


@router.post(
    "/challenges/{challenge_id}/attempts",
    response_model=CTFAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_attempt(
    challenge_id: UUID,
    request: CTFStartAttemptRequest | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFAttemptResponse:
    service = get_ctf_service(session)

    try:
        attempt = await service.start_attempt(
            learner_id=current_user.id,
            challenge_id=challenge_id,
            environment_id=(
                request.environment_id
                if request
                else None
            ),
            session_id=(
                request.session_id
                if request
                else None
            ),
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    await session.commit()

    return CTFAttemptResponse.model_validate(
        attempt,
    )


@router.post(
    "/attempts/{attempt_id}/start",
    response_model=CTFAttemptResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_in_progress(
    attempt_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFAttemptResponse:
    service = get_ctf_service(session)

    try:
        attempt = await service.mark_in_progress(
            attempt_id=attempt_id,
            learner_id=current_user.id,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidCTFAttemptTransition as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CTF attempt cannot be started from its current state.",
        ) from exc

    await session.commit()

    return CTFAttemptResponse.model_validate(
        attempt,
    )


@router.get(
    "/attempts/{attempt_id}",
    response_model=CTFAttemptResponse,
    status_code=status.HTTP_200_OK,
)
async def get_attempt(
    attempt_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFAttemptResponse:
    service = get_ctf_service(session)

    try:
        attempt = await service.get_attempt(
            learner_id=current_user.id,
            attempt_id=attempt_id,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CTFAttemptResponse.model_validate(
        attempt,
    )


@router.get(
    "/challenges/{challenge_id}/attempts",
    response_model=CTFAttemptListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_attempts(
    challenge_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFAttemptListResponse:
    service = get_ctf_service(session)

    attempts = await service.list_attempts(
        learner_id=current_user.id,
        challenge_id=challenge_id,
    )

    return CTFAttemptListResponse(
        items=[
            CTFAttemptResponse.model_validate(attempt)
            for attempt in attempts
        ]
    )


@router.post(
    "/attempts/{attempt_id}/submit",
    response_model=CTFSubmitResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_attempt(
    attempt_id: UUID,
    request: CTFSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFSubmitResponse:
    service = get_ctf_service(session)

    try:
        attempt, submission = await service.submit(
            attempt_id=attempt_id,
            learner_id=current_user.id,
            submission_value=request.submission_value,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CTFAttemptNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except CTFEvaluationConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CTF evaluation is temporarily unavailable.",
        ) from exc

    await session.commit()

    return CTFSubmitResponse(
        attempt=CTFAttemptResponse.model_validate(
            attempt,
        ),
        submission=CTFSubmissionResponse.model_validate(
            submission,
        ),
    )


@router.get(
    "/attempts/{attempt_id}/submissions",
    response_model=CTFSubmissionListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_submissions(
    attempt_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFSubmissionListResponse:
    service = get_ctf_service(session)

    try:
        submissions = await service.list_submissions(
            learner_id=current_user.id,
            attempt_id=attempt_id,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CTFSubmissionListResponse(
        items=[
            CTFSubmissionResponse.model_validate(
                submission,
            )
            for submission in submissions
        ]
    )


@router.post(
    "/attempts/{attempt_id}/environment-failed",
    response_model=CTFAttemptResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_environment_failed(
    attempt_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CTFAttemptResponse:
    service = get_ctf_service(session)

    try:
        attempt = await service.mark_environment_failed(
            attempt_id=attempt_id,
            learner_id=current_user.id,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidCTFAttemptTransition as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CTF environment cannot be failed from the current attempt state.",
        ) from exc

    await session.commit()

    return CTFAttemptResponse.model_validate(
        attempt,
    )
