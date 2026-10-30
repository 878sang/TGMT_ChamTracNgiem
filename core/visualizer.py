"""
Module: visualizer.py
Vẽ trực quan kết quả chấm trắc nghiệm 50 câu lên ảnh bài làm đã nắn phẳng.
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

from core.omr_extractor import get_question_coords

COLOR_CORRECT = (0, 180, 0)      # Xanh lá
COLOR_WRONG = (0, 0, 220)        # Đỏ
COLOR_KEY = (0, 200, 240)        # Vàng (đáp án chuẩn)
COLOR_BLANK = (0, 140, 255)      # Cam
COLOR_BANNER_BG = (255, 255, 255)
COLOR_BANNER_BORDER = (0, 0, 160)

OPT_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3}


def draw_grading_overlay(
    aligned_img: np.ndarray,
    student_answers: Dict[int, Any],
    answer_key: Dict[int, str],
    score_info: Dict[str, Any],
    student_id: str = "",
    coords_map: Optional[Dict[int, Tuple[int, List[int]]]] = None
) -> np.ndarray:
    """Vẽ lớp phủ kết quả chấm điểm 50 câu lên ảnh bài làm 1200x1700"""
    canvas = aligned_img.copy()

    # 1. Vẽ Banner tổng kết điểm ở góc trên
    cv2.rectangle(canvas, (70, 15), (1130, 80), COLOR_BANNER_BG, -1)
    cv2.rectangle(canvas, (70, 15), (1130, 80), COLOR_BANNER_BORDER, 2)

    score = score_info.get("score", 0.0)
    correct = score_info.get("correct_count", 0)
    wrong = score_info.get("wrong_count", 0)
    blank = score_info.get("blank_count", 0)
    rank = score_info.get("rank", "")

    title_text = f"DIEM: {score:.2f} / 10.0"
    if student_id:
        title_text = f"[{student_id}]  " + title_text

    cv2.putText(canvas, title_text, (90, 58), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 0, 200), 2)
    stat_text = f"Dung: {correct}/50  |  Sai: {wrong}  |  Trong: {blank}  |  Loai: {rank}"
    cv2.putText(canvas, stat_text, (520, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 100, 0), 2)

    # 2. Vẽ khoanh tròn từng câu trong số 50 câu
    details = score_info.get("details", {})
    radius = 15

    for q_num in range(1, 51):
        if coords_map and q_num in coords_map:
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
            cv2.circle(canvas, (cx_c, cy), radius, COLOR_CORRECT, 3)
            cv2.line(canvas, (cx_c - 5, cy), (cx_c - 1, cy + 5), COLOR_CORRECT, 2)
            cv2.line(canvas, (cx_c - 1, cy + 5), (cx_c + 6, cy - 5), COLOR_CORRECT, 2)

        # Bỏ trống
        elif st_ans is None or st_ans == "":
            if key_ans in OPT_MAP:
                cx_k = cx_list[OPT_MAP[key_ans]]
                cv2.circle(canvas, (cx_k, cy), radius, COLOR_KEY, 3)

        # Tô nhiều ô
        elif isinstance(st_ans, (list, tuple)):
            for a_item in st_ans:
                if a_item in OPT_MAP:
                    cx_w = cx_list[OPT_MAP[a_item]]
                    cv2.circle(canvas, (cx_w, cy), radius, COLOR_WRONG, 3)
                    cv2.line(canvas, (cx_w - 6, cy - 6), (cx_w + 6, cy + 6), COLOR_WRONG, 2)
                    cv2.line(canvas, (cx_w - 6, cy + 6), (cx_w + 6, cy - 6), COLOR_WRONG, 2)
            if key_ans in OPT_MAP:
                cx_k = cx_list[OPT_MAP[key_ans]]
                cv2.circle(canvas, (cx_k, cy), radius, COLOR_KEY, 3)

        # Tô sai
        else:
            wrong_opt = str(st_ans).strip().upper()
            if wrong_opt in OPT_MAP:
                cx_w = cx_list[OPT_MAP[wrong_opt]]
                cv2.circle(canvas, (cx_w, cy), radius, COLOR_WRONG, 3)
                cv2.line(canvas, (cx_w - 6, cy - 6), (cx_w + 6, cy + 6), COLOR_WRONG, 2)
                cv2.line(canvas, (cx_w - 6, cy + 6), (cx_w + 6, cy - 6), COLOR_WRONG, 2)
            if key_ans in OPT_MAP:
                cx_k = cx_list[OPT_MAP[key_ans]]
                cv2.circle(canvas, (cx_k, cy), radius, COLOR_KEY, 3)

    return canvas
