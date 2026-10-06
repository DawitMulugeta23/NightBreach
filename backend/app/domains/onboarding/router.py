from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User

from .schemas import (
    LearnerProfileResponse,
    OnboardingAnswerRequest,
    OnboardingAnswerResponse,
    OnboardingStartResponse,
)
from .service import OnboardingService

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


def _question_payload(question, service, answers) -> OnboardingStartResponse:
    return OnboardingStartResponse(
        question_id=question.id,
        dimension=question.dimension,
        prompt=question.prompt,
        options=[{"id": o.id, "label": o.label} for o in question.options],
        progress=service.progress(answers),
    )


@router.post("/start", response_model=OnboardingStartResponse)
async def start(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> OnboardingStartResponse:
    service = OnboardingService(session)
    await service.get_or_create(user.id)

    answers: dict[str, str] = {}
    question = service.current_question(answers)
    if question is None:
        raise RuntimeError("Onboarding tree is empty.")
    return _question_payload(question, service, answers)


@router.post("/answer", response_model=OnboardingAnswerResponse)
async def answer(
    payload: OnboardingAnswerRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> OnboardingAnswerResponse:
    service = OnboardingService(session)

    answers: dict[str, str] = dict(payload.answer_sheet or {})
    answers[payload.question_id] = ",".join(payload.option_ids)

    next_question, _summary = await service.answer(
        learner_id=user.id, answers=answers
    )

    if next_question is not None:
        return OnboardingAnswerResponse(
            completed=False,
            next=_question_payload(next_question, service, answers),
        )

    profile = await service.get_or_create(user.id)
    return OnboardingAnswerResponse(
        completed=True,
        profile=LearnerProfileResponse(
            learner_id=profile.learner_id,
            goals=profile.goals or [],
            technical_background=profile.technical_background,
            computer_knowledge=profile.computer_knowledge or "NONE",
            networking_knowledge=profile.networking_knowledge or "NONE",
            linux_cli_knowledge=profile.linux_cli_knowledge or "NONE",
            web_security_knowledge=profile.web_security_knowledge or "NONE",
            practical_security_experience=profile.practical_security_experience or "NONE",
            tool_experience=profile.tool_experience or {},
            knowledge_gaps=profile.knowledge_gaps or [],
            recommended_learning_paths=profile.recommended_learning_paths or [],
            recommended_practice=profile.recommended_practice or [],
            challenge_recommendation=profile.challenge_recommendation or "HIGH_GUIDANCE",
            personalized_advice=profile.personalized_advice or "",
            completed_at=profile.completed_at,
        ),
    )


@router.get("/profile", response_model=LearnerProfileResponse | None)
async def get_profile(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    service = OnboardingService(session)
    profile = await service.get_or_create(user.id)
    if profile.completed_at is None:
        return None
    return LearnerProfileResponse(
        learner_id=profile.learner_id,
        goals=profile.goals or [],
        technical_background=profile.technical_background,
        computer_knowledge=profile.computer_knowledge or "NONE",
        networking_knowledge=profile.networking_knowledge or "NONE",
        linux_cli_knowledge=profile.linux_cli_knowledge or "NONE",
        web_security_knowledge=profile.web_security_knowledge or "NONE",
        practical_security_experience=profile.practical_security_experience or "NONE",
        tool_experience=profile.tool_experience or {},
        knowledge_gaps=profile.knowledge_gaps or [],
        recommended_learning_paths=profile.recommended_learning_paths or [],
        recommended_practice=profile.recommended_practice or [],
        challenge_recommendation=profile.challenge_recommendation or "HIGH_GUIDANCE",
        personalized_advice=profile.personalized_advice or "",
        completed_at=profile.completed_at,
    )