from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ctf_attempt import CTFAttempt
from app.models.ctf_challenge import (
    CTFChallenge,
    CTFChallengeGroup,
    CTFChallengeStatus,
)
from app.models.ctf_submission import CTFSubmission


class CTFRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_published_challenge(
        self,
        challenge_id: UUID,
    ) -> CTFChallenge | None:
        result = await self.session.execute(
            select(CTFChallenge)
            .where(
                CTFChallenge.id == challenge_id,
                CTFChallenge.status == CTFChallengeStatus.PUBLISHED,
            )
        )
        return result.scalar_one_or_none()

    async def get_published_challenge_by_slug(
        self,
        slug: str,
    ) -> CTFChallenge | None:
        result = await self.session.execute(
            select(CTFChallenge)
            .where(
                CTFChallenge.slug == slug,
                CTFChallenge.status == CTFChallengeStatus.PUBLISHED,
            )
        )
        return result.scalar_one_or_none()

    async def list_published_challenges(
        self,
        *,
        group_id: UUID | None = None,
    ) -> list[CTFChallenge]:
        statement = (
            select(CTFChallenge)
            .where(CTFChallenge.status == CTFChallengeStatus.PUBLISHED)
            .order_by(
                CTFChallenge.group_id,
                CTFChallenge.difficulty,
                CTFChallenge.title,
            )
        )

        if group_id is not None:
            statement = statement.where(
                CTFChallenge.group_id == group_id,
            )

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_published_group(
        self,
        group_id: UUID,
    ) -> CTFChallengeGroup | None:
        result = await self.session.execute(
            select(CTFChallengeGroup).where(
                CTFChallengeGroup.id == group_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_attempt(
        self,
        *,
        attempt_id: UUID,
        learner_id: UUID,
    ) -> CTFAttempt | None:
        result = await self.session.execute(
            select(CTFAttempt)
            .where(
                CTFAttempt.id == attempt_id,
                CTFAttempt.learner_id == learner_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_next_attempt_number(
        self,
        *,
        challenge_id: UUID,
        learner_id: UUID,
    ) -> int:
        lock_key = f"ctf-attempt-number:{learner_id}:{challenge_id}"

        await self.session.execute(
            text(
                """
                SELECT pg_advisory_xact_lock(
                    hashtextextended(:lock_key, 0)
                )
                """
            ),
            {"lock_key": lock_key},
        )

        result = await self.session.execute(
            select(
                func.max(CTFAttempt.attempt_number),
            ).where(
                CTFAttempt.challenge_id == challenge_id,
                CTFAttempt.learner_id == learner_id,
            )
        )

        current_max = result.scalar_one()
        return (current_max or 0) + 1

    async def create_attempt(
        self,
        attempt: CTFAttempt,
    ) -> CTFAttempt:
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def create_submission(
        self,
        submission: CTFSubmission,
    ) -> CTFSubmission:
        self.session.add(submission)
        await self.session.flush()
        return submission

    async def list_attempts(
        self,
        *,
        challenge_id: UUID,
        learner_id: UUID,
    ) -> list[CTFAttempt]:
        result = await self.session.execute(
            select(CTFAttempt)
            .where(
                CTFAttempt.challenge_id == challenge_id,
                CTFAttempt.learner_id == learner_id,
            )
            .order_by(CTFAttempt.attempt_number)
        )

        return list(result.scalars().all())

    async def list_submissions(
        self,
        *,
        attempt_id: UUID,
        learner_id: UUID,
    ) -> list[CTFSubmission]:
        result = await self.session.execute(
            select(CTFSubmission)
            .join(
                CTFAttempt,
                CTFSubmission.attempt_id == CTFAttempt.id,
            )
            .where(
                CTFSubmission.attempt_id == attempt_id,
                CTFAttempt.learner_id == learner_id,
            )
            .order_by(CTFSubmission.submitted_at)
        )

        return list(result.scalars().all())
