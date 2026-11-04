import json
import os
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

from core.image_alignment import (
    STANDARD_HEIGHT,
    STANDARD_WIDTH,
    _select_marker_quad,
    align_paper,
    find_fiducial_markers,
)
from core.omr_extractor import QUESTION_COORDS, extract_all_data
from core.exam_processor import process_single_submission
from core.sheet_generator import (
    generate_50_mcq_template,
    generate_sample_submission_50_mcq,
)
from core.cv_utils import imread_utf8, imwrite_utf8
from core.visualizer import _locate_bubble_circle


ROOT = Path(__file__).resolve().parents[1]
LAYOUT_PATH = ROOT / "templates" / "layouts" / "thpt50.json"
EXPECTED = {question: "ABCD"[(question - 1) % 4] for question in range(1, 51)}


def _read_answers(image: np.ndarray, total_questions: int = 50) -> dict:
    success, aligned, message = align_paper(image)
    assert success, message
    assert aligned is not None
    result = extract_all_data(aligned, total_questions=total_questions)
    assert result["layout_source"] == "FormTHPT50", result["warning_message"]
    return result


def test_layout_matches_the_supplied_thpt50_sheet():
    layout = json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))
    assert (layout["canvas_w"], layout["canvas_h"]) == (1653, 2337)
    assert layout["capacity"] == 50
    assert [block["rows"] for block in layout["blocks"]] == [25, 25]
    assert [block["first_question"] for block in layout["blocks"]] == [1, 26]
    assert layout["id_blocks"]["student_id"]["columns"] == 6
    assert layout["id_blocks"]["exam_code"]["columns"] == 3
    assert len(layout["markers"]) == 25
    assert (STANDARD_WIDTH, STANDARD_HEIGHT) == (1653, 2337)


def test_clean_sheet_reads_all_answers_and_digit_blocks():
    sheet = generate_sample_submission_50_mcq(
        answers=EXPECTED,
        sbd="123456",
        exam_code="789",
    )
    result = _read_answers(sheet)
    assert result["answers"] == EXPECTED
    assert result["sbd"] == "123456"
    assert result["exam_code"] == "789"
    assert result["overall_confidence"] >= 0.98
    assert min(result["block_confidence"].values()) >= 0.98


@pytest.mark.parametrize("question_count", [10, 20, 30, 40, 50])
def test_any_supported_question_count_reads_the_first_n_answers(question_count):
    sheet = generate_sample_submission_50_mcq(answers=EXPECTED)
    result = _read_answers(sheet, question_count)
    assert result["answers"] == {
        question: EXPECTED[question] for question in range(1, question_count + 1)
    }


def test_question_count_above_capacity_has_an_explicit_error():
    sheet = generate_sample_submission_50_mcq(answers=EXPECTED)
    success, aligned, message = align_paper(sheet)
    assert success, message
    with pytest.raises(ValueError, match="tối đa 50 câu"):
        extract_all_data(aligned, total_questions=51)


@pytest.mark.parametrize("question_count", [10, 20, 30, 40, 50])
def test_full_grading_pipeline_accepts_any_first_n_count(question_count):
    answer_key = {q: EXPECTED[q] for q in range(1, question_count + 1)}
    sheet = generate_sample_submission_50_mcq(answers=answer_key)
    with tempfile.TemporaryDirectory() as output_dir:
        image_path = os.path.join(output_dir, "student.png")
        assert imwrite_utf8(image_path, sheet)
        submission = process_single_submission(
            image_path,
            answer_key,
            annotated_dir=output_dir,
            total_questions=question_count,
        )
    assert submission.status == "Thành công", submission.error_message
    assert submission.correct_count == question_count
    assert submission.score == 10.0


