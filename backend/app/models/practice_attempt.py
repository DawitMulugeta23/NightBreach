from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PracticeAttempt(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "practice_attempts"

    practice_activity_id: Mapped[UUID] = mapped_column(
        ForeignKey("practice_activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    learner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ctf_attempt_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("ctf_attempts.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )

    attempt_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    submission_ref: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    result: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "practice_activity_id",
            "learner_id",
            "attempt_no",
            name="uq_practice_attempts_activity_learner_attempt",
        ),
        CheckConstraint(
            "attempt_no > 0",
            name="ck_practice_attempts_attempt_no_positive",
        ),
    )

    practice_activity = relationship(
        "PracticeActivity",
    )

    learner = relationship(
        "User",
    )

    ctf_attempt = relationship(
        "CTFAttempt",
    )
