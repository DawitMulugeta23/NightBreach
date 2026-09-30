import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.user import User


TEST_USERNAMES = (
    "api_test_user",
    "duplicate_user",
    "login_test_user",
    "me_test_user",
)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
async def clean_test_users():
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(User).where(User.username.in_(TEST_USERNAMES))
        )
        await session.commit()

    yield

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(User).where(User.username.in_(TEST_USERNAMES))
        )
        await session.commit()


@pytest.mark.asyncio
async def test_register_returns_user(client, clean_test_users) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "api_test_user",
            "email": "api_test@example.com",
            "password": "strong-password-123",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["username"] == "api_test_user"
    assert body["email"] == "api_test@example.com"
    assert "id" in body
    assert "hashed_password" not in body


@pytest.mark.asyncio
async def test_register_duplicate_username_returns_conflict(
    client,
    clean_test_users,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_user",
            "email": "duplicate1@example.com",
            "password": "strong-password-123",
        },
    )

    assert response.status_code == 201

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_user",
            "email": "duplicate2@example.com",
            "password": "strong-password-123",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_login_returns_access_token(
    client,
    clean_test_users,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_test_user",
            "email": "login_test@example.com",
            "password": "strong-password-123",
        },
    )

    assert response.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "login_test_user",
            "password": "strong-password-123",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


@pytest.mark.asyncio
async def test_invalid_credentials_returns_401(
    client,
    clean_test_users,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "does_not_exist",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


@pytest.mark.asyncio
async def test_me_requires_authentication(
    client,
    clean_test_users,
) -> None:
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


@pytest.mark.asyncio
async def test_me_returns_authenticated_user(
    client,
    clean_test_users,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "me_test_user",
            "email": "me_test@example.com",
            "password": "strong-password-123",
        },
    )

    assert response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "me_test_user",
            "password": "strong-password-123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["username"] == "me_test_user"
    assert body["email"] == "me_test@example.com"
    assert "hashed_password" not in body
