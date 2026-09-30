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


class RoomStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class RoomAccessLevel(str, Enum):
    FREE = "FREE"
    PRO = "PRO"


class Room(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "rooms"

    module_id: Mapped[UUID] = mapped_column(
        ForeignKey("modules.id", ondelete="CASCADE"),
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

    status: Mapped[RoomStatus] = mapped_column(
        SAEnum(
            RoomStatus,
            name="room_status",
        ),
        nullable=False,
        default=RoomStatus.DRAFT,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    access_level: Mapped[RoomAccessLevel] = mapped_column(
        SAEnum(
            RoomAccessLevel,
            name="room_access_level",
        ),
        nullable=False,
        default=RoomAccessLevel.FREE,
    )

    __table_args__ = (
        UniqueConstraint(
            "module_id",
            "slug",
            name="uq_rooms_module_slug",
        ),
        UniqueConstraint(
            "module_id",
            "position",
            name="uq_rooms_module_position",
        ),
        CheckConstraint(
            "position >= 0",
            name="ck_rooms_position_nonnegative",
        ),
    )

    module = relationship(
        "Module",
        back_populates="rooms",
    )

    lessons = relationship(
        "Lesson",
        back_populates="room",
        cascade="all, delete-orphan",
        order_by="Lesson.position",
    )
