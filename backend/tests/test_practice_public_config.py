from app.domains.practice.public_config import build_public_configuration


def test_public_configuration_preserves_learner_visible_fields():
    configuration = {
        "options": ["A", "B", "C"],
        "placeholder": "Choose an answer",
    }

    result = build_public_configuration(configuration)

    assert result == configuration


def test_public_configuration_removes_expected_answer():
    configuration = {
        "options": ["A", "B", "C"],
        "expected_answer": "B",
    }

    result = build_public_configuration(configuration)

    assert result == {
        "options": ["A", "B", "C"],
    }

    assert "expected_answer" not in result


def test_public_configuration_removes_correct_answer():
    configuration = {
        "options": ["A", "B", "C"],
        "correct_answer": "B",
    }

    result = build_public_configuration(configuration)

    assert result == {
        "options": ["A", "B", "C"],
    }

    assert "correct_answer" not in result


def test_public_configuration_removes_expected_value():
    configuration = {
        "prompt": "Submit the hostname.",
        "expected": "nightbreach",
    }

    result = build_public_configuration(configuration)

    assert result == {
        "prompt": "Submit the hostname.",
    }

    assert "expected" not in result


def test_public_configuration_does_not_mutate_original():
    configuration = {
        "options": ["A", "B"],
        "correct_answer": "A",
    }

    result = build_public_configuration(configuration)

    assert configuration == {
        "options": ["A", "B"],
        "correct_answer": "A",
    }

    assert result == {
        "options": ["A", "B"],
    }
