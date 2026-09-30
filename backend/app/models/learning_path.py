from enum import Enum

from sqlalchemy import CheckConstraint, Enum as SAEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class LearningPathStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class LearningPath(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "learning_paths"

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[LearningPathStatus] = mapped_column(
        SAEnum(
            LearningPathStatus,
            name="learning_path_status",
        ),
        nullable=False,
        default=LearningPathStatus.DRAFT,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "position >= 0",
            name="ck_learning_paths_position_nonnegative",
        ),
    )

    modules = relationship(
        "Module",
        back_populates="learning_path",
        cascade="all, delete-orphan",
        order_by="Module.position",
    )
