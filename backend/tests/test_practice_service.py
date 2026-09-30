from uuid import uuid4

import pytest

from app.core.errors import NotFoundError, ValidationError
from app.db.session import AsyncSessionLocal
from app.domains.practice.service import PracticeService
from app.models.practice import Practice, PracticeStatus
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)
from app.models.user import User


async def create_user(session, email: str) -> User:
    user = User(
        id=uuid4(),
        email=email,
        username=f"practice_{uuid4().hex[:11]}",
        hashed_password="test-hash",
    )
    session.add(user)
    await session.flush()
    return user


async def create_published_activity(session) -> PracticeActivity:
    practice = Practice(
        id=uuid4(),
        title="Practice Service Test",
        description="Practice service integration test",
        status=PracticeStatus.PUBLISHED,
    )
    session.add(practice)
    await session.flush()

    activity = PracticeActivity(
        id=uuid4(),
        practice_id=practice.id,
        position=1,
        activity_type=PracticeActivityType.TEXT_QUESTION,
        title="Test Question",
        instructions="Answer the question.",
        required=True,
        evaluation_type=PracticeEvaluationType.TEXT_EXACT,
        configuration={"expected_answer": "Linux"},
        guidance_policy={},
    )
    session.add(activity)
    await session.flush()

    return activity


@pytest.mark.asyncio
async def test_start_attempt_creates_first_attempt():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-start-{uuid4()}@example.com",
        )
        activity = await create_published_activity(session)

        service = PracticeService(session)

        attempt = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        assert attempt.id is not None
        assert attempt.practice_activity_id == activity.id
        assert attempt.learner_id == learner.id
        assert attempt.attempt_no == 1
        assert attempt.started_at is not None
        assert attempt.submitted_at is None

        await session.rollback()


@pytest.mark.asyncio
async def test_second_attempt_gets_next_attempt_number():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-retry-{uuid4()}@example.com",
        )
        activity = await create_published_activity(session)

        service = PracticeService(session)

        first = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        second = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        assert first.attempt_no == 1
        assert second.attempt_no == 2

        await session.rollback()


@pytest.mark.asyncio
async def test_learner_cannot_access_another_learners_attempt():
    async with AsyncSessionLocal() as session:
        owner = await create_user(
            session,
            f"practice-owner-{uuid4()}@example.com",
        )
        other_learner = await create_user(
            session,
            f"practice-other-{uuid4()}@example.com",
        )
        activity = await create_published_activity(session)

        service = PracticeService(session)

        attempt = await service.start_attempt(
            activity_id=activity.id,
            learner_id=owner.id,
        )

        with pytest.raises(
            NotFoundError,
            match="Practice attempt not found",
        ):
            await service.get_attempt(
                attempt_id=attempt.id,
                learner_id=other_learner.id,
            )

        await session.rollback()


@pytest.mark.asyncio
async def test_correct_submission_succeeds():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-success-{uuid4()}@example.com",
        )
        activity = await create_published_activity(session)

        service = PracticeService(session)

        attempt = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        submitted = await service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Linux",
        )

        assert submitted.result == "SUCCESS"
        assert submitted.score == 1
        assert submitted.submission_ref == "Linux"
        assert submitted.submitted_at is not None

        await session.rollback()


@pytest.mark.asyncio
async def test_incorrect_submission_fails():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-failed-{uuid4()}@example.com",
        )
        activity = await create_published_activity(session)

        service = PracticeService(session)

        attempt = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        submitted = await service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Windows",
        )

        assert submitted.result == "FAILED"
        assert submitted.score == 0
        assert submitted.submission_ref == "Windows"
        assert submitted.submitted_at is not None

        await session.rollback()


@pytest.mark.asyncio
async def test_attempt_cannot_be_submitted_twice():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-double-submit-{uuid4()}@example.com",
        )
        activity = await create_published_activity(session)

        service = PracticeService(session)

        attempt = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        await service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="Linux",
        )

        with pytest.raises(
            ValidationError,
            match="already been submitted",
        ):
            await service.submit_attempt(
                attempt_id=attempt.id,
                learner_id=learner.id,
                submission="Linux",
            )

        await session.rollback()


@pytest.mark.asyncio
async def test_unpublished_activity_cannot_start_attempt():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-unpublished-{uuid4()}@example.com",
        )

        practice = Practice(
            id=uuid4(),
            title="Unpublished Practice",
            description="Not available to learners",
            status=PracticeStatus.DRAFT,
        )
        session.add(practice)
        await session.flush()

        activity = PracticeActivity(
            id=uuid4(),
            practice_id=practice.id,
            position=1,
            activity_type=PracticeActivityType.TEXT_QUESTION,
            title="Draft Question",
            instructions="This should not be executable.",
            required=True,
            evaluation_type=PracticeEvaluationType.TEXT_EXACT,
            configuration={"expected_answer": "Linux"},
            guidance_policy={},
        )
        session.add(activity)
        await session.flush()

        service = PracticeService(session)

        with pytest.raises(
            NotFoundError,
            match="Practice activity not found",
        ):
            await service.start_attempt(
                activity_id=activity.id,
                learner_id=learner.id,
            )

        await session.rollback()


