from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.core.errors import NotFoundError
from app.domains.ctf.evaluator import (
    CTFEvaluationConfigurationError,
    evaluate_submission,
)
from app.domains.ctf.repository import CTFRepository
from app.domains.ctf.state_machine import (
    InvalidCTFAttemptTransition,
    validate_attempt_transition,
)
from app.models.ctf_attempt import CTFAttempt, CTFAttemptStatus
from app.models.ctf_submission import CTFSubmission


class CTFAttemptNotActiveError(Exception):
    pass


class CTFEnvironmentFailureTransitionError(Exception):
    pass


class CTFService:
    def __init__(self, repository: CTFRepository) -> None:
        self.repository = repository

    async def list_challenges(
        self,
        *,
        group_id: UUID | None = None,
    ) -> list:
        return await self.repository.list_published_challenges(
            group_id=group_id,
        )

    async def get_challenge(
        self,
        *,
        challenge_id: UUID,
    ):
        challenge = await self.repository.get_published_challenge(
            challenge_id,
        )

        if challenge is None:
            raise NotFoundError("CTF challenge not found")

        return challenge

    async def get_challenge_by_slug(
        self,
        *,
        slug: str,
    ):
        challenge = await self.repository.get_published_challenge_by_slug(
            slug,
        )

        if challenge is None:
            raise NotFoundError("CTF challenge not found")

        return challenge

    async def start_attempt(
        self,
        *,
        learner_id: UUID,
        challenge_id: UUID,
        environment_id: UUID | None = None,
        session_id: str | None = None,
    ) -> CTFAttempt:
        challenge = await self.repository.get_published_challenge(
            challenge_id,
        )

        if challenge is None:
            raise NotFoundError("CTF challenge not found")

        attempt_number = await self.repository.get_next_attempt_number(
            challenge_id=challenge_id,
            learner_id=learner_id,
        )

        now = datetime.now(timezone.utc)

        attempt = CTFAttempt(
            id=uuid4(),
            learner_id=learner_id,
            challenge_id=challenge.id,
            environment_id=environment_id,
            session_id=session_id,
            attempt_number=attempt_number,
            status=CTFAttemptStatus.CREATED,
        )

        await self.repository.create_attempt(attempt)

        validate_attempt_transition(
            attempt.status,
            CTFAttemptStatus.STARTED,
        )

        attempt.status = CTFAttemptStatus.STARTED
        attempt.started_at = now

        await self.repository.session.flush()

        return attempt

    async def mark_in_progress(
        self,
        *,
        attempt_id: UUID,
        learner_id: UUID,
    ) -> CTFAttempt:
        attempt = await self.repository.get_attempt(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise NotFoundError("CTF attempt not found")

        if attempt.status == CTFAttemptStatus.IN_PROGRESS:
            return attempt

        validate_attempt_transition(
            attempt.status,
            CTFAttemptStatus.IN_PROGRESS,
        )

        attempt.status = CTFAttemptStatus.IN_PROGRESS

        await self.repository.session.flush()

        return attempt

    async def submit(
        self,
        *,
        attempt_id: UUID,
        learner_id: UUID,
        submission_value: str,
    ) -> tuple[CTFAttempt, CTFSubmission]:
        attempt = await self.repository.get_attempt(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise NotFoundError("CTF attempt not found")

        if attempt.status in {
            CTFAttemptStatus.PASSED,
            CTFAttemptStatus.FAILED,
            CTFAttemptStatus.ENVIRONMENT_FAILED,
        }:
            raise CTFAttemptNotActiveError(
                "CTF attempt is not active."
            )

        if attempt.status == CTFAttemptStatus.STARTED:
            validate_attempt_transition(
                attempt.status,
                CTFAttemptStatus.IN_PROGRESS,
            )
            attempt.status = CTFAttemptStatus.IN_PROGRESS

        if attempt.status != CTFAttemptStatus.IN_PROGRESS:
            raise CTFAttemptNotActiveError(
                "CTF attempt is not active."
            )

        challenge = await self.repository.get_published_challenge(
            attempt.challenge_id,
        )

        if challenge is None:
            raise NotFoundError("CTF challenge not found")

        now = datetime.now(timezone.utc)

        validate_attempt_transition(
            attempt.status,
            CTFAttemptStatus.SUBMITTED,
        )
        attempt.status = CTFAttemptStatus.SUBMITTED

        await self.repository.session.flush()

        validate_attempt_transition(
            attempt.status,
            CTFAttemptStatus.EVALUATING,
        )
        attempt.status = CTFAttemptStatus.EVALUATING

        await self.repository.session.flush()

        # The evaluator reads the authoritative validation configuration
        # from the persisted challenge. The learner never supplies the
        # expected answer, expected flag, or accepted values.
        evaluation = evaluate_submission(
            challenge=challenge,
            submission=submission_value,
        )

        submission = CTFSubmission(
            id=uuid4(),
            attempt_id=attempt.id,
            submission_value=submission_value,
            submitted_at=now,
            result=evaluation.result,
        )

        await self.repository.create_submission(submission)

        if evaluation.passed:
            validate_attempt_transition(
                attempt.status,
                CTFAttemptStatus.PASSED,
            )
            attempt.status = CTFAttemptStatus.PASSED
        else:
            validate_attempt_transition(
                attempt.status,
                CTFAttemptStatus.FAILED,
            )
            attempt.status = CTFAttemptStatus.FAILED

        attempt.completed_at = now

        await self.repository.session.flush()

        return attempt, submission

    async def mark_environment_failed(
        self,
        *,
        attempt_id: UUID,
        learner_id: UUID,
    ) -> CTFAttempt:
        attempt = await self.repository.get_attempt(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise NotFoundError("CTF attempt not found")

        if attempt.status == CTFAttemptStatus.ENVIRONMENT_FAILED:
            return attempt

        if attempt.status not in {
            CTFAttemptStatus.CREATED,
            CTFAttemptStatus.STARTED,
            CTFAttemptStatus.IN_PROGRESS,
        }:
            raise CTFEnvironmentFailureTransitionError(
                "CTF environment cannot be failed from the current attempt state."
            )

        attempt.status = CTFAttemptStatus.ENVIRONMENT_FAILED
        attempt.completed_at = datetime.now(timezone.utc)

        await self.repository.session.flush()

        return attempt

    async def list_attempts(
        self,
        *,
        learner_id: UUID,
        challenge_id: UUID,
    ) -> list[CTFAttempt]:
        return await self.repository.list_attempts(
            challenge_id=challenge_id,
            learner_id=learner_id,
        )

    async def get_attempt(
        self,
        *,
        learner_id: UUID,
        attempt_id: UUID,
    ) -> CTFAttempt:
        attempt = await self.repository.get_attempt(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise NotFoundError("CTF attempt not found")

        return attempt

    async def list_submissions(
        self,
        *,
        learner_id: UUID,
        attempt_id: UUID,
    ) -> list[CTFSubmission]:
        attempt = await self.repository.get_attempt(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise NotFoundError("CTF attempt not found")

        return await self.repository.list_submissions(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )
