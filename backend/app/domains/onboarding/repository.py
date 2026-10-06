from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import LearnerProfile


class LearnerProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_learner(self, learner_id: UUID) -> LearnerProfile | None:
        result = await self._session.execute(
            select(LearnerProfile).where(LearnerProfile.learner_id == learner_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, profile: LearnerProfile) -> LearnerProfile:
        self._session.add(profile)
        await self._session.flush()
        return profile