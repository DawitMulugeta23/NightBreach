from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ctf_attempt import CTFAttempt


class CTFAttemptRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        attempt_id: UUID,
    ) -> CTFAttempt | None:
        result = await self.session.execute(
            select(CTFAttempt).where(
                CTFAttempt.id == attempt_id
            )
        )

        return result.scalar_one_or_none()

    async def get_for_learner(
        self,
        attempt_id: UUID,
        learner_id: UUID,
    ) -> CTFAttempt | None:
        result = await self.session.execute(
            select(CTFAttempt).where(
                CTFAttempt.id == attempt_id,
                CTFAttempt.learner_id == learner_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_next_attempt_number(
        self,
        learner_id: UUID,
        challenge_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(
                func.coalesce(
                    func.max(
                        CTFAttempt.attempt_number
                    ),
                    0,
                )
            ).where(
                CTFAttempt.learner_id == learner_id,
                CTFAttempt.challenge_id == challenge_id,
            )
        )

        current = result.scalar_one()

        return int(current) + 1

    async def create(
        self,
        attempt: CTFAttempt,
    ) -> CTFAttempt:
        self.session.add(attempt)

        await self.session.flush()
        await self.session.refresh(attempt)

        return attempt

    async def save(
        self,
        attempt: CTFAttempt,
    ) -> CTFAttempt:
        self.session.add(attempt)

        await self.session.flush()
        await self.session.refresh(attempt)

        return attempt
