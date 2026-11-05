"""Regression tests for answer parsing and score calculation."""

from core.grading_engine import (
    generate_sample_answer_key,
    grade_submission,
    parse_answer_string,
)


def test_grade_all_correct_uses_requested_question_count():
    result = grade_submission({1: "a", 2: "B"}, {1: "A", 2: "B"}, total_questions=2)

    assert result["score"] == 10.0
    assert result["correct_count"] == 2
    assert result["wrong_count"] == 0


def test_blank_whitespace_is_not_marked_wrong():
    result = grade_submission({1: "   "}, {1: "A"}, total_questions=1)

    assert result["blank_count"] == 1
    assert result["wrong_count"] == 0
    assert result["details"][1]["student"] == "Trống"


def test_multiple_answer_with_non_string_value_does_not_crash():
    result = grade_submission({1: ["A", 2]}, {1: "A"}, total_questions=1)

    assert result["multiple_count"] == 1
    assert result["wrong_count"] == 1
    assert result["details"][1]["student"] == "A,2"


def test_parse_indexed_and_compact_answer_formats():
    assert parse_answer_string("1:A 2:b 3-C", max_q=3) == {1: "A", 2: "B", 3: "C"}
    assert parse_answer_string("A b C d", max_q=4) == {1: "A", 2: "B", 3: "C", 4: "D"}


def test_sample_key_has_requested_size_and_valid_options():
    result = generate_sample_answer_key(20)

    assert len(result) == 20
    assert set(result.values()) <= {"A", "B", "C", "D"}
