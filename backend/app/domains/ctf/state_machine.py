from app.models.ctf_attempt import CTFAttemptStatus


ALLOWED_ATTEMPT_TRANSITIONS = {
    CTFAttemptStatus.CREATED: {
        CTFAttemptStatus.STARTED,
    },
    CTFAttemptStatus.STARTED: {
        CTFAttemptStatus.IN_PROGRESS,
    },
    CTFAttemptStatus.IN_PROGRESS: {
        CTFAttemptStatus.SUBMITTED,
    },
    CTFAttemptStatus.SUBMITTED: {
        CTFAttemptStatus.EVALUATING,
    },
    CTFAttemptStatus.EVALUATING: {
        CTFAttemptStatus.PASSED,
        CTFAttemptStatus.FAILED,
    },
    CTFAttemptStatus.PASSED: set(),
    CTFAttemptStatus.FAILED: set(),
    CTFAttemptStatus.ENVIRONMENT_FAILED: set(),
}


class InvalidCTFAttemptTransition(Exception):
    pass


def validate_attempt_transition(
    current: CTFAttemptStatus,
    target: CTFAttemptStatus,
) -> None:
    allowed = ALLOWED_ATTEMPT_TRANSITIONS.get(
        current,
        set(),
    )

    if target not in allowed:
        raise InvalidCTFAttemptTransition(
            f"Invalid CTF attempt transition: "
            f"{current.value} -> {target.value}"
        )
