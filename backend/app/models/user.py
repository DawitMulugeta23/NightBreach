from enum import Enum

from sqlalchemy import Boolean, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ProgressionMode(str, Enum):
    STRICT = "strict"
    FREE = "free"


class User(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    progression_mode: Mapped[ProgressionMode] = mapped_column(
        SAEnum(
            ProgressionMode,
            name="progression_mode",
            native_enum=False,
        ),
        nullable=False,
        default=ProgressionMode.STRICT,
        server_default=ProgressionMode.STRICT.value,
    )

    onboarding_quiz_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