@pytest.mark.asyncio
async def test_attempt_history_is_ordered_by_attempt_number():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-history-{uuid4()}@example.com",
        )
        activity = await create_published_activity(session)

        service = PracticeService(session)

        first = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        await service.submit_attempt(
            attempt_id=first.id,
            learner_id=learner.id,
            submission="Linux",
        )

        second = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        await service.submit_attempt(
            attempt_id=second.id,
            learner_id=learner.id,
            submission="Windows",
        )

        history = await service.list_attempts(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        assert len(history) == 2
        assert history[0].attempt_no == 1
        assert history[1].attempt_no == 2
        assert history[0].result == "SUCCESS"
        assert history[1].result == "FAILED"

        await session.rollback()


async def create_published_guided_ctf_activity(session):
    from app.models.ctf_challenge import (
        CTFChallenge,
        CTFChallengeGroup,
        CTFChallengeMode,
        CTFChallengeStatus,
        CTFChallengeType,
    )

    group = CTFChallengeGroup(
        id=uuid4(),
        code=f"practice-ctf-{uuid4().hex[:10]}",
        name="Practice CTF Test Group",
        description="Group used by Practice CTF integration tests.",
        position=1,
    )

    challenge = CTFChallenge(
        id=uuid4(),
        slug=f"practice-ctf-{uuid4().hex}",
        title="Practice Guided CTF",
        description="Guided CTF challenge for Practice integration.",
        objective="Submit the test flag.",
        scenario="Controlled Practice integration scenario.",
        difficulty="easy",
        mode=CTFChallengeMode.GUIDED,
        status=CTFChallengeStatus.PUBLISHED,
        challenge_type=CTFChallengeType.FLAG,
        validation_config={
            "expected_flag": "NB{practice-ctf}",
            "comparison": "exact",
        },
    )

    group.challenges.append(challenge)

    practice = Practice(
        id=uuid4(),
        title="Guided CTF Practice",
        description="Practice containing a Guided CTF activity.",
        status=PracticeStatus.PUBLISHED,
    )

    activity = PracticeActivity(
        id=uuid4(),
        practice_id=practice.id,
        position=1,
        activity_type=PracticeActivityType.GUIDED_CTF,
        title="Guided CTF Activity",
        instructions="Complete the linked CTF challenge.",
        required=True,
        evaluation_type=PracticeEvaluationType.FLAG_SUBMISSION,
        configuration={
            "challenge_id": str(challenge.id),
        },
        guidance_policy={},
    )

    session.add(group)
    session.add(practice)
    await session.flush()

    session.add(activity)
    await session.flush()

    return activity, challenge


@pytest.mark.asyncio
async def test_guided_ctf_start_creates_and_links_ctf_attempt():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-ctf-start-{uuid4()}@example.com",
        )
        activity, challenge = await create_published_guided_ctf_activity(
            session
        )

        service = PracticeService(session)

        attempt = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        assert attempt.attempt_no == 1
        assert attempt.ctf_attempt_id is not None

        ctf_attempt = await service.ctf_service.get_attempt(
            learner_id=learner.id,
            attempt_id=attempt.ctf_attempt_id,
        )

        assert ctf_attempt.challenge_id == challenge.id
        assert ctf_attempt.learner_id == learner.id
        assert ctf_attempt.attempt_number == 1

        await session.rollback()


@pytest.mark.asyncio
async def test_guided_ctf_correct_submission_succeeds():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-ctf-success-{uuid4()}@example.com",
        )
        activity, _ = await create_published_guided_ctf_activity(
            session
        )

        service = PracticeService(session)

        attempt = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        submitted = await service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="NB{practice-ctf}",
        )

        assert submitted.result == "SUCCESS"
        assert submitted.score == 1
        assert submitted.submission_ref == "NB{practice-ctf}"
        assert submitted.submitted_at is not None

        ctf_attempt = await service.ctf_service.get_attempt(
            learner_id=learner.id,
            attempt_id=submitted.ctf_attempt_id,
        )

        assert ctf_attempt.status.value == "passed"

        await session.rollback()


@pytest.mark.asyncio
async def test_guided_ctf_incorrect_submission_fails():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-ctf-failed-{uuid4()}@example.com",
        )
        activity, _ = await create_published_guided_ctf_activity(
            session
        )

        service = PracticeService(session)

        attempt = await service.start_attempt(
            activity_id=activity.id,
            learner_id=learner.id,
        )

        submitted = await service.submit_attempt(
            attempt_id=attempt.id,
            learner_id=learner.id,
            submission="NB{wrong-flag}",
        )

        assert submitted.result == "FAILED"
        assert submitted.score == 0
        assert submitted.submission_ref == "NB{wrong-flag}"
        assert submitted.submitted_at is not None

        ctf_attempt = await service.ctf_service.get_attempt(
            learner_id=learner.id,
            attempt_id=submitted.ctf_attempt_id,
        )

        assert ctf_attempt.status.value == "failed"

        await session.rollback()


@pytest.mark.asyncio
async def test_guided_ctf_requires_challenge_id():
    async with AsyncSessionLocal() as session:
        learner = await create_user(
            session,
            f"practice-ctf-invalid-{uuid4()}@example.com",
        )

        practice = Practice(
            id=uuid4(),
            title="Invalid Guided CTF Practice",
            description="Missing challenge configuration.",
            status=PracticeStatus.PUBLISHED,
        )
        session.add(practice)
        await session.flush()

        activity = PracticeActivity(
            id=uuid4(),
            practice_id=practice.id,
            position=1,
            activity_type=PracticeActivityType.GUIDED_CTF,
            title="Invalid Guided CTF",
            instructions="This activity has no challenge ID.",
            required=True,
            evaluation_type=PracticeEvaluationType.FLAG_SUBMISSION,
            configuration={},
            guidance_policy={},
        )
        session.add(activity)
        await session.flush()

        service = PracticeService(session)

        with pytest.raises(
            ValidationError,
            match="missing challenge_id",
        ):
            await service.start_attempt(
                activity_id=activity.id,
                learner_id=learner.id,
            )

        await session.rollback()
