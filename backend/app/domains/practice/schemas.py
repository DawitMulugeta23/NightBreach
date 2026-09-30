from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domains.practice.public_config import build_public_configuration
from app.models.practice import PracticeActivityMode
from app.models.practice_activity import (
    PracticeActivityType,
    PracticeEvaluationType,
)


class StartAttemptRequest(BaseModel):
    environment_id: UUID | None = None
    session_id: str | None = Field(default=None, max_length=255)


class StartAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practice_activity_id: UUID
    attempt_no: int
    ctf_attempt_id: UUID | None
    started_at: datetime


class SubmitActivityRequest(BaseModel):
    submission: str = Field(min_length=1)


class SubmitActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practice_activity_id: UUID
    attempt_no: int
    ctf_attempt_id: UUID | None
    result: str
    score: Decimal | None
    submitted_at: datetime


class PracticeActivityDetail(BaseModel):
    id: UUID
    practice_id: UUID
    position: int
    activity_type: PracticeActivityType
    title: str
    instructions: str
    required: bool
    evaluation_type: PracticeEvaluationType
    environment_requirement_id: UUID | None
    configuration: dict
    guidance_policy: dict

    @classmethod
    def from_activity(cls, activity) -> "PracticeActivityDetail":
        return cls(
            id=activity.id,
            practice_id=activity.practice_id,
            position=activity.position,
            activity_type=activity.activity_type,
            title=activity.title,
            instructions=activity.instructions,
            required=activity.required,
            evaluation_type=activity.evaluation_type,
            environment_requirement_id=activity.environment_requirement_id,
            configuration=build_public_configuration(
                activity.configuration
            ),
            guidance_policy=activity.guidance_policy,
        )


class PracticeActivityListResponse(BaseModel):
    practice_id: UUID
    activity_mode: PracticeActivityMode
    activities: list[PracticeActivityDetail]


class PracticeAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    practice_activity_id: UUID
    attempt_no: int
    ctf_attempt_id: UUID | None
    submission_ref: str | None
    result: str | None
    score: Decimal | None
    started_at: datetime
    submitted_at: datetime | None
