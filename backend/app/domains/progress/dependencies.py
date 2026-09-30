from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User

from .service import ProgressService


def get_progress_service(
    session: AsyncSession = Depends(get_db_session),
) -> ProgressService:
    return ProgressService(session=session)


async def get_progress_learner(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
