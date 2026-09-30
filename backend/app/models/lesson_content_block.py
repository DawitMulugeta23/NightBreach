from enum import Enum
from uuid import UUID

from sqlalchemy import (
    Enum as SAEnum,
    ForeignKey,
    Integer,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class LessonContentBlockType(str, Enum):
    TEXT = "TEXT"
    HEADING = "HEADING"
    CODE = "CODE"
    IMAGE = "IMAGE"
    CALLOUT = "CALLOUT"
    LIST = "LIST"
    TABLE = "TABLE"
    TERMINAL_OUTPUT = "TERMINAL_OUTPUT"


class LessonContentBlock(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lesson_content_blocks"

    lesson_id: Mapped[UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    block_type: Mapped[LessonContentBlockType] = mapped_column(
        SAEnum(
            LessonContentBlockType,
            name="lesson_content_block_type",
        ),
        nullable=False,
    )

    content: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "position",
            name="uq_lesson_content_blocks_lesson_position",
        ),
    )

    lesson = relationship(
        "Lesson",
        back_populates="content_blocks",
    )
