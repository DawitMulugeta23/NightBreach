from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class LessonStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class LessonAccessOverride(str, Enum):
    FREE = "FREE"
    PRO = "PRO"


class LessonCompletionRule(str, Enum):
    REQUIRED_PRACTICE = "REQUIRED_PRACTICE"


class Lesson(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lessons"

    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[LessonStatus] = mapped_column(
        SAEnum(LessonStatus, name="lesson_status"),
        nullable=False,
        default=LessonStatus.DRAFT,
    )

    access_override: Mapped[Optional[LessonAccessOverride]] = mapped_column(
        SAEnum(LessonAccessOverride, name="lesson_access_override"),
        nullable=True,
    )

    completion_rule: Mapped[LessonCompletionRule] = mapped_column(
        SAEnum(LessonCompletionRule, name="lesson_completion_rule"),
        nullable=False,
        default=LessonCompletionRule.REQUIRED_PRACTICE,
    )

    environment_requirement_id: Mapped[Optional[UUID]] = mapped_column(
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("room_id", "slug", name="uq_lessons_room_slug"),
        UniqueConstraint("room_id", "position", name="uq_lessons_room_position"),
        CheckConstraint("position >= 0", name="ck_lessons_position_nonnegative"),
    )

    room = relationship(
        "Room",
        back_populates="lessons",
    )

    content_blocks = relationship(
        "LessonContentBlock",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="LessonContentBlock.position",
    )

    lesson_practices = relationship(
        "LessonPractice",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="LessonPractice.position",
    )
