"""
Module: visualizer.py
Phụ trách: Thành viên 2 (Computer Vision 2)
Chức năng:
  - Vẽ trực tiếp kết quả chấm lên ảnh bài làm đã nắn phẳng
  - Ô tô đúng: Khoanh viền XANH LÁ
  - Ô tô sai: Khoanh viền ĐỎ
  - Đáp án đúng bị bỏ lỡ: Khoanh viền VÀNG
  - Đóng dấu bảng tổng kết điểm to, rõ ở góc trên bài làm để trả bài cho học sinh
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import cv2
import numpy as np
from typing import Dict, Any
from core.models import ExamMode


COLOR_CORRECT = (0, 180, 0)      # Xanh lá
COLOR_WRONG = (0, 0, 220)        # Đỏ
COLOR_KEY = (0, 200, 240)        # Vàng (đáp án đúng)
COLOR_TEXT = (20, 20, 20)


def draw_grading_overlay(
    aligned_img: np.ndarray, 
    mode: str, 
    extracted_data: Dict[str, Any], 
    answer_key: Dict[str, Any],
    score_info: Dict[str, Any]
) -> np.ndarray:
    """
    Vẽ lớp phủ kết quả chấm điểm lên ảnh bài làm 1200x1700
    """
    canvas = aligned_img.copy()

    # -------------------------------------------------------------
    # 1. Đóng dấu Banner điểm số góc trên
    # -------------------------------------------------------------
    cv2.rectangle(canvas, (80, 15), (1120, 75), (255, 255, 255), -1)
    cv2.rectangle(canvas, (80, 15), (1120, 75), (0, 0, 160), 2)

    total_score = score_info.get("total_score") if mode == ExamMode.THPT_2025 else score_info.get("score", 0.0)
    score_text = f"DIEM: {total_score:.2f} / 10.0"
    cv2.putText(canvas, score_text, (100, 58), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 200), 3)

    if mode == ExamMode.FULL_MCQ:
        stat_text = f"Dung: {score_info.get('correct_count', 0)} | Sai: {score_info.get('wrong_count', 0)} | Trong: {score_info.get('blank_count', 0)}"
        cv2.putText(canvas, stat_text, (520, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 0), 2)
    else:
        p1 = score_info.get("score_part1", 0.0)
        p2 = score_info.get("score_part2", 0.0)
        p3 = score_info.get("score_part3", 0.0)
        stat_text = f"P1 (TN): {p1:.2f}d | P2 (D/S): {p2:.2f}d | P3 (So): {p3:.2f}d"
        cv2.putText(canvas, stat_text, (480, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 100, 0), 2)

    opt_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

    # -------------------------------------------------------------
    # 2. Vẽ khoanh tròn theo chế độ
    # -------------------------------------------------------------
    if mode == ExamMode.FULL_MCQ:
        st_answers = extracted_data.get("answers", {})
        details = score_info.get("details", {})

        for q_num, det in details.items():
            st_ans = det.get("student")
            key_ans = det.get("key")
            is_c = det.get("is_correct", False)

            if q_num <= 20:
                base_x = 120
                q_row = q_num - 1
            else:
                base_x = 640
                q_row = q_num - 21
            cy = 600 + q_row * 48

            # Nếu đúng: khoanh xanh ô học sinh tô
            if is_c and st_ans in opt_map:
                cx = base_x + 125 + opt_map[st_ans] * 75
                cv2.circle(canvas, (cx, cy), 16, COLOR_CORRECT, 3)

            # Nếu sai: khoanh đỏ ô học sinh tô, khoanh vàng ô key
            elif not is_c:
                if st_ans in opt_map:
                    cx_st = base_x + 125 + opt_map[st_ans] * 75
                    cv2.circle(canvas, (cx_st, cy), 16, COLOR_WRONG, 3)
                    # Gạch chéo nhẹ
                    cv2.line(canvas, (cx_st - 10, cy - 10), (cx_st + 10, cy + 10), COLOR_WRONG, 2)
                if key_ans in opt_map:
                    cx_key = base_x + 125 + opt_map[key_ans] * 75
                    cv2.circle(canvas, (cx_key, cy), 17, COLOR_KEY, 3)

    elif mode == ExamMode.THPT_2025:
        # 1. Vẽ Phần I
        p1_details = score_info.get("details_p1", {})
        for q_num, det in p1_details.items():
            st_ans = det.get("student")
            key_ans = det.get("key")
            is_c = det.get("is_correct", False)

            c_i = 0 if q_num <= 6 else 1
            bx = 140 if c_i == 0 else 640
            q_pos = (q_num - 1) if c_i == 0 else (q_num - 7)
            cy = 550 + q_pos * 40

            if is_c and st_ans in opt_map:
                cx = bx + 130 + opt_map[st_ans] * 70
                cv2.circle(canvas, (cx, cy), 15, COLOR_CORRECT, 3)
            elif not is_c:
                if st_ans in opt_map:
                    cx_st = bx + 130 + opt_map[st_ans] * 70
                    cv2.circle(canvas, (cx_st, cy), 15, COLOR_WRONG, 3)
                if key_ans in opt_map:
                    cx_key = bx + 130 + opt_map[key_ans] * 70
                    cv2.circle(canvas, (cx_key, cy), 16, COLOR_KEY, 3)

        # 2. Vẽ Phần II (Đúng / Sai)
        p2_details = score_info.get("details_p2", {})
        for q_num, q_det in p2_details.items():
            bx = 130 if (q_num % 2 != 0) else 640
            by = 880 if (q_num <= 2) else 1030
            sub_dets = q_det.get("sub_items", {})
            for s_idx, sub in enumerate(['a', 'b', 'c', 'd']):
                s_det = sub_dets.get(sub, {})
                st_ans = s_det.get("student")
                key_ans = s_det.get("key")
                is_sub_c = s_det.get("is_correct", False)
                sy = by + 10 + s_idx * 30

                if is_sub_c:
                    cx = bx + 180 if st_ans == "Đ" else bx + 230
                    cv2.circle(canvas, (cx, sy), 14, COLOR_CORRECT, 2)
                else:
                    if st_ans:
                        cx_st = bx + 180 if st_ans == "Đ" else bx + 230
                        cv2.circle(canvas, (cx_st, sy), 14, COLOR_WRONG, 2)
                    if key_ans:
                        cx_k = bx + 180 if key_ans == "Đ" else bx + 230
                        cv2.circle(canvas, (cx_k, sy), 15, COLOR_KEY, 2)

        # 3. Vẽ Phần III (Trả lời ngắn)
        p3_details = score_info.get("details_p3", {})
        for q_num, det in p3_details.items():
            q_idx = int(q_num) - 1
            col_pos = q_idx % 3
            row_pos = q_idx // 3
            bx = 120 + col_pos * 340
            by = 1260 + row_pos * 160

            st_val = det.get("student", "")
            key_val = det.get("key", "")
            is_c = det.get("is_correct", False)

            tag_text = f"Dung: {st_val}" if is_c else f"Sai: {st_val or 'Trong'} (Key: {key_val})"
            color = COLOR_CORRECT if is_c else COLOR_WRONG
            # Khung viền kết quả nhỏ phía dưới bảng số
            cv2.rectangle(canvas, (bx + 8, by + 140), (bx + 260, by + 158), (255, 255, 255), -1)
            cv2.rectangle(canvas, (bx + 8, by + 140), (bx + 260, by + 158), color, 1)
            cv2.putText(canvas, tag_text, (bx + 12, by + 154), cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1)

    return canvas
