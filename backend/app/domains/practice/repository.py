from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.practice import Practice, PracticeStatus
from app.models.practice_activity import PracticeActivity
from app.models.practice_attempt import PracticeAttempt


class PracticeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_published_activity(
        self,
        activity_id: UUID,
    ) -> PracticeActivity | None:
        result = await self.session.execute(
            select(PracticeActivity)
            .join(PracticeActivity.practice)
            .where(
                PracticeActivity.id == activity_id,
                Practice.status == PracticeStatus.PUBLISHED,
            )
        )
        return result.scalar_one_or_none()

    async def get_attempt(
        self,
        attempt_id: UUID,
        learner_id: UUID,
    ) -> PracticeAttempt | None:
        result = await self.session.execute(
            select(PracticeAttempt)
            .where(
                PracticeAttempt.id == attempt_id,
                PracticeAttempt.learner_id == learner_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_next_attempt_number(
        self,
        activity_id: UUID,
        learner_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(func.max(PracticeAttempt.attempt_no)).where(
                PracticeAttempt.practice_activity_id == activity_id,
                PracticeAttempt.learner_id == learner_id,
            )
        )

        current_max = result.scalar_one()
        return (current_max or 0) + 1

    async def create_attempt(
        self,
        attempt: PracticeAttempt,
    ) -> PracticeAttempt:
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def list_attempts(
        self,
        activity_id: UUID,
        learner_id: UUID,
    ) -> list[PracticeAttempt]:
        result = await self.session.execute(
            select(PracticeAttempt)
            .where(
                PracticeAttempt.practice_activity_id == activity_id,
                PracticeAttempt.learner_id == learner_id,
            )
            .order_by(PracticeAttempt.attempt_no)
        )

        return list(result.scalars().all())
