from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PracticeActivityType(str, Enum):
    TEXT_QUESTION = "TEXT_QUESTION"
    PRACTICAL_TASK = "PRACTICAL_TASK"
    GUIDED_CTF = "GUIDED_CTF"


class PracticeEvaluationType(str, Enum):
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TEXT_EXACT = "TEXT_EXACT"
    TEXT_NORMALIZED = "TEXT_NORMALIZED"
    TEXT_CASE_INSENSITIVE = "TEXT_CASE_INSENSITIVE"
    COMMAND_RESULT = "COMMAND_RESULT"
    OUTPUT_EXTRACTION = "OUTPUT_EXTRACTION"
    FLAG_SUBMISSION = "FLAG_SUBMISSION"


class PracticeActivity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "practice_activities"

    practice_id: Mapped[UUID] = mapped_column(
        ForeignKey("practices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    activity_type: Mapped[PracticeActivityType] = mapped_column(
        SAEnum(
            PracticeActivityType,
            name="practice_activity_type",
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    instructions: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    evaluation_type: Mapped[PracticeEvaluationType] = mapped_column(
        SAEnum(
            PracticeEvaluationType,
            name="practice_evaluation_type",
        ),
        nullable=False,
    )

    environment_requirement_id: Mapped[Optional[UUID]] = mapped_column(
        nullable=True,
    )

    configuration: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    guidance_policy: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    __table_args__ = (
        # One activity can occupy only one position within a practice.
        # The authoritative source specifies UNIQUE(practice_id, position).
        UniqueConstraint(
            "practice_id",
            "position",
            name="uq_practice_activities_practice_position",
        ),
    )

    practice = relationship(
        "Practice",
        back_populates="activities",
    )
