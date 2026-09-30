from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.domains.ctf.repository import CTFRepository
from app.domains.ctf.service import CTFService
from app.domains.progress.service import ProgressService
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
)
from app.models.practice_attempt import PracticeAttempt

from .evaluator import PracticeEvaluator
from .repository import PracticeRepository


class PracticeService:
    def __init__(
        self,
        session: AsyncSession,
        evaluator: PracticeEvaluator | None = None,
    ) -> None:
        self.repository = PracticeRepository(session)
        self.ctf_service = CTFService(
            CTFRepository(session),
        )
        self.evaluator = evaluator or PracticeEvaluator()

    async def start_attempt(
        self,
        *,
        activity_id: UUID,
        learner_id: UUID,
        environment_id: UUID | None = None,
        session_id: str | None = None,
    ) -> PracticeAttempt:
        activity = await self.repository.get_published_activity(
            activity_id
        )

        if activity is None:
            raise NotFoundError("Practice activity not found.")

        attempt_no = await self.repository.get_next_attempt_number(
            activity_id=activity_id,
            learner_id=learner_id,
        )

        ctf_attempt_id = None

        if activity.activity_type == PracticeActivityType.GUIDED_CTF:
            challenge_id = self._get_ctf_challenge_id(activity)

            ctf_attempt = await self.ctf_service.start_attempt(
                learner_id=learner_id,
                challenge_id=challenge_id,
                environment_id=environment_id,
                session_id=session_id,
            )

            ctf_attempt_id = ctf_attempt.id

        attempt = PracticeAttempt(
            practice_activity_id=activity.id,
            learner_id=learner_id,
            ctf_attempt_id=ctf_attempt_id,
            attempt_no=attempt_no,
            started_at=datetime.now(timezone.utc),
        )

        return await self.repository.create_attempt(attempt)

    async def submit_attempt(
        self,
        *,
        attempt_id: UUID,
        learner_id: UUID,
        submission: str,
    ) -> PracticeAttempt:
        attempt = await self.repository.get_attempt(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise NotFoundError("Practice attempt not found.")

        if attempt.submitted_at is not None:
            raise ValidationError(
                "Practice attempt has already been submitted."
            )

        activity = await self.repository.get_published_activity(
            attempt.practice_activity_id
        )

        if activity is None:
            raise NotFoundError("Practice activity not found.")

        if activity.activity_type == PracticeActivityType.GUIDED_CTF:
            return await self._submit_guided_ctf_attempt(
                attempt=attempt,
                learner_id=learner_id,
                submission=submission,
            )

        try:
            evaluation = self.evaluator.evaluate(
                activity,
                submission,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        attempt.submission_ref = submission
        attempt.result = (
            "SUCCESS"
            if evaluation.successful
            else "FAILED"
        )
        attempt.score = evaluation.score
        attempt.submitted_at = datetime.now(timezone.utc)

        if evaluation.successful:
            await self._process_successful_activity(
                learner_id=learner_id,
                activity_id=activity.id,
            )

        return attempt

    async def _submit_guided_ctf_attempt(
        self,
        *,
        attempt: PracticeAttempt,
        learner_id: UUID,
        submission: str,
    ) -> PracticeAttempt:
        if attempt.ctf_attempt_id is None:
            raise ValidationError(
                "Guided CTF practice attempt is missing its CTF attempt."
            )

        try:
            ctf_attempt, _ = await self.ctf_service.submit(
                attempt_id=attempt.ctf_attempt_id,
                learner_id=learner_id,
                submission_value=submission,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        attempt.submission_ref = submission
        attempt.result = (
            "SUCCESS"
            if ctf_attempt.status.value == "passed"
            else "FAILED"
        )
        attempt.score = (
            1
            if ctf_attempt.status.value == "passed"
            else 0
        )
        attempt.submitted_at = datetime.now(timezone.utc)

        if ctf_attempt.status.value == "passed":
            await self._process_successful_activity(
                learner_id=learner_id,
                activity_id=attempt.practice_activity_id,
            )

        return attempt

    async def _process_successful_activity(
        self,
        *,
        learner_id: UUID,
        activity_id: UUID,
    ) -> None:
        progress_service = ProgressService(self.repository.session)

        await progress_service.process_successful_activity(
            learner_id=learner_id,
            activity_id=activity_id,
        )

    @staticmethod
    def _get_ctf_challenge_id(
        activity: PracticeActivity,
    ) -> UUID:
        challenge_id = activity.configuration.get("challenge_id")

        if challenge_id is None:
            raise ValidationError(
                "Guided CTF activity is missing challenge_id."
            )

        try:
            return UUID(str(challenge_id))
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValidationError(
                "Guided CTF activity has an invalid challenge_id."
            ) from exc

    async def get_attempt(
        self,
        *,
        attempt_id: UUID,
        learner_id: UUID,
    ) -> PracticeAttempt:
        attempt = await self.repository.get_attempt(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise NotFoundError("Practice attempt not found.")

        return attempt

    async def list_attempts(
        self,
        *,
        activity_id: UUID,
        learner_id: UUID,
    ) -> list[PracticeAttempt]:
        activity = await self.repository.get_published_activity(
            activity_id
        )

        if activity is None:
            raise NotFoundError("Practice activity not found.")

        return await self.repository.list_attempts(
            activity_id=activity_id,
            learner_id=learner_id,
        )
