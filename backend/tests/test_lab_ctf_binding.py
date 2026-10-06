from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.errors import ConflictError, NotFoundError
from app.domains.ctf.evaluator import (
    CTFEvaluationConfigurationError,
    evaluate_submission,
)
from app.domains.ctf.service import CTFService
from app.domains.sandbox.labs.ctf_binding import (
    LabChallengeConfigurationError,
    LabChallengeResolver,
)
from app.domains.sandbox.labs.flags import derive_flag
from app.domains.sandbox.labs.registry import get_lab
from app.models.ctf_attempt import CTFAttemptStatus
from app.models.ctf_challenge import CTFChallengeType
from app.models.sandbox import EnvironmentState

SLUG = "linux-file-permissions"
OBJECTIVE = "permissions-flag-001"
REFERENCE = {"slug": SLUG, "objective_id": OBJECTIVE}
LEARNER = uuid4()


def make_environment(**overrides):
    values = dict(
        id=uuid4(), learner_id=LEARNER, lab_slug=SLUG,
        lab_secret="secret-value", state=EnvironmentState.READY,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


class FakeEnvironmentRepository:
    def __init__(self, environment=None):
        self.environment = environment

    async def get_for_learner(self, *, environment_id, learner_id):
        env = self.environment
        if env is not None and env.id == environment_id and env.learner_id == learner_id:
            return env
        return None


def make_resolver(environment=None):
    resolver = LabChallengeResolver(session=SimpleNamespace())
    resolver.repository = FakeEnvironmentRepository(environment)
    return resolver


def start(resolver, environment_id, learner_id=LEARNER):
    return resolver.check_attempt_start(
        learner_id=learner_id, environment_id=environment_id, lab_reference=REFERENCE
    )


# --- resolver ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_requires_an_environment():
    with pytest.raises(ConflictError):
        await start(make_resolver(make_environment()), None)


@pytest.mark.asyncio
async def test_start_accepts_a_running_environment_of_the_learner():
    environment = make_environment()
    await start(make_resolver(environment), environment.id)


@pytest.mark.asyncio
async def test_start_hides_other_learners_environments():
    environment = make_environment(learner_id=uuid4())
    with pytest.raises(NotFoundError):
        await start(make_resolver(environment), environment.id)


@pytest.mark.asyncio
async def test_start_rejects_environment_of_a_different_lab():
    environment = make_environment(lab_slug="some-other-lab")
    with pytest.raises(NotFoundError):
        await start(make_resolver(environment), environment.id)


@pytest.mark.asyncio
async def test_start_rejects_environment_that_is_not_running():
    environment = make_environment(state=EnvironmentState.STOPPED)
    with pytest.raises(ConflictError):
        await start(make_resolver(environment), environment.id)


@pytest.mark.asyncio
async def test_expected_flag_is_the_derived_environment_flag():
    environment = make_environment()
    flag = await make_resolver(environment).expected_flag(
        learner_id=LEARNER, environment_id=environment.id, lab_reference=REFERENCE
    )
    assert flag == derive_flag(
        secret=environment.lab_secret,
        environment_id=environment.id,
        objective=get_lab(SLUG).objective(OBJECTIVE),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("reference", [
    {"slug": "no-such-lab", "objective_id": OBJECTIVE},
    {"slug": SLUG, "objective_id": "no-such-objective"},
    {"slug": SLUG},
    {},
])
async def test_misconfigured_lab_reference_is_a_configuration_error(reference):
    with pytest.raises(LabChallengeConfigurationError):
        await make_resolver(make_environment()).expected_flag(
            learner_id=LEARNER, environment_id=uuid4(), lab_reference=reference
        )


# --- evaluator --------------------------------------------------------------

def lab_challenge(**config):
    return SimpleNamespace(
        id=uuid4(),
        challenge_type=CTFChallengeType.FLAG,
        validation_config={"lab": REFERENCE, "comparison": "normalized", **config},
    )


def test_evaluator_uses_the_supplied_expected_value():
    challenge = lab_challenge()
    assert evaluate_submission(challenge=challenge, submission="NB{x}\n", expected="NB{x}").passed
    assert not evaluate_submission(challenge=challenge, submission="NB{y}", expected="NB{x}").passed


def test_evaluator_without_expected_value_still_needs_stored_configuration():
    with pytest.raises(CTFEvaluationConfigurationError):
        evaluate_submission(challenge=lab_challenge(), submission="NB{x}")


# --- CTFService -------------------------------------------------------------

class FakeCTFRepository:
    def __init__(self, challenge, attempt=None):
        self.challenge = challenge
        self.attempt = attempt
        self.created_attempts = []
        self.created_submissions = []
        self.session = SimpleNamespace(flush=AsyncMock())

    async def get_published_challenge(self, challenge_id):
        return self.challenge

    async def get_next_attempt_number(self, *, challenge_id, learner_id):
        return 1

    async def create_attempt(self, attempt):
        self.created_attempts.append(attempt)
        return attempt

    async def get_attempt(self, *, attempt_id, learner_id):
        return self.attempt

    async def create_submission(self, submission):
        self.created_submissions.append(submission)
        return submission


class FakeResolver:
    def __init__(self, expected="NB{perm_0123456789abcdef}", error=None):
        self.expected = expected
        self.error = error
        self.start_calls = []
        self.flag_calls = []

    async def check_attempt_start(self, **kwargs):
        self.start_calls.append(kwargs)
        if self.error:
            raise self.error

    async def expected_flag(self, **kwargs):
        self.flag_calls.append(kwargs)
        if self.error:
            raise self.error
        return self.expected


def make_attempt(environment_id=None):
    return SimpleNamespace(
        id=uuid4(), learner_id=LEARNER, challenge_id=uuid4(),
        environment_id=environment_id, status=CTFAttemptStatus.STARTED, completed_at=None,
    )


@pytest.mark.asyncio
async def test_lab_challenge_start_checks_the_environment():
    resolver, repo = FakeResolver(), FakeCTFRepository(lab_challenge())
    environment_id = uuid4()

    attempt = await CTFService(repo, lab_resolver=resolver).start_attempt(
        learner_id=LEARNER, challenge_id=uuid4(), environment_id=environment_id
    )

    assert attempt.environment_id == environment_id
    assert resolver.start_calls[0]["environment_id"] == environment_id
    assert resolver.start_calls[0]["lab_reference"] == REFERENCE


@pytest.mark.asyncio
async def test_lab_challenge_start_is_refused_when_the_environment_check_fails():
    repo = FakeCTFRepository(lab_challenge())
    service = CTFService(repo, lab_resolver=FakeResolver(error=NotFoundError("nope")))

    with pytest.raises(NotFoundError):
        await service.start_attempt(learner_id=LEARNER, challenge_id=uuid4(), environment_id=uuid4())

    assert repo.created_attempts == []


@pytest.mark.asyncio
async def test_lab_challenge_without_a_resolver_is_a_configuration_error():
    with pytest.raises(CTFEvaluationConfigurationError):
        await CTFService(FakeCTFRepository(lab_challenge())).start_attempt(
            learner_id=LEARNER, challenge_id=uuid4(), environment_id=uuid4()
        )


@pytest.mark.asyncio
async def test_plain_challenge_never_consults_the_resolver():
    challenge = SimpleNamespace(
        id=uuid4(), challenge_type=CTFChallengeType.FLAG,
        validation_config={"expected_flag": "NB{static}"},
    )
    resolver, repo = FakeResolver(), FakeCTFRepository(challenge, make_attempt())
    service = CTFService(repo, lab_resolver=resolver)

    await service.start_attempt(learner_id=LEARNER, challenge_id=challenge.id, environment_id=None)
    attempt, _ = await service.submit(
        attempt_id=repo.attempt.id, learner_id=LEARNER, submission_value="NB{static}"
    )

    assert attempt.status == CTFAttemptStatus.PASSED
    assert resolver.start_calls == [] and resolver.flag_calls == []


@pytest.mark.asyncio
async def test_lab_submission_passes_with_the_environment_flag():
    environment_id = uuid4()
    resolver = FakeResolver()
    repo = FakeCTFRepository(lab_challenge(), make_attempt(environment_id))

    attempt, submission = await CTFService(repo, lab_resolver=resolver).submit(
        attempt_id=repo.attempt.id, learner_id=LEARNER,
        submission_value="  NB{perm_0123456789abcdef}\n",
    )

    assert attempt.status == CTFAttemptStatus.PASSED
    assert submission.result == "passed"
    assert resolver.flag_calls[0]["environment_id"] == environment_id


@pytest.mark.asyncio
async def test_lab_submission_fails_with_a_wrong_flag():
    repo = FakeCTFRepository(lab_challenge(), make_attempt(uuid4()))

    attempt, submission = await CTFService(repo, lab_resolver=FakeResolver()).submit(
        attempt_id=repo.attempt.id, learner_id=LEARNER, submission_value="NB{perm_ffffffffffffffff}"
    )

    assert attempt.status == CTFAttemptStatus.FAILED
    assert submission.result == "failed"


@pytest.mark.asyncio
async def test_lab_submission_requires_a_running_environment():
    repo = FakeCTFRepository(lab_challenge(), make_attempt(uuid4()))
    service = CTFService(repo, lab_resolver=FakeResolver(error=ConflictError("not running")))

    with pytest.raises(ConflictError):
        await service.submit(
            attempt_id=repo.attempt.id, learner_id=LEARNER,
            submission_value="NB{perm_0123456789abcdef}",
        )

    assert repo.created_submissions == []
    assert repo.attempt.status not in (
        CTFAttemptStatus.SUBMITTED, CTFAttemptStatus.EVALUATING,
        CTFAttemptStatus.PASSED, CTFAttemptStatus.FAILED,
    )
