import re
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import ProgressionMode, User

from .repository import UserRepository


USERNAME_PATTERN = re.compile(r"^[a-z0-9_]{3,20}$")


class IdentityError(Exception):
    """Base exception for Identity-domain errors."""


class UsernameAlreadyExistsError(IdentityError):
    pass


class EmailAlreadyExistsError(IdentityError):
    pass


class InvalidCredentialsError(IdentityError):
    pass


class InvalidUsernameError(IdentityError):
    pass


class IdentityService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRepository(session)
        self.session = session

    async def register(
        self,
        *,
        username: str,
        email: str,
        password: str,
    ) -> User:
        if not USERNAME_PATTERN.fullmatch(username):
            raise InvalidUsernameError(
                "Username must contain only lowercase letters, numbers, "
                "and underscores, and must be 3-20 characters long."
            )

        if await self.repository.get_by_username(username):
            raise UsernameAlreadyExistsError(
                "Username is already registered."
            )

        if await self.repository.get_by_email(email):
            raise EmailAlreadyExistsError(
                "Email is already registered."
            )

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            progression_mode=ProgressionMode.STRICT,
            onboarding_quiz_completed=False,
        )

        try:
            return await self.repository.create(user)
        except IntegrityError:
            await self.session.rollback()

            if await self.repository.get_by_username(username):
                raise UsernameAlreadyExistsError(
                    "Username is already registered."
                )

            if await self.repository.get_by_email(email):
                raise EmailAlreadyExistsError(
                    "Email is already registered."
                )

            raise

    async def authenticate(
        self,
        *,
        username: str,
        password: str,
    ) -> User:
        user = await self.repository.get_by_username(username)

        if user is None or not verify_password(
            password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError("Invalid username or password.")

        return user

    def create_token(self, user: User) -> str:
        return create_access_token(str(user.id))

    async def get_user(self, user_id: UUID) -> User | None:
        return await self.repository.get_by_id(user_id)
