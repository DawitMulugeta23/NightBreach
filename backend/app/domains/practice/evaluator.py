from __future__ import annotations

from dataclasses import dataclass

from app.models.practice_activity import (
    PracticeActivity,
    PracticeEvaluationType,
)


@dataclass(frozen=True)
class EvaluationResult:
    successful: bool
    score: float


class PracticeEvaluator:
    """Evaluates learner submissions according to the activity definition."""

    def evaluate(
        self,
        activity: PracticeActivity,
        submission: str,
    ) -> EvaluationResult:
        evaluation_type = activity.evaluation_type
        configuration = activity.configuration

        if evaluation_type == PracticeEvaluationType.MULTIPLE_CHOICE:
            return self._evaluate_multiple_choice(
                configuration,
                submission,
            )

        if evaluation_type == PracticeEvaluationType.TEXT_EXACT:
            return self._evaluate_exact(
                configuration,
                submission,
            )

        if evaluation_type == PracticeEvaluationType.TEXT_CASE_INSENSITIVE:
            return self._evaluate_case_insensitive(
                configuration,
                submission,
            )

        if evaluation_type == PracticeEvaluationType.TEXT_NORMALIZED:
            return self._evaluate_normalized(
                configuration,
                submission,
            )

        raise ValueError(
            f"Evaluation type {evaluation_type.value} is not supported "
            "by the text evaluator."
        )

    @staticmethod
    def _expected_answer(configuration: dict) -> str:
        expected = configuration.get("expected_answer")

        if not isinstance(expected, str):
            raise ValueError(
                "Activity configuration must contain a string "
                "'expected_answer'."
            )

        return expected

    @staticmethod
    def _multiple_choice_configuration(
        configuration: dict,
    ) -> tuple[list[str], str]:
        options = configuration.get("options")
        correct_answer = configuration.get("correct_answer")

        if not isinstance(options, list) or not options:
            raise ValueError(
                "Multiple-choice configuration must contain a non-empty "
                "'options' list."
            )

        if not all(isinstance(option, str) for option in options):
            raise ValueError(
                "Multiple-choice 'options' must contain only strings."
            )

        if not isinstance(correct_answer, str):
            raise ValueError(
                "Multiple-choice configuration must contain a string "
                "'correct_answer'."
            )

        if correct_answer not in options:
            raise ValueError(
                "Multiple-choice 'correct_answer' must be one of the "
                "configured options."
            )

        return options, correct_answer

    def _evaluate_multiple_choice(
        self,
        configuration: dict,
        submission: str,
    ) -> EvaluationResult:
        _, correct_answer = self._multiple_choice_configuration(
            configuration
        )

        successful = submission == correct_answer

        return EvaluationResult(
            successful=successful,
            score=1.0 if successful else 0.0,
        )

    def _evaluate_exact(
        self,
        configuration: dict,
        submission: str,
    ) -> EvaluationResult:
        expected = self._expected_answer(configuration)
        successful = submission == expected

        return EvaluationResult(
            successful=successful,
            score=1.0 if successful else 0.0,
        )

    def _evaluate_case_insensitive(
        self,
        configuration: dict,
        submission: str,
    ) -> EvaluationResult:
        expected = self._expected_answer(configuration)
        successful = submission.casefold() == expected.casefold()

        return EvaluationResult(
            successful=successful,
            score=1.0 if successful else 0.0,
        )

    def _evaluate_normalized(
        self,
        configuration: dict,
        submission: str,
    ) -> EvaluationResult:
        expected = self._normalize(
            self._expected_answer(configuration)
        )
        actual = self._normalize(submission)

        successful = actual == expected

        return EvaluationResult(
            successful=successful,
            score=1.0 if successful else 0.0,
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.strip().split())