def test_full_pipeline_crops_and_grades_a_low_resolution_perspective_photo():
    sheet = generate_sample_submission_50_mcq(
        answers=EXPECTED,
        sbd="123456",
        exam_code="789",
    )
    height, width = sheet.shape[:2]
    source = np.float32(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]
    )
    destination = np.float32(
        [[70, 45], [width + 100, 10], [width + 130, height + 180], [20, height + 140]]
    )
    photo = cv2.warpPerspective(
        sheet,
        cv2.getPerspectiveTransform(source, destination),
        (width + 200, height + 200),
        borderValue=(80, 80, 80),
    )
    photo = cv2.resize(photo, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_AREA)
    photo = cv2.GaussianBlur(photo, (3, 3), 0.7)

    with tempfile.TemporaryDirectory() as output_dir:
        image_path = os.path.join(output_dir, "phone_photo.png")
        assert imwrite_utf8(image_path, photo)
        submission = process_single_submission(
            image_path,
            EXPECTED,
            annotated_dir=output_dir,
            total_questions=50,
        )
        flattened = imread_utf8(submission.processed_image_path)

    assert submission.status == "Thành công", submission.error_message
    assert submission.correct_count == 50
    assert submission.score == 10.0
    assert submission.processed_image_path
    assert flattened is not None
    assert flattened.shape[:2] == (STANDARD_HEIGHT, STANDARD_WIDTH)


def test_full_pipeline_flattens_and_scans_a_rotated_low_resolution_import():
    sheet = generate_sample_submission_50_mcq(
        answers=EXPECTED,
        sbd="123456",
        exam_code="789",
    )
    photo = cv2.resize(sheet, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_AREA)
    photo = cv2.rotate(photo, cv2.ROTATE_180)

    with tempfile.TemporaryDirectory() as output_dir:
        image_path = os.path.join(output_dir, "rotated_phone_photo.png")
        assert imwrite_utf8(image_path, photo)
        submission = process_single_submission(
            image_path,
            EXPECTED,
            annotated_dir=output_dir,
            total_questions=50,
        )
        flattened = imread_utf8(submission.processed_image_path)

    assert submission.status == "Thành công", submission.error_message
    assert submission.correct_count == 50
    assert submission.score == 10.0
    assert submission.processed_image_path
    assert flattened is not None
    assert flattened.shape[:2] == (STANDARD_HEIGHT, STANDARD_WIDTH)


@pytest.mark.parametrize(
    "rotation",
    [
        cv2.ROTATE_90_CLOCKWISE,
        cv2.ROTATE_180,
        cv2.ROTATE_90_COUNTERCLOCKWISE,
    ],
)
def test_rotated_photos_are_oriented_from_the_active_layout(rotation):
    sheet = generate_sample_submission_50_mcq(
        answers=EXPECTED,
        sbd="123456",
        exam_code="789",
    )
    result = _read_answers(cv2.rotate(sheet, rotation))
    assert result["answers"] == EXPECTED
    assert result["sbd"] == "123456"
    assert result["exam_code"] == "789"


