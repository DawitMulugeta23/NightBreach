from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .models import LearnerProfile
from .questions import TREE, AnswerSet, Question, next_question
from .repository import LearnerProfileRepository
from .scoring import summarise


class OnboardingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = LearnerProfileRepository(session)

    async def get_or_create(self, learner_id: UUID) -> LearnerProfile:
        profile = await self._repo.get_by_learner(learner_id)
        if profile is None:
            profile = LearnerProfile(learner_id=learner_id)
            await self._repo.upsert(profile)
        return profile

    def current_question(self, answers: AnswerSet) -> Question | None:
        return next_question(answers)

    async def answer(
        self,
        *,
        learner_id: UUID,
        answers: AnswerSet,
    ) -> tuple[Question | None, dict | None]:
        """Return (next_question, final_profile_dict | None)."""
        next_q = self.current_question(answers)
        if next_q is not None:
            return next_q, None

        summary = summarise(answers)
        profile = await self.get_or_create(learner_id)

        for key, value in summary.items():
            setattr(profile, key, value)

        from datetime import datetime, timezone
        profile.completed_at = datetime.now(timezone.utc)

        await self._session.commit()
        return None, summary

    @staticmethod
    def progress(answers: AnswerSet) -> dict:
        applicable = [q for q in TREE if q.gate(answers) or q.id in answers]
        return {
            "answered": len([q for q in applicable if q.id in answers]),
            "total": len(applicable),
        }