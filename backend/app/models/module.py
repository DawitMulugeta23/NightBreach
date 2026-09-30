from enum import Enum
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ModuleStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class Module(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "modules"

    learning_path_id: Mapped[UUID] = mapped_column(
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[ModuleStatus] = mapped_column(
        SAEnum(
            ModuleStatus,
            name="module_status",
        ),
        nullable=False,
        default=ModuleStatus.DRAFT,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "learning_path_id",
            "slug",
            name="uq_modules_learning_path_slug",
        ),
        UniqueConstraint(
            "learning_path_id",
            "position",
            name="uq_modules_learning_path_position",
        ),
        CheckConstraint(
            "position >= 0",
            name="ck_modules_position_nonnegative",
        ),
    )

    learning_path = relationship(
        "LearningPath",
        back_populates="modules",
    )

    rooms = relationship(
        "Room",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="Room.position",
    )
