from __future__ import annotations

from typing import Any


# Keys that can contain answers or other evaluator-only information.
_PRIVATE_CONFIGURATION_KEYS = {
    "expected_answer",
    "correct_answer",
    "expected",
}


def build_public_configuration(configuration: dict[str, Any]) -> dict[str, Any]:
    """
    Return the learner-visible portion of an activity configuration.

    Evaluation configuration is authoritative server-side and may contain
    answers or other information that must not be exposed before submission.
    The public representation therefore removes evaluator-only keys while
    preserving learner-facing configuration such as multiple-choice options.
    """
    return {
        key: value
        for key, value in configuration.items()
        if key not in _PRIVATE_CONFIGURATION_KEYS
    }
