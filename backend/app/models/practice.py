from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PracticeStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class PracticeActivityMode(str, Enum):
    TEXT = "TEXT"
    PRACTICAL = "PRACTICAL"
    GUIDED_CTF = "GUIDED_CTF"


class Practice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "practices"

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[PracticeStatus] = mapped_column(
        SAEnum(
            PracticeStatus,
            name="practice_status",
        ),
        nullable=False,
        default=PracticeStatus.DRAFT,
    )

    activity_mode: Mapped[PracticeActivityMode] = mapped_column(
        SAEnum(
            PracticeActivityMode,
            name="practice_activity_mode",
        ),
        nullable=False,
        default=PracticeActivityMode.TEXT,
    )

    environment_requirement_id: Mapped[Optional[UUID]] = mapped_column(
        nullable=True,
    )

    activities = relationship(
        "PracticeActivity",
        back_populates="practice",
        cascade="all, delete-orphan",
        order_by="PracticeActivity.position",
    )

    lesson_practices = relationship(
        "LessonPractice",
        back_populates="practice",
        cascade="all, delete-orphan",
    )
