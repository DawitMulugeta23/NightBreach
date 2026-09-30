from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domains.practice.public_config import build_public_configuration
from app.models.lesson import LessonAccessOverride, LessonCompletionRule
from app.models.lesson_content_block import LessonContentBlockType
from app.models.practice import PracticeActivityMode, PracticeStatus
from app.models.practice_activity import (
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.room import RoomAccessLevel


class LearningPathSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    description: str
    position: int


class LearningPathDetail(LearningPathSummary):
    modules: list["ModuleSummary"]


class ModuleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    learning_path_id: UUID
    slug: str
    title: str
    description: str
    position: int


class ModuleDetail(ModuleSummary):
    rooms: list["RoomSummary"]


class RoomSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    module_id: UUID
    slug: str
    title: str
    description: str
    position: int
    access_level: RoomAccessLevel


class RoomDetail(RoomSummary):
    lessons: list["LessonSummary"]


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    room_id: UUID
    slug: str
    title: str
    description: str
    position: int
    access_override: LessonAccessOverride | None
    completion_rule: LessonCompletionRule


class ContentBlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    position: int
    block_type: LessonContentBlockType
    content: dict[str, Any]


class PracticeActivityResponse(BaseModel):
    id: UUID
    practice_id: UUID
    position: int
    activity_type: PracticeActivityType
    title: str
    instructions: str
    required: bool
    evaluation_type: PracticeEvaluationType
    configuration: dict[str, Any]
    guidance_policy: dict[str, Any]

    @classmethod
    def from_activity(cls, activity) -> "PracticeActivityResponse":
        return cls(
            id=activity.id,
            practice_id=activity.practice_id,
            position=activity.position,
            activity_type=activity.activity_type,
            title=activity.title,
            instructions=activity.instructions,
            required=activity.required,
            evaluation_type=activity.evaluation_type,
            configuration=build_public_configuration(
                activity.configuration
            ),
            guidance_policy=activity.guidance_policy,
        )


class PracticeResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: PracticeStatus
    activity_mode: PracticeActivityMode
    activities: list[PracticeActivityResponse]

    @classmethod
    def from_practice(cls, practice) -> "PracticeResponse":
        return cls(
            id=practice.id,
            title=practice.title,
            description=practice.description,
            status=practice.status,
            activity_mode=practice.activity_mode,
            activities=[
                PracticeActivityResponse.from_activity(activity)
                for activity in practice.activities
            ],
        )


class LessonPracticeResponse(BaseModel):
    id: UUID
    lesson_id: UUID
    practice_id: UUID
    position: int
    required: bool
    practice: PracticeResponse

    @classmethod
    def from_lesson_practice(
        cls,
        lesson_practice,
    ) -> "LessonPracticeResponse":
        return cls(
            id=lesson_practice.id,
            lesson_id=lesson_practice.lesson_id,
            practice_id=lesson_practice.practice_id,
            position=lesson_practice.position,
            required=lesson_practice.required,
            practice=PracticeResponse.from_practice(
                lesson_practice.practice
            ),
        )


class LessonDetail(LessonSummary):
    content_blocks: list[ContentBlockResponse]
    lesson_practices: list[LessonPracticeResponse]

    @classmethod
    def from_lesson(cls, lesson) -> "LessonDetail":
        return cls(
            id=lesson.id,
            room_id=lesson.room_id,
            slug=lesson.slug,
            title=lesson.title,
            description=lesson.description,
            position=lesson.position,
            access_override=lesson.access_override,
            completion_rule=lesson.completion_rule,
            content_blocks=[
                ContentBlockResponse.model_validate(block)
                for block in lesson.content_blocks
            ],
            lesson_practices=[
                LessonPracticeResponse.from_lesson_practice(
                    lesson_practice
                )
                for lesson_practice in lesson.lesson_practices
                if lesson_practice.practice is not None
            ],
        )


LearningPathDetail.model_rebuild()
ModuleDetail.model_rebuild()
RoomDetail.model_rebuild()
LessonDetail.model_rebuild()
