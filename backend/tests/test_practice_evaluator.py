from uuid import uuid4

import pytest

from app.domains.practice.evaluator import PracticeEvaluator
from app.models.practice_activity import (
    PracticeActivity,
    PracticeActivityType,
    PracticeEvaluationType,
)


def make_activity(
    evaluation_type: PracticeEvaluationType,
    configuration: dict,
) -> PracticeActivity:
    return PracticeActivity(
        id=uuid4(),
        practice_id=uuid4(),
        position=1,
        activity_type=PracticeActivityType.TEXT_QUESTION,
        title="Evaluator Test",
        instructions="Answer the question.",
        required=True,
        evaluation_type=evaluation_type,
        configuration=configuration,
        guidance_policy={},
    )


def test_exact_evaluation_accepts_correct_answer():
    activity = make_activity(
        PracticeEvaluationType.TEXT_EXACT,
        {"expected_answer": "Linux"},
    )

    result = PracticeEvaluator().evaluate(activity, "Linux")

    assert result.successful is True
    assert result.score == 1.0


def test_exact_evaluation_rejects_incorrect_answer():
    activity = make_activity(
        PracticeEvaluationType.TEXT_EXACT,
        {"expected_answer": "Linux"},
    )

    result = PracticeEvaluator().evaluate(activity, "linux")

    assert result.successful is False
    assert result.score == 0.0


def test_case_insensitive_evaluation_ignores_case():
    activity = make_activity(
        PracticeEvaluationType.TEXT_CASE_INSENSITIVE,
        {"expected_answer": "Linux"},
    )

    result = PracticeEvaluator().evaluate(activity, "LINUX")

    assert result.successful is True
    assert result.score == 1.0


def test_case_insensitive_evaluation_rejects_different_answer():
    activity = make_activity(
        PracticeEvaluationType.TEXT_CASE_INSENSITIVE,
        {"expected_answer": "Linux"},
    )

    result = PracticeEvaluator().evaluate(activity, "Windows")

    assert result.successful is False
    assert result.score == 0.0


def test_normalized_evaluation_ignores_outer_and_repeated_whitespace():
    activity = make_activity(
        PracticeEvaluationType.TEXT_NORMALIZED,
        {"expected_answer": "hello world"},
    )

    result = PracticeEvaluator().evaluate(
        activity,
        "  hello    world  ",
    )

    assert result.successful is True
    assert result.score == 1.0


def test_multiple_choice_evaluation_accepts_correct_option():
    activity = make_activity(
        PracticeEvaluationType.MULTIPLE_CHOICE,
        {
            "options": ["A", "B", "C"],
            "correct_answer": "B",
        },
    )

    result = PracticeEvaluator().evaluate(activity, "B")

    assert result.successful is True
    assert result.score == 1.0


def test_multiple_choice_evaluation_rejects_wrong_option():
    activity = make_activity(
        PracticeEvaluationType.MULTIPLE_CHOICE,
        {
            "options": ["A", "B", "C"],
            "correct_answer": "B",
        },
    )

    result = PracticeEvaluator().evaluate(activity, "A")

    assert result.successful is False
    assert result.score == 0.0


def test_malformed_configuration_is_rejected():
    activity = make_activity(
        PracticeEvaluationType.TEXT_EXACT,
        {},
    )

    with pytest.raises(ValueError, match="expected_answer"):
        PracticeEvaluator().evaluate(activity, "Linux")


@pytest.mark.parametrize(
    "evaluation_type",
    [
        PracticeEvaluationType.COMMAND_RESULT,
        PracticeEvaluationType.OUTPUT_EXTRACTION,
        PracticeEvaluationType.FLAG_SUBMISSION,
    ],
)
def test_unsupported_practical_evaluation_types_are_rejected(
    evaluation_type: PracticeEvaluationType,
):
    activity = make_activity(
        evaluation_type,
        {"expected_answer": "Linux"},
    )

    with pytest.raises(ValueError, match="not supported"):
        PracticeEvaluator().evaluate(activity, "Linux")


def test_multiple_choice_rejects_missing_options():
    activity = make_activity(
        PracticeEvaluationType.MULTIPLE_CHOICE,
        {"correct_answer": "B"},
    )

    with pytest.raises(ValueError, match="options"):
        PracticeEvaluator().evaluate(activity, "B")


def test_multiple_choice_rejects_unknown_correct_answer():
    activity = make_activity(
        PracticeEvaluationType.MULTIPLE_CHOICE,
        {
            "options": ["A", "B", "C"],
            "correct_answer": "D",
        },
    )

    with pytest.raises(ValueError, match="one of the configured options"):
        PracticeEvaluator().evaluate(activity, "D")


def test_multiple_choice_rejects_non_string_options():
    activity = make_activity(
        PracticeEvaluationType.MULTIPLE_CHOICE,
        {
            "options": ["A", 2, "C"],
            "correct_answer": "A",
        },
    )

    with pytest.raises(ValueError, match="only strings"):
        PracticeEvaluator().evaluate(activity, "A")


def test_multiple_choice_rejects_missing_correct_answer():
    activity = make_activity(
        PracticeEvaluationType.MULTIPLE_CHOICE,
        {
            "options": ["A", "B", "C"],
        },
    )

    with pytest.raises(ValueError, match="correct_answer"):
        PracticeEvaluator().evaluate(activity, "A")
