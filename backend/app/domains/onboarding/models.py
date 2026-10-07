from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LearnerProfile(Base):
    """SRS 4.7 - the learner profile produced at the end of onboarding."""

    __tablename__ = "learner_profiles"

    # Named explicitly so the metadata matches the existing database exactly.
    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            name="learner_profiles_learner_id_key",
        ),
        Index(
            "ix_learner_profiles_learner_id",
            "learner_id",
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    # Capability dimensions (SRS 4.4). All enum-ish strings.
    goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    technical_background: Mapped[str | None] = mapped_column(String(32))
    computer_knowledge: Mapped[str | None] = mapped_column(String(16))
    networking_knowledge: Mapped[str | None] = mapped_column(String(16))
    linux_cli_knowledge: Mapped[str | None] = mapped_column(String(16))
    web_security_knowledge: Mapped[str | None] = mapped_column(String(16))
    practical_security_experience: Mapped[str | None] = mapped_column(String(32))
    tool_experience: Mapped[dict] = mapped_column(JSON, default=dict)

    # Recommendations produced from the profile.
    knowledge_gaps: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommended_learning_paths: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommended_practice: Mapped[list[str]] = mapped_column(JSON, default=list)
    challenge_recommendation: Mapped[str | None] = mapped_column(String(32))
    personalized_advice: Mapped[str | None] = mapped_column(String(2000))

    # Specialization lock (SRS 21.5/21.6).
    specialization_slug: Mapped[str | None] = mapped_column(String(64))
    specialization_locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    learner = relationship("User", backref="learner_profile", uselist=False)