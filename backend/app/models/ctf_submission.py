from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.ctf_attempt import CTFAttempt


class CTFSubmission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ctf_submissions"

    attempt_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "ctf_attempts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    submission_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    attempt: Mapped["CTFAttempt"] = relationship(
        "CTFAttempt",
        back_populates="submissions",
    )
