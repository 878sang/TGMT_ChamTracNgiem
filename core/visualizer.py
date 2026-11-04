"""
Module: visualizer.py
Vẽ kết quả chấm lên ảnh FormTHPT50 đã nắn phẳng.
- Câu đúng: Khoanh viền XANH LÁ kèm tick
- Câu sai: Khoanh viền ĐỎ kèm gạch chéo
- Câu bỏ trống: Khoanh viền VÀNG vào đáp án chuẩn của đề
- Tô nhiều ô: Khoanh viền ĐỎ tất cả các ô đã chọn và khoanh VÀNG vào đáp án chuẩn
- Banner điểm số to rõ ràng trên đầu bài làm
"""

import os
import sys
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.omr_extractor import ACTIVE_LAYOUT, get_question_coords

COLOR_CORRECT = (0, 180, 0)      # Xanh lá
COLOR_WRONG = (0, 0, 220)        # Đỏ
COLOR_KEY = (0, 200, 240)        # Vàng (đáp án chuẩn)
COLOR_BLANK = (0, 140, 255)      # Cam
COLOR_BANNER_BG = (255, 255, 255)
COLOR_BANNER_BORDER = (0, 0, 160)

OPT_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3}


def _locate_bubble_circle(
    gray_img: np.ndarray,
    cx: int,
    cy: int,
) -> Tuple[Tuple[int, int], int]:
    """Refine a template bubble center to the printed ring visible in the image."""
    search_radius = 24
    height, width = gray_img.shape[:2]
    if (
        cx - search_radius < 0
        or cy - search_radius < 0
        or cx + search_radius >= width
        or cy + search_radius >= height
    ):
        return (cx, cy), int(round(ACTIVE_LAYOUT["blocks"][0]["radius"]))

    roi = gray_img[
        cy - search_radius:cy + search_radius + 1,
        cx - search_radius:cx + search_radius + 1,
    ]
    circles = cv2.HoughCircles(
        cv2.medianBlur(roi, 5),
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=70,
        param2=14,
        minRadius=10,
        maxRadius=20,
    )
    if circles is None:
        return (cx, cy), int(round(ACTIVE_LAYOUT["blocks"][0]["radius"]))

    candidates = [
        circle
        for circle in circles[0]
        if np.hypot(
            circle[0] - search_radius,
            circle[1] - search_radius,
        ) <= 18
    ]
    if not candidates:
        return (cx, cy), int(round(ACTIVE_LAYOUT["blocks"][0]["radius"]))

    circle = min(
        candidates,
        key=lambda item: np.hypot(
            item[0] - search_radius,
            item[1] - search_radius,
        ),
    )
    center = (
        int(round(cx + circle[0] - search_radius)),
        int(round(cy + circle[1] - search_radius)),
    )
    return center, int(round(circle[2]))


