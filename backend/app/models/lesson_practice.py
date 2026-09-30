from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class LessonPractice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lesson_practices"

    lesson_id: Mapped[UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    practice_id: Mapped[UUID] = mapped_column(
        ForeignKey("practices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "practice_id",
            name="uq_lesson_practices_lesson_practice",
        ),
        UniqueConstraint(
            "practice_id",
            name="uq_lesson_practices_practice",
        ),
        UniqueConstraint(
            "lesson_id",
            "position",
            name="uq_lesson_practices_lesson_position",
        ),
        CheckConstraint(
            "position >= 0",
            name="ck_lesson_practices_position_nonnegative",
        ),
    )

    lesson = relationship(
        "Lesson",
        back_populates="lesson_practices",
    )

    practice = relationship(
        "Practice",
        back_populates="lesson_practices",
    )
