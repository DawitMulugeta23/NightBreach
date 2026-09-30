from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ProgressStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class LearnerLearningPathProgress(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "learner_learning_path_progress"

    learner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    learning_path_id: Mapped[UUID] = mapped_column(
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ProgressStatus] = mapped_column(
        SAEnum(
            ProgressStatus,
            name="progress_status",
            native_enum=False,
        ),
        nullable=False,
        default=ProgressStatus.NOT_STARTED,
        server_default=ProgressStatus.NOT_STARTED.value,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "learning_path_id",
            name="uq_learner_learning_path_progress",
        ),
    )


class LearnerModuleProgress(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "learner_module_progress"

    learner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    module_id: Mapped[UUID] = mapped_column(
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ProgressStatus] = mapped_column(
        SAEnum(
            ProgressStatus,
            name="progress_status",
            native_enum=False,
        ),
        nullable=False,
        default=ProgressStatus.NOT_STARTED,
        server_default=ProgressStatus.NOT_STARTED.value,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "module_id",
            name="uq_learner_module_progress",
        ),
    )


class LearnerRoomProgress(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "learner_room_progress"

    learner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ProgressStatus] = mapped_column(
        SAEnum(
            ProgressStatus,
            name="progress_status",
            native_enum=False,
        ),
        nullable=False,
        default=ProgressStatus.NOT_STARTED,
        server_default=ProgressStatus.NOT_STARTED.value,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "room_id",
            name="uq_learner_room_progress",
        ),
    )


class LearnerLessonProgress(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "learner_lesson_progress"

    learner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lesson_id: Mapped[UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ProgressStatus] = mapped_column(
        SAEnum(
            ProgressStatus,
            name="progress_status",
            native_enum=False,
        ),
        nullable=False,
        default=ProgressStatus.NOT_STARTED,
        server_default=ProgressStatus.NOT_STARTED.value,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "lesson_id",
            name="uq_learner_lesson_progress",
        ),
    )
