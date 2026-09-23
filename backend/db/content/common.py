"""Shared helpers for course content modules."""
import hashlib


def _hash_answer(answer: str) -> str:
    return hashlib.sha256(answer.strip().lower().encode()).hexdigest()


def _hash_answers(answers) -> str:
    """Store one or more acceptable answers joined by '|', each hashed."""
    if isinstance(answers, str):
        answers = [answers]
    return "|".join(_hash_answer(a) for a in answers if a)


def _flag(value: str) -> str:
    """Wrap a plaintext value in the NB{...} flag format."""
    return f"NB{{{value}}}"


def _resolve_answer_hash(q_data: dict) -> str:
    """Return the answer hash for a question, from 'flag' if present, else 'answer_hash'."""
    if "flag" in q_data:
        return _hash_answers(_flag(q_data["flag"]))
    return q_data["answer_hash"]
