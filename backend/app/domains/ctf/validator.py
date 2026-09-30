from enum import Enum


class ValidationMode(str, Enum):
    EXACT = "EXACT"
    CASE_INSENSITIVE = "CASE_INSENSITIVE"
    NORMALIZED = "NORMALIZED"
    MULTIPLE_ACCEPTED = "MULTIPLE_ACCEPTED"
    FLAG_VALIDATION = "FLAG_VALIDATION"


def normalize_answer(value: str) -> str:
    return " ".join(
        value.strip().split()
    )


class CTFValidator:

    def validate(
        self,
        *,
        submitted_value: str,
        expected_value: str | None,
        accepted_values: list[str] | None,
        mode: ValidationMode,
    ) -> bool:

        if mode == ValidationMode.EXACT:
            return (
                expected_value is not None
                and submitted_value == expected_value
            )

        if mode == ValidationMode.CASE_INSENSITIVE:
            return (
                expected_value is not None
                and submitted_value.casefold()
                == expected_value.casefold()
            )

        if mode == ValidationMode.NORMALIZED:
            return (
                expected_value is not None
                and normalize_answer(submitted_value)
                == normalize_answer(expected_value)
            )

        if mode == ValidationMode.MULTIPLE_ACCEPTED:
            if not accepted_values:
                return False

            submitted = normalize_answer(
                submitted_value
            ).casefold()

            return any(
                normalize_answer(value).casefold()
                == submitted
                for value in accepted_values
            )

        if mode == ValidationMode.FLAG_VALIDATION:
            return (
                expected_value is not None
                and submitted_value.strip()
                == expected_value.strip()
            )

        raise ValueError(
            f"Unsupported validation mode: {mode}"
        )