def test_perspective_low_light_and_shadow_keep_the_answers_readable():
    sheet = generate_sample_submission_50_mcq(
        answers=EXPECTED,
        sbd="123456",
        exam_code="789",
    )
    height, width = sheet.shape[:2]
    source = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])
    destination = np.float32(
        [[130, 100], [width + 20, 20], [width + 90, height + 130], [30, height + 40]]
    )
    transform = cv2.getPerspectiveTransform(source, destination)
    photo = cv2.warpPerspective(
        sheet,
        transform,
        (width + 220, height + 220),
        borderValue=(75, 75, 75),
    )
    illumination = np.linspace(0.62, 0.9, photo.shape[1], dtype=np.float32)[None, :, None]
    photo = np.clip(photo.astype(np.float32) * illumination + 24, 0, 255).astype(np.uint8)
    shadow = np.zeros(photo.shape[:2], dtype=np.uint8)
    cv2.ellipse(
        shadow,
        (photo.shape[1] // 2, photo.shape[0] // 2),
        (photo.shape[1] // 5, photo.shape[0] // 2),
        -12,
        0,
        360,
        80,
        -1,
    )
    photo = cv2.subtract(photo, cv2.merge([shadow, shadow, shadow]))

    result = _read_answers(photo)
    accuracy = sum(result["answers"][q] == EXPECTED[q] for q in EXPECTED) / 50
    assert accuracy >= 0.98
    assert result["sbd"] == "123456"
    assert result["exam_code"] == "789"


def test_low_resolution_photo_is_cropped_flat_and_still_matches_the_layout():
    sheet = generate_sample_submission_50_mcq(
        answers=EXPECTED,
        sbd="123456",
        exam_code="789",
    )
    photo = cv2.resize(sheet, (768, 1024), interpolation=cv2.INTER_AREA)
    photo = cv2.GaussianBlur(photo, (3, 3), 0.7)

    result = _read_answers(photo)

    assert result["answers"] == EXPECTED
    assert result["sbd"] == "123456"
    assert result["exam_code"] == "789"


def test_faint_mark_is_detected_after_warping_a_photo():
    sheet = generate_50_mcq_template()
    success, aligned, message = align_paper(sheet)
    assert success, message
    assert aligned is not None
    y, centers = QUESTION_COORDS[27]
    cv2.circle(aligned, (centers[3], y), 5, (220, 220, 220), -1)

    result = extract_all_data(aligned)

    assert result["layout_source"] == "FormTHPT50"
    assert result["answers"][27] == "D"


def test_two_filled_bubbles_are_still_reported_as_multiple():
    sheet = generate_sample_submission_50_mcq(answers={1: ["A", "B"]})
    success, aligned, message = align_paper(sheet)
    assert success, message
    assert aligned is not None

    result = extract_all_data(aligned)

    assert result["answers"][1] == ["A", "B"]
    assert result["needs_review"]


def test_overlay_center_tracks_a_printed_bubble_shifted_by_local_warp():
    gray = np.full((100, 100), 255, dtype=np.uint8)
    expected_center = (53, 45)
    cv2.circle(gray, expected_center, 16, 120, 2)

    center, radius = _locate_bubble_circle(gray, 50, 50)

    assert abs(center[0] - expected_center[0]) <= 1
    assert abs(center[1] - expected_center[1]) <= 1
    assert 15 <= radius <= 17


def test_unrecognized_image_is_rejected_without_using_fallback_coordinates():
    image = np.full((STANDARD_HEIGHT, STANDARD_WIDTH, 3), 255, dtype=np.uint8)
    result = extract_all_data(image, total_questions=40)
    assert result["layout_source"] == "unrecognized"
    assert result["coords_map"] == {}
    assert all(answer is None for answer in result["answers"].values())


def test_marker_detection_ignores_large_rectangular_clutter():
    image = np.full((1024, 768), 255, dtype=np.uint8)
    expected = np.float32([[98, 109], [626, 105], [647, 919], [73, 909]])
    for x, y in expected:
        cv2.rectangle(image, (int(x - 8), int(y - 8)), (int(x + 8), int(y + 8)), 0, -1)
    for x, y in ((32, 747), (679, 279), (706, 787), (63, 985)):
        cv2.rectangle(image, (x - 20, y - 15), (x + 20, y + 15), 0, -1)

    marker_quad = find_fiducial_markers(image)

    assert marker_quad is not None
    np.testing.assert_allclose(marker_quad, expected, atol=1)


def test_marker_selection_ignores_background_square_that_expands_the_quad():
    expected = np.float32(
        [[242.5, 272.5], [1562.5, 261.5], [1617.0, 2298.5], [181.0, 2271.5]]
    )
    candidates = [
        {
            "center": tuple(point),
            "area": 800.0,
            "bbox": (int(point[0] - 15), int(point[1] - 15), 30, 30),
        }
        for point in expected
    ]
    candidates.append(
        {
            "center": (43.0, 336.0),
            "area": 431.0,
            "bbox": (28, 320, 30, 32),
        }
    )

    marker_quad = _select_marker_quad(candidates, 1920, 2560)

    assert marker_quad is not None
    np.testing.assert_allclose(marker_quad, expected, atol=1)


def test_clean_processing_stays_under_two_seconds():
    sheet = generate_sample_submission_50_mcq(answers=EXPECTED)
    started = time.perf_counter()
    result = _read_answers(sheet)
    assert result["answers"] == EXPECTED
    assert time.perf_counter() - started < 2.0
