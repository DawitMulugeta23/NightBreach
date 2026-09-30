from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.errors import AuthenticationError, ConflictError, ValidationError
from app.db.session import get_db_session
from app.models.user import User

from .schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from .service import (
    EmailAlreadyExistsError,
    IdentityService,
    InvalidCredentialsError,
    InvalidUsernameError,
    UsernameAlreadyExistsError,
)


router = APIRouter(
    prefix="/auth",
    tags=["identity"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    service = IdentityService(session)

    try:
        user = await service.register(
            username=request.username,
            email=request.email,
            password=request.password,
        )
        await session.commit()
        return user

    except UsernameAlreadyExistsError as exc:
        await session.rollback()
        raise ConflictError(str(exc)) from exc

    except EmailAlreadyExistsError as exc:
        await session.rollback()
        raise ConflictError(str(exc)) from exc

    except InvalidUsernameError as exc:
        await session.rollback()
        raise ValidationError(str(exc)) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    service = IdentityService(session)

    try:
        user = await service.authenticate(
            username=request.username,
            password=request.password,
        )
    except InvalidCredentialsError as exc:
        raise AuthenticationError(str(exc)) from exc

    return TokenResponse(
        access_token=service.create_token(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
