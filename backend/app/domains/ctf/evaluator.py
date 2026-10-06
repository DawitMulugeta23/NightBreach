from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.models.ctf_challenge import (
    CTFChallenge,
    CTFChallengeType,
)


class CTFComparison(str, Enum):
    EXACT = "exact"
    NORMALIZED = "normalized"
    CASE_INSENSITIVE = "case_insensitive"


class CTFEvaluationConfigurationError(Exception):
    pass


@dataclass(frozen=True)
class CTFEvaluationResult:
    passed: bool
    result: str


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def compare_values(
    submitted: str,
    expected: str,
    comparison: CTFComparison,
) -> bool:
    if comparison == CTFComparison.EXACT:
        return submitted == expected

    if comparison == CTFComparison.CASE_INSENSITIVE:
        return (
            submitted.strip().casefold()
            == expected.strip().casefold()
        )

    if comparison == CTFComparison.NORMALIZED:
        return normalize_text(submitted) == normalize_text(expected)

    return False


def _comparison_from_config(
    config: dict[str, Any],
) -> CTFComparison:
    value = config.get(
        "comparison",
        CTFComparison.EXACT.value,
    )

    try:
        return CTFComparison(value)
    except (TypeError, ValueError) as exc:
        raise CTFEvaluationConfigurationError(
            "Invalid CTF validation configuration."
        ) from exc


def _expected_value(
    challenge: CTFChallenge,
) -> str:
    config = challenge.validation_config or {}

    if challenge.challenge_type == CTFChallengeType.FLAG:
        value = config.get("expected_flag")

    elif challenge.challenge_type == CTFChallengeType.OUTPUT_EXTRACTION:
        value = config.get("expected_output")

    elif challenge.challenge_type == CTFChallengeType.ANSWER:
        value = config.get("expected_answer")

    else:
        raise CTFEvaluationConfigurationError(
            "Unsupported CTF challenge type."
        )

    if value is None:
        raise CTFEvaluationConfigurationError(
            "CTF challenge has no configured validation value."
        )

    if not isinstance(value, str):
        raise CTFEvaluationConfigurationError(
            "CTF validation value must be a string."
        )

    return value


def evaluate_submission(
    *,
    challenge: CTFChallenge,
    submission: str,
    expected: str | None = None,
) -> CTFEvaluationResult:
    """
    Evaluate exclusively against server-side challenge configuration.

    Never return the expected value or expose validation configuration
    through an error message.
    """
    config = challenge.validation_config or {}

    # A caller may supply the expected value (for example a per-environment
    # lab flag); otherwise it comes from the stored challenge configuration.
    if expected is None:
        expected = _expected_value(challenge)

    comparison = _comparison_from_config(config)

    passed = compare_values(
        submitted=submission,
        expected=expected,
        comparison=comparison,
    )

    return CTFEvaluationResult(
        passed=passed,
        result="passed" if passed else "failed",
    )
