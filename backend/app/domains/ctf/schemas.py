from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.ctf_challenge import (
    CTFChallengeMode,
    CTFChallengeStatus,
    CTFChallengeType,
)
from app.models.ctf_attempt import CTFAttemptStatus


class CTFChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    description: str
    objective: str
    scenario: str | None
    group_id: UUID
    difficulty: str
    mode: CTFChallengeMode
    status: CTFChallengeStatus
    challenge_type: CTFChallengeType
    environment_requirement_id: UUID | None

    # IMPORTANT:
    # validation_config is intentionally NOT exposed.
    # It may contain expected flags/answers.


class CTFChallengeListResponse(BaseModel):
    items: list[CTFChallengeResponse]


class CTFStartAttemptRequest(BaseModel):
    environment_id: UUID | None = None
    session_id: str | None = Field(
        default=None,
        max_length=255,
    )


class CTFAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    learner_id: UUID
    challenge_id: UUID
    environment_id: UUID | None
    session_id: str | None
    attempt_number: int
    status: CTFAttemptStatus
    started_at: object | None
    completed_at: object | None


class CTFAttemptListResponse(BaseModel):
    items: list[CTFAttemptResponse]


class CTFSubmitRequest(BaseModel):
    submission_value: str = Field(
        min_length=1,
        max_length=10_000,
    )


class CTFSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    attempt_id: UUID
    submission_value: str
    submitted_at: object
    result: str


class CTFSubmissionListResponse(BaseModel):
    items: list[CTFSubmissionResponse]


class CTFSubmitResponse(BaseModel):
    attempt: CTFAttemptResponse
    submission: CTFSubmissionResponse
