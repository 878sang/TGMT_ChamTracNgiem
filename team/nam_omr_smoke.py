"""Batch smoke runner assigned to Nam.

Run from the repository root:
    python -m team.nam_omr_smoke Tets
"""

import argparse
from pathlib import Path

from core.exam_processor import process_single_submission
from core.grading_engine import generate_sample_answer_key


def run_smoke(folder: str, total_questions: int = 50) -> list[dict[str, object]]:
    """Process every supported image and return compact QA rows."""
    answer_key = generate_sample_answer_key(total_questions)
    rows = []
    for image_path in sorted(Path(folder).glob("*")):
        if image_path.suffix.lower() not in {".jpg", ".jpeg", ".jpe", ".png"}:
            continue
        result = process_single_submission(
            str(image_path), answer_key, total_questions=total_questions
        )
        rows.append(
            {
                "file": image_path.name,
                "status": result.status,
                "score": result.score,
                "correct": result.correct_count,
                "blank": result.blank_count,
                "multiple": result.multiple_count,
                "needs_review": result.needs_review,
                "error": result.error_message,
            }
        )
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke-test FormTHPT50 images")
    parser.add_argument("folder", nargs="?", default="Tets")
    args = parser.parse_args()
    for row in run_smoke(args.folder):
        print(row)
