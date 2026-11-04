"""OMR extraction for the active THPT50 layout."""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.layouts import load_layout

ACTIVE_LAYOUT = load_layout()
OPTIONS = ("A", "B", "C", "D")
MARKED_BUBBLE_CONTRAST = 12.0


def _layout_question_coords() -> Dict[int, Tuple[int, List[int]]]:
    coords = {}
    for block in ACTIVE_LAYOUT["blocks"]:
        for row in block["questions"]:
            coords[int(row["question"])] = (
                int(round(row["y"])),
                [
                    int(round(row["options"][option]["x"]))
                    for option in block["option_order"]
                ],
            )
    return coords


QUESTION_COORDS = _layout_question_coords()


def _get_bubble_ink_contrast(
    gray_img: np.ndarray,
    cx: int,
    cy: int,
    radius: int,
) -> float:
    """Measure marked ink against the local paper around one printed bubble."""
    center_radius = max(3, int(round(radius * 0.5)))
    outer_radius = radius + 8
    h, w = gray_img.shape[:2]
    if (
        cx - outer_radius < 0
        or cy - outer_radius < 0
        or cx + outer_radius >= w
        or cy + outer_radius >= h
    ):
        return 0.0
    roi = gray_img[
        cy - outer_radius:cy + outer_radius + 1,
        cx - outer_radius:cx + outer_radius + 1,
    ]
    yy, xx = np.ogrid[-outer_radius:outer_radius + 1, -outer_radius:outer_radius + 1]
    distance_squared = xx * xx + yy * yy
    center = roi[distance_squared <= center_radius * center_radius]
    local_paper = roi[
        (distance_squared >= (radius + 4) ** 2)
        & (distance_squared <= outer_radius ** 2)
    ]
    return max(0.0, float(np.mean(local_paper)) - float(np.mean(center)))


def _layout_bubble_confidence(gray_img: np.ndarray) -> Tuple[float, Dict[str, float]]:
    h, w = gray_img.shape[:2]
    block_scores: Dict[str, float] = {}
    for block in ACTIVE_LAYOUT["blocks"]:
        radius = max(4, int(round(block["radius"])))
        outer_radius = radius + 8
        yy, xx = np.ogrid[-outer_radius:outer_radius + 1, -outer_radius:outer_radius + 1]
        distance_squared = xx * xx + yy * yy
        ring_mask = (
            (distance_squared >= (radius - 1) ** 2)
            & (distance_squared <= (radius + 2) ** 2)
        )
        outside_mask = (
            (distance_squared >= (radius + 4) ** 2)
            & (distance_squared <= outer_radius ** 2)
        )
        matched = 0
        total = 0
        for row in block["questions"]:
            for point in row["options"].values():
                cx, cy = int(round(point["x"])), int(round(point["y"]))
                if (
                    cx - outer_radius < 0
                    or cy - outer_radius < 0
                    or cx + outer_radius >= w
                    or cy + outer_radius >= h
                ):
                    continue
                roi = gray_img[
                    cy - outer_radius:cy + outer_radius + 1,
                    cx - outer_radius:cx + outer_radius + 1,
                ]
                ring_mean = float(np.mean(roi[ring_mask]))
                outside_mean = float(np.mean(roi[outside_mask]))
                matched += outside_mean - ring_mean >= 15
                total += 1
        block_scores[block["id"]] = matched / total if total else 0.0
    overall = sum(block_scores.values()) / len(block_scores) if block_scores else 0.0
    return overall, block_scores


def _layout_marker_confidence(gray_img: np.ndarray) -> float:
    """Check the distributed black registration squares after perspective alignment."""
    h, w = gray_img.shape[:2]
    matched = 0
    total = 0
    for marker in ACTIVE_LAYOUT["markers"]:
        radius = max(3, int(round(marker["size"] * 0.3)))
        outer_radius = max(radius + 2, int(round(marker["size"] * 0.6)))
        cx, cy = int(round(marker["x"])), int(round(marker["y"]))
        if (
            cx - outer_radius < 0
            or cy - outer_radius < 0
            or cx + outer_radius >= w
            or cy + outer_radius >= h
        ):
            continue
        roi = gray_img[
            cy - outer_radius:cy + outer_radius + 1,
            cx - outer_radius:cx + outer_radius + 1,
        ]
        yy, xx = np.ogrid[-outer_radius:outer_radius + 1, -outer_radius:outer_radius + 1]
        distance_squared = xx * xx + yy * yy
        center = roi[distance_squared <= radius * radius]
        surrounding_paper = roi[
            (distance_squared >= (radius + 2) ** 2)
            & (distance_squared <= outer_radius * outer_radius)
        ]
        contrast = float(np.mean(surrounding_paper) - np.mean(center))
        matched += float(np.mean(center) < 160 and contrast >= 12)
        total += 1
    return matched / total if total else 0.0


def _read_digit_block(
    gray_img: np.ndarray,
    block: Dict[str, Any],
) -> Tuple[str, bool, float]:
    digits: List[str] = []
    confidences: List[float] = []
    is_valid = True
    for column in block["columns_data"]:
        contrasts = [
            _get_bubble_ink_contrast(
                gray_img,
                int(round(bubble["x"])),
                int(round(bubble["y"])),
                radius=int(round(block["radius"])),
            )
            for bubble in column["digits"]
        ]
        ordered = sorted(contrasts, reverse=True)
        confidence = (ordered[0] - ordered[1]) / 255.0
        confidences.append(confidence)
        if ordered[0] < 18:
            digits.append("?")
            is_valid = False
        elif ordered[1] >= 18 and ordered[0] - ordered[1] < 18:
            digits.append("?")
            is_valid = False
        else:
            digits.append(str(int(np.argmax(contrasts))))
    return "".join(digits), is_valid, min(confidences, default=0.0)


