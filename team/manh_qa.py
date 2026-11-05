"""Quality-assurance checks assigned to Mạnh."""

from typing import Any


def validate_submission_result(result: Any, expected_questions: int) -> list[str]:
    """Return actionable consistency errors for one processed submission."""
    errors: list[str] = []
    answers = getattr(result, "answers", {})
    details = getattr(result, "details", {})
    if len(answers) != expected_questions:
        errors.append(f"answers has {len(answers)} items; expected {expected_questions}")
    if getattr(result, "status", "") != "Lỗi" and len(details) != expected_questions:
        errors.append(f"details has {len(details)} items; expected {expected_questions}")
    total = sum(
        int(getattr(result, field, 0))
        for field in ("correct_count", "wrong_count", "blank_count")
    )
    if getattr(result, "status", "") != "Lỗi" and total != expected_questions:
        errors.append(f"score counters total {total}; expected {expected_questions}")
    return errors
