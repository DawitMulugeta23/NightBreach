from uuid import uuid4

import pytest

from app.core.dependencies import get_current_user
from app.core.errors import AuthenticationError
from app.core.security import create_access_token
from app.models.user import User


class FakeCredentials:
    def __init__(
        self,
        credentials: str,
        scheme: str = "Bearer",
    ) -> None:
        self.credentials = credentials
        self.scheme = scheme


class FakeRepository:
    def __init__(self, user: User | None) -> None:
        self.user = user

    async def get_by_id(self, user_id):
        return self.user


@pytest.mark.asyncio
async def test_missing_credentials_rejected() -> None:
    with pytest.raises(AuthenticationError):
        await get_current_user(
            credentials=None,
            session=None,
        )


@pytest.mark.asyncio
async def test_invalid_token_rejected() -> None:
    credentials = FakeCredentials("not-a-valid-token")

    with pytest.raises(AuthenticationError):
        await get_current_user(
            credentials=credentials,
            session=None,
        )


@pytest.mark.asyncio
async def test_valid_token_with_missing_user_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = uuid4()
    token = create_access_token(str(user_id))

    credentials = FakeCredentials(token)

    class FakeRepositoryInstance:
        async def get_by_id(self, requested_user_id):
            assert requested_user_id == user_id
            return None

    monkeypatch.setattr(
        "app.core.dependencies.UserRepository",
        lambda session: FakeRepositoryInstance(),
    )

    with pytest.raises(AuthenticationError):
        await get_current_user(
            credentials=credentials,
            session=None,
        )


@pytest.mark.asyncio
async def test_valid_token_returns_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = uuid4()

    user = User(
        id=user_id,
        username="test_user",
        email="test@example.com",
        hashed_password="unused",
    )

    token = create_access_token(str(user_id))
    credentials = FakeCredentials(token)

    class FakeRepositoryInstance:
        async def get_by_id(self, requested_user_id):
            assert requested_user_id == user_id
            return user

    monkeypatch.setattr(
        "app.core.dependencies.UserRepository",
        lambda session: FakeRepositoryInstance(),
    )

    result = await get_current_user(
        credentials=credentials,
        session=None,
    )

    assert result is user
    assert result.id == user_id
    assert result.username == "test_user"


def test_access_token_contains_user_subject() -> None:
    user_id = uuid4()

    token = create_access_token(str(user_id))

    from app.core.security import decode_access_token

    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