def extract_all_data(
    aligned_bgr: np.ndarray,
    total_questions: int = 50,
    known_coords_map: Optional[Dict[int, Tuple[int, List[int]]]] = None,
    known_layout_source: str = "",
) -> Dict[str, Any]:
    """Read answers and identification digits using the active layout only."""
    capacity = int(ACTIVE_LAYOUT["capacity"])
    if not 1 <= total_questions <= capacity:
        raise ValueError(
            f"Phiếu này chỉ có tối đa {capacity} câu; số câu phải nằm trong khoảng 1 đến {capacity}."
        )

    gray = (
        cv2.cvtColor(aligned_bgr, cv2.COLOR_BGR2GRAY)
        if len(aligned_bgr.shape) == 3
        else aligned_bgr
    )
    bubble_confidence, block_confidence = _layout_bubble_confidence(gray)
    marker_confidence = _layout_marker_confidence(gray)
    layout_confidence = max(bubble_confidence, marker_confidence)
    if layout_confidence >= 0.60:
        layout_source = known_layout_source or ACTIVE_LAYOUT["name"]
        coords_map = (
            known_coords_map if known_coords_map is not None else QUESTION_COORDS
        )
    else:
        layout_source = "unrecognized"
        coords_map = {}

    coords_map = {
        question: coords_map[question]
        for question in range(1, total_questions + 1)
        if question in coords_map
    }
    answers: Dict[int, Any] = {}
    answer_confidence: Dict[int, float] = {}
    warnings: List[str] = []
    needs_review = layout_source == "unrecognized"
    if needs_review:
        block_confidence = {block["id"]: 0.0 for block in ACTIVE_LAYOUT["blocks"]}
        warnings.append(
            "Ảnh không khớp lưới đáp án FormTHPT50; không dùng tọa độ dự phòng để tránh chấm sai."
        )

    radius = int(round(ACTIVE_LAYOUT["blocks"][0]["radius"]))
    for question in range(1, total_questions + 1):
        if question not in coords_map:
            answers[question] = None
            answer_confidence[question] = 0.0
            continue
        cy, centers = coords_map[question]
        scores = [
            _get_bubble_ink_contrast(gray, cx, cy, radius)
            for cx in centers
        ]
        ordered = sorted(scores, reverse=True)
        strongest, second = ordered[:2]
        answer_confidence[question] = (
            (strongest - second) / max(strongest, 1.0)
        )
        marked = [
            OPTIONS[index]
            for index, score in enumerate(scores)
            if score >= 18 and score >= strongest * 0.35
        ]
        if len(marked) >= 2:
            answers[question] = marked
            needs_review = True
            warnings.append(f"Câu {question}: Tô nhiều đáp án ({', '.join(marked)})")
        elif strongest >= MARKED_BUBBLE_CONTRAST:
            answers[question] = OPTIONS[int(np.argmax(scores))]
            if second >= 12:
                needs_review = True
                warnings.append(f"Câu {question}: Nghi vấn tẩy lem nhem")
        else:
            answers[question] = None

    if layout_source == "unrecognized":
        sbd, is_valid_sbd = "", False
        exam_code, is_valid_code = "", False
    else:
        sbd, is_valid_sbd, _ = _read_digit_block(
            gray, ACTIVE_LAYOUT["id_blocks"]["student_id"]
        )
        exam_code, is_valid_code, _ = _read_digit_block(
            gray, ACTIVE_LAYOUT["id_blocks"]["exam_code"]
        )
    if sbd and ("?" in sbd or not is_valid_sbd):
        warnings.insert(0, f"SBD chưa rõ: '{sbd}'")
        needs_review = True
    if exam_code and ("?" in exam_code or not is_valid_code):
        warnings.insert(0, f"Mã đề chưa rõ: '{exam_code}'")
        needs_review = True
    if layout_source != "unrecognized" and (
        marker_confidence < 0.80
        and bubble_confidence < 0.80
    ):
        warnings.insert(
            0,
            f"Độ khớp lưới FormTHPT50 thấp "
            f"(ô đáp án {bubble_confidence:.0%}, marker {marker_confidence:.0%}).",
        )
        needs_review = True

    return {
        "num_questions": total_questions,
        "coords_map": coords_map,
        "layout_source": layout_source,
        "layout_name": ACTIVE_LAYOUT["name"],
        "overall_confidence": layout_confidence,
        "marker_confidence": marker_confidence,
        "block_confidence": block_confidence,
        "answer_confidence": answer_confidence,
        "sbd": sbd,
        "is_valid_sbd": is_valid_sbd,
        "exam_code": exam_code,
        "is_valid_code": is_valid_code,
        "answers": answers,
        "needs_review": needs_review,
        "warnings": warnings,
        "warning_message": "; ".join(warnings[:3]) if warnings else "",
    }


def get_question_coords(q_num: int) -> Tuple[int, List[int]]:
    """Return coordinates for one question in the active THPT50 layout."""
    if q_num not in QUESTION_COORDS:
        raise ValueError(f"Question must be between 1 and {ACTIVE_LAYOUT['capacity']}.")
    return QUESTION_COORDS[q_num]
