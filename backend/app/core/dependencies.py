from __future__ import annotations

from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AuthenticationError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.domains.identity.repository import UserRepository
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError()

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")

        if not isinstance(subject, str):
            raise AuthenticationError()

        user_id = UUID(subject)

    except AuthenticationError:
        raise
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        raise AuthenticationError()

    user = await UserRepository(session).get_by_id(user_id)

    if user is None:
        raise AuthenticationError()

    return user
