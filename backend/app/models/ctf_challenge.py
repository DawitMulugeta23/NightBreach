from __future__ import annotations

from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CTFChallengeMode(str, Enum):
    GUIDED = "guided"
    INDEPENDENT = "independent"


class CTFChallengeStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CTFChallengeType(str, Enum):
    FLAG = "flag"
    OUTPUT_EXTRACTION = "output_extraction"
    ANSWER = "answer"


class CTFChallengeGroup(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ctf_challenge_groups"

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    challenges: Mapped[list["CTFChallenge"]] = relationship(
        back_populates="group",
    )


class CTFChallenge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ctf_challenges"

    slug: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    scenario: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("ctf_challenge_groups.id"),
        nullable=False,
        index=True,
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    mode: Mapped[CTFChallengeMode] = mapped_column(
        SAEnum(
            CTFChallengeMode,
            name="ctf_challenge_mode",
            native_enum=False,
        ),
        nullable=False,
    )

    status: Mapped[CTFChallengeStatus] = mapped_column(
        SAEnum(
            CTFChallengeStatus,
            name="ctf_challenge_status",
            native_enum=False,
        ),
        nullable=False,
        default=CTFChallengeStatus.DRAFT,
        server_default=CTFChallengeStatus.DRAFT.value,
    )

    challenge_type: Mapped[CTFChallengeType] = mapped_column(
        SAEnum(
            CTFChallengeType,
            name="ctf_challenge_type",
            native_enum=False,
        ),
        nullable=False,
    )

    # This intentionally remains a bare UUID.
    # Sandbox owns the actual environment requirement.
    environment_requirement_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
        index=True,
    )

    # Server-side challenge configuration.
    #
    # This may contain validation data such as:
    # {
    #     "expected_flag": "...",
    #     "expected_answer": "...",
    #     "expected_output": "..."
    # }
    #
    # It must never be returned directly by learner-facing APIs.
    validation_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    group: Mapped[CTFChallengeGroup] = relationship(
        back_populates="challenges",
    )

    attempts: Mapped[list["CTFAttempt"]] = relationship(
        back_populates="challenge",
    )
