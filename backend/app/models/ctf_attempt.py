from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.ctf_challenge import CTFChallenge
    from app.models.ctf_submission import CTFSubmission
    from app.models.user import User


class CTFAttemptStatus(str, Enum):
    CREATED = "created"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EVALUATING = "evaluating"
    PASSED = "passed"
    FAILED = "failed"
    ENVIRONMENT_FAILED = "environment_failed"


class CTFAttempt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ctf_attempts"

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "challenge_id",
            "attempt_number",
            name="uq_ctf_attempt_learner_challenge_number",
        ),
    )

    learner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    challenge_id: Mapped[UUID] = mapped_column(
        ForeignKey("ctf_challenges.id"),
        nullable=False,
        index=True,
    )

    environment_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
        index=True,
    )

    session_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[CTFAttemptStatus] = mapped_column(
        SAEnum(
            CTFAttemptStatus,
            name="ctf_attempt_status",
            native_enum=False,
        ),
        nullable=False,
        default=CTFAttemptStatus.CREATED,
        server_default="created",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    learner: Mapped["User"] = relationship(
        "User",
        lazy="raise",
    )

    challenge: Mapped["CTFChallenge"] = relationship(
        "CTFChallenge",
        lazy="raise",
    )

    submissions: Mapped[list["CTFSubmission"]] = relationship(
        "CTFSubmission",
        back_populates="attempt",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="CTFSubmission.submitted_at",
    )