def remove_grading_overlay(image: np.ndarray) -> np.ndarray:
    """Remove saturated grading colors before a previously annotated sheet is rescanned."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    overlay_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    color_ranges = (
        ((0, 100, 60), (10, 255, 255)),
        ((170, 100, 60), (179, 255, 255)),
        ((15, 80, 70), (40, 255, 255)),
        ((45, 80, 60), (85, 255, 255)),
    )
    for lower, upper in color_ranges:
        overlay_mask = cv2.bitwise_or(
            overlay_mask,
            cv2.inRange(hsv, np.array(lower, dtype=np.uint8), np.array(upper, dtype=np.uint8)),
        )

    if cv2.countNonZero(overlay_mask) == 0:
        return image.copy()

    overlay_mask = cv2.dilate(
        overlay_mask,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
    )
    return cv2.inpaint(image, overlay_mask, 4, cv2.INPAINT_TELEA)


def draw_grading_overlay(
    aligned_img: np.ndarray,
    student_answers: Dict[int, Any],
    answer_key: Dict[int, str],
    score_info: Dict[str, Any],
    student_id: str = "",
    coords_map: Optional[Dict[int, Tuple[int, List[int]]]] = None
) -> np.ndarray:
    """Draw grading results on the aligned THPT50 canvas."""
    canvas = aligned_img.copy()
    height, width = canvas.shape[:2]
    margin_x = int(round(width * 0.06))
    banner_height = int(round(height * 0.06))

    # 1. Vẽ Banner tổng kết điểm ở góc trên
    cv2.rectangle(canvas, (margin_x, 0), (width - margin_x, banner_height), COLOR_BANNER_BG, -1)
    cv2.rectangle(canvas, (margin_x, 0), (width - margin_x, banner_height), COLOR_BANNER_BORDER, 2)

    score = score_info.get("score", 0.0)
    correct = score_info.get("correct_count", 0)
    wrong = score_info.get("wrong_count", 0)
    blank = score_info.get("blank_count", 0)
    rank = score_info.get("rank", "")

    title_text = f"DIEM: {score:.2f} / 10.0"
    total_questions = score_info.get("total_questions", len(answer_key))
    stat_text = f"Dung: {correct}/{total_questions}  |  Sai: {wrong}  |  Trong: {blank}  |  Loai: {rank}"
    title_font = cv2.FONT_HERSHEY_DUPLEX
    stat_font = cv2.FONT_HERSHEY_SIMPLEX
    title_scale = width / 1200 * 0.85
    title_thickness = max(2, int(round(width / 1200 * 2)))
    cv2.putText(
        canvas, title_text, (margin_x + 20, int(banner_height * 0.50)),
        title_font, title_scale, (0, 0, 200), title_thickness
    )
    stat_scale = width / 1200 * 0.65
    stat_width = cv2.getTextSize(stat_text, stat_font, stat_scale, 2)[0][0]
    if student_id:
        identity_text = f"Ma hoc sinh: {student_id}"
        identity_scale = width / 1200 * 0.7
        identity_width = cv2.getTextSize(identity_text, stat_font, identity_scale, 2)[0][0]
        available_width = width - 2 * margin_x - 40
        gap = 24
        if stat_width + identity_width + gap > available_width:
            scale_factor = (available_width - gap) / (stat_width + identity_width)
            stat_scale *= scale_factor
            identity_scale *= scale_factor
            stat_width = cv2.getTextSize(stat_text, stat_font, stat_scale, 2)[0][0]
            identity_width = cv2.getTextSize(identity_text, stat_font, identity_scale, 2)[0][0]
        identity_x = width - margin_x - 20 - identity_width
        cv2.putText(
            canvas, identity_text, (identity_x, int(banner_height * 0.84)),
            stat_font, identity_scale, (70, 70, 70), 2
        )
    cv2.putText(
        canvas, stat_text, (margin_x + 20, int(banner_height * 0.84)),
        stat_font, stat_scale, (0, 100, 0), 2
    )

    # 2. Vẽ khoanh tròn các câu đã chấm
    details = score_info.get("details", {})
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY) if canvas.ndim == 3 else canvas
    circle_cache: Dict[Tuple[int, int], Tuple[Tuple[int, int], int]] = {}

    def locate(cx: int, cy: int) -> Tuple[Tuple[int, int], int]:
        key = (cx, cy)
        if key not in circle_cache:
            circle_cache[key] = _locate_bubble_circle(gray, cx, cy)
        return circle_cache[key]

    for q_num in range(1, total_questions + 1):
        if coords_map is not None:
            if q_num not in coords_map:
                continue
            cy, cx_list = coords_map[q_num]
        else:
            cy, cx_list = get_question_coords(q_num)

        det = details.get(q_num, {})
        st_ans = student_answers.get(q_num)
        key_ans = str(answer_key.get(q_num, "")).strip().upper()
        is_correct = det.get("is_correct", False)

        # Đúng
        if is_correct and key_ans in OPT_MAP:
            cx_c = cx_list[OPT_MAP[key_ans]]
            center, radius = locate(cx_c, cy)
            cv2.circle(canvas, center, radius, COLOR_CORRECT, 3)
            cv2.line(
                canvas,
                (center[0] - 5, center[1]),
                (center[0] - 1, center[1] + 5),
                COLOR_CORRECT,
                2,
            )
            cv2.line(
                canvas,
                (center[0] - 1, center[1] + 5),
                (center[0] + 6, center[1] - 5),
                COLOR_CORRECT,
                2,
            )

        # Bỏ trống
        elif st_ans is None or st_ans == "":
            if key_ans in OPT_MAP:
                cx_k = cx_list[OPT_MAP[key_ans]]
                center, radius = locate(cx_k, cy)
                cv2.circle(canvas, center, radius, COLOR_KEY, 3)

        # Tô nhiều ô
        elif isinstance(st_ans, (list, tuple)):
            for a_item in st_ans:
                if a_item in OPT_MAP:
                    cx_w = cx_list[OPT_MAP[a_item]]
                    center, radius = locate(cx_w, cy)
                    cv2.circle(canvas, center, radius, COLOR_WRONG, 3)
                    cv2.line(
                        canvas,
                        (center[0] - 6, center[1] - 6),
                        (center[0] + 6, center[1] + 6),
                        COLOR_WRONG,
                        2,
                    )
                    cv2.line(
                        canvas,
                        (center[0] - 6, center[1] + 6),
                        (center[0] + 6, center[1] - 6),
                        COLOR_WRONG,
                        2,
                    )
            if key_ans in OPT_MAP:
                cx_k = cx_list[OPT_MAP[key_ans]]
                center, radius = locate(cx_k, cy)
                cv2.circle(canvas, center, radius, COLOR_KEY, 3)

        # Tô sai
        else:
            wrong_opt = str(st_ans).strip().upper()
            if wrong_opt in OPT_MAP:
                cx_w = cx_list[OPT_MAP[wrong_opt]]
                center, radius = locate(cx_w, cy)
                cv2.circle(canvas, center, radius, COLOR_WRONG, 3)
                cv2.line(
                    canvas,
                    (center[0] - 6, center[1] - 6),
                    (center[0] + 6, center[1] + 6),
                    COLOR_WRONG,
                    2,
                )
                cv2.line(
                    canvas,
                    (center[0] - 6, center[1] + 6),
                    (center[0] + 6, center[1] - 6),
                    COLOR_WRONG,
                    2,
                )
            if key_ans in OPT_MAP:
                cx_k = cx_list[OPT_MAP[key_ans]]
                center, radius = locate(cx_k, cy)
                cv2.circle(canvas, center, radius, COLOR_KEY, 3)

    return canvas
