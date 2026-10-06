from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OnboardingStartResponse(BaseModel):
    question_id: str
    dimension: str
    prompt: str
    options: list[dict]
    progress: dict  # {"answered": n, "total": m}


class OnboardingAnswerRequest(BaseModel):
    question_id: str
    option_ids: list[str] = Field(min_length=1)


class OnboardingAnswerResponse(BaseModel):
    completed: bool
    next: OnboardingStartResponse | None = None
    profile: "LearnerProfileResponse | None" = None


class LearnerProfileResponse(BaseModel):
    learner_id: UUID
    goals: list[str]
    technical_background: str | None
    computer_knowledge: str
    networking_knowledge: str
    linux_cli_knowledge: str
    web_security_knowledge: str
    practical_security_experience: str
    tool_experience: dict
    knowledge_gaps: list[str]
    recommended_learning_paths: list[str]
    recommended_practice: list[str]
    challenge_recommendation: str
    personalized_advice: str
    completed_at: datetime | None


OnboardingAnswerResponse.model_rebuild()