from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.progress import ProgressStatus


class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    learner_id: UUID
    status: ProgressStatus
    started_at: datetime | None
    completed_at: datetime | None
    last_activity_at: datetime


class LessonProgressResponse(ProgressResponse):
    lesson_id: UUID


class RoomProgressResponse(ProgressResponse):
    room_id: UUID


class ModuleProgressResponse(ProgressResponse):
    module_id: UUID


class LearningPathProgressResponse(ProgressResponse):
    learning_path_id: UUID


class CompletedRoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    learner_id: UUID
    room_id: UUID
    status: ProgressStatus
    completed_at: datetime | None
    last_activity_at: datetime


class CompletedModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    learner_id: UUID
    module_id: UUID
    status: ProgressStatus
    completed_at: datetime | None
    last_activity_at: datetime


class CompletionStateResponse(BaseModel):
    lesson_id: UUID
    room_id: UUID
    module_id: UUID
    learning_path_id: UUID

    lesson_status: ProgressStatus
    room_status: ProgressStatus
    module_status: ProgressStatus
    learning_path_status: ProgressStatus
