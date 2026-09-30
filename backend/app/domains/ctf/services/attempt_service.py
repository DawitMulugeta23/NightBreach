from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.ctf.repositories.attempt_repository import (
    CTFAttemptRepository,
)
from app.domains.ctf.state_machine import (
    validate_attempt_transition,
)
from app.domains.ctf.validator import (
    CTFValidator,
    ValidationMode,
)
from app.models.ctf_attempt import (
    CTFAttempt,
    CTFAttemptStatus,
)
from app.models.ctf_submission import CTFSubmission


class CTFAttemptNotFound(Exception):
    pass


class CTFSubmissionNotAllowed(Exception):
    pass


class CTFAttemptService:

    def __init__(
        self,
        session: AsyncSession,
        validator: CTFValidator,
    ):
        self.session = session
        self.attempts = CTFAttemptRepository(session)
        self.validator = validator

    async def create_attempt(
        self,
        *,
        learner_id: UUID,
        challenge_id: UUID,
        environment_id: UUID | None,
        session_id: str | None,
    ) -> CTFAttempt:

        attempt_number = (
            await self.attempts.get_next_attempt_number(
                learner_id=learner_id,
                challenge_id=challenge_id,
            )
        )

        attempt = CTFAttempt(
            learner_id=learner_id,
            challenge_id=challenge_id,
            environment_id=environment_id,
            session_id=session_id,
            attempt_number=attempt_number,
            status=CTFAttemptStatus.CREATED,
        )

        return await self.attempts.create(attempt)

    async def start_attempt(
        self,
        *,
        learner_id: UUID,
        attempt_id: UUID,
    ) -> CTFAttempt:

        attempt = await self.attempts.get_for_learner(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise CTFAttemptNotFound()

        validate_attempt_transition(
            attempt.status,
            CTFAttemptStatus.STARTED,
        )

        attempt.status = CTFAttemptStatus.STARTED
        attempt.started_at = datetime.now(timezone.utc)

        return await self.attempts.save(attempt)

    async def submit(
        self,
        *,
        learner_id: UUID,
        attempt_id: UUID,
        submission_value: str,
        expected_value: str | None,
        accepted_values: list[str] | None,
        validation_mode: ValidationMode,
    ) -> tuple[CTFSubmission, CTFAttempt]:

        attempt = await self.attempts.get_for_learner(
            attempt_id=attempt_id,
            learner_id=learner_id,
        )

        if attempt is None:
            raise CTFAttemptNotFound()

        if attempt.status in {
            CTFAttemptStatus.PASSED,
            CTFAttemptStatus.FAILED,
            CTFAttemptStatus.ENVIRONMENT_FAILED,
        }:
            raise CTFSubmissionNotAllowed(
                "This attempt is closed."
            )

        if attempt.status not in {
            CTFAttemptStatus.STARTED,
            CTFAttemptStatus.IN_PROGRESS,
        }:
            raise CTFSubmissionNotAllowed(
                f"Cannot submit while attempt is "
                f"{attempt.status.value}."
            )

        if attempt.status == CTFAttemptStatus.STARTED:
            validate_attempt_transition(
                attempt.status,
                CTFAttemptStatus.IN_PROGRESS,
            )

            attempt.status = (
                CTFAttemptStatus.IN_PROGRESS
            )

        passed = self.validator.validate(
            submitted_value=submission_value,
            expected_value=expected_value,
            accepted_values=accepted_values,
            mode=validation_mode,
        )

        submission = CTFSubmission(
            attempt_id=attempt.id,
            submission_value=submission_value,
            submitted_at=datetime.now(timezone.utc),
            result=(
                "ACCEPTED"
                if passed
                else "INCORRECT"
            ),
        )

        self.session.add(submission)

        validate_attempt_transition(
            attempt.status,
            CTFAttemptStatus.SUBMITTED,
        )

        attempt.status = CTFAttemptStatus.SUBMITTED

        await self.session.flush()

        validate_attempt_transition(
            attempt.status,
            CTFAttemptStatus.EVALUATING,
        )

        attempt.status = CTFAttemptStatus.EVALUATING

        await self.session.flush()

        if passed:
            validate_attempt_transition(
                attempt.status,
                CTFAttemptStatus.PASSED,
            )

            attempt.status = CTFAttemptStatus.PASSED
            attempt.completed_at = (
                datetime.now(timezone.utc)
            )

        else:
            validate_attempt_transition(
                attempt.status,
                CTFAttemptStatus.FAILED,
            )

            attempt.status = CTFAttemptStatus.FAILED

        await self.session.flush()
        await self.session.refresh(submission)
        await self.session.refresh(attempt)

        return submission, attempt

    async def retry_attempt(
        self,
        *,
        learner_id: UUID,
        challenge_id: UUID,
        environment_id: UUID | None,
        session_id: str | None,
    ) -> CTFAttempt:

        return await self.create_attempt(
            learner_id=learner_id,
            challenge_id=challenge_id,
            environment_id=environment_id,
            session_id=session_id,
        )
