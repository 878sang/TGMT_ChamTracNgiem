"""
Module: omr_extractor.py
Phụ trách: Thành viên 2 (Computer Vision 2)
Chức năng:
  - Bóc tách SBD (6 số) và Mã đề thi (3 số)
  - Nhận diện đáp án Chế độ 1: Full trắc nghiệm 4 lựa chọn (A, B, C, D)
  - Nhận diện đáp án Chế độ 2: Đề chuẩn THPT 2025 (Phần I, II, III)
  - Thuật toán so sánh tương đối (Relative Scoring) chống sai số do ánh sáng/tẩy chì
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import cv2
import numpy as np
from typing import Dict, Tuple, Any, Optional, List
from core.models import ExamMode


def get_bubble_density(gray_img: np.ndarray, cx: int, cy: int, radius: int = 12) -> float:
    """
    Tính mật độ pixel được tô (đen) trong vùng tròn tâm (cx, cy) bán kính radius.
    Trả về tỷ lệ từ 0.0 (hoàn toàn trắng) đến 1.0 (hoàn toàn đen).
    """
    h, w = gray_img.shape[:2]
    x1, x2 = max(0, int(cx - radius)), min(w, int(cx + radius + 1))
    y1, y2 = max(0, int(cy - radius)), min(h, int(cy + radius + 1))
    
    roi = gray_img[y1:y2, x1:x2]
    if roi.size == 0:
        return 0.0

    # Nhị phân hóa cục bộ
    _, thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Tạo circular mask
    mask = np.zeros(roi.shape, dtype=np.uint8)
    cv2.circle(mask, (int(cx - x1), int(cy - y1)), int(radius * 0.85), 255, -1)

    masked_pixels = cv2.bitwise_and(thresh, thresh, mask=mask)
    total_mask_pixels = cv2.countNonZero(mask)
    if total_mask_pixels == 0:
        return 0.0

    filled_pixels = cv2.countNonZero(masked_pixels)
    return float(filled_pixels) / float(total_mask_pixels)


def extract_sbd(gray_img: np.ndarray) -> Tuple[str, bool, float]:
    """
    Quét khối Số Báo Danh (6 cột x 10 hàng 0-9)
    Tâm các ô: cx = 160 + col * 65, cy = 200 + row * 25
    Trả về: (sbd_string, is_valid: bool, min_confidence: float)
    Nếu cột không được tô hoặc tô không rõ ràng, không tự gán số mặc định ('0')
    mà đánh dấu '?' để cảnh báo người dùng xác nhận.
    """
    sbd_digits = []
    min_confidence = 1.0
    is_valid = True

    for col in range(6):
        cx = 160 + col * 65
        densities = [get_bubble_density(gray_img, cx, 200 + r * 25, radius=8) for r in range(10)]
        max_idx = int(np.argmax(densities))
        max_val = densities[max_idx]

        sorted_d = sorted(densities, reverse=True)
        conf = sorted_d[0] - sorted_d[1]
        min_confidence = min(min_confidence, conf)

        if max_val < 0.22:
            # Cột bị bỏ trống hoặc tô quá mờ
            sbd_digits.append("?")
            is_valid = False
        elif sorted_d[1] >= 0.22 and conf < 0.12:
            # Nghi vấn tô 2 ô cùng 1 cột hoặc tẩy lem
            sbd_digits.append("?")
            is_valid = False
        else:
            sbd_digits.append(str(max_idx))

    return "".join(sbd_digits), is_valid, min_confidence


def extract_exam_code(gray_img: np.ndarray) -> Tuple[str, bool, float]:
    """
    Quét khối Mã Đề Thi (3 cột x 10 hàng 0-9)
    Tâm các ô: cx = 680 + col * 65, cy = 200 + row * 25
    Trả về: (code_string, is_valid: bool, min_confidence: float)
    Nếu không đọc được hoặc nghi vấn, không tự gán số mặc định ('100')
    mà trả về '?' và is_valid = False để cảnh báo người dùng xác nhận.
    """
    code_digits = []
    min_confidence = 1.0
    is_valid = True

    for col in range(3):
        cx = 680 + col * 65
        densities = [get_bubble_density(gray_img, cx, 200 + r * 25, radius=8) for r in range(10)]
        max_idx = int(np.argmax(densities))
        max_val = densities[max_idx]

        sorted_d = sorted(densities, reverse=True)
        conf = sorted_d[0] - sorted_d[1]
        min_confidence = min(min_confidence, conf)

        if max_val < 0.22:
            code_digits.append("?")
            is_valid = False
        elif sorted_d[1] >= 0.22 and conf < 0.12:
            code_digits.append("?")
            is_valid = False
        else:
            code_digits.append(str(max_idx))

    return "".join(code_digits), is_valid, min_confidence


def extract_full_mcq_answers(gray_img: np.ndarray, num_questions: int = 40) -> Tuple[Dict[int, Any], bool]:
    """
    Nhận diện đáp án Chế độ 1: 40 câu trắc nghiệm (A, B, C, D)
    Trả về: (answers_dict, needs_review: bool)
    """
    answers = {}
    options = ['A', 'B', 'C', 'D']
    needs_review = False

    for q_idx in range(num_questions):
        q_num = q_idx + 1
        if q_num <= 20:
            base_x = 120
            q_row = q_num - 1
        else:
            base_x = 640
            q_row = q_num - 21

        cy = 600 + q_row * 48
        densities = [get_bubble_density(gray_img, base_x + 125 + o * 75, cy, radius=12) for o in range(4)]
        
        sorted_d = sorted(densities, reverse=True)
        d_max1 = sorted_d[0]
        d_max2 = sorted_d[1]
        best_opt = options[int(np.argmax(densities))]

        # Ngưỡng phát hiện
        if d_max1 < 0.22:
            # Chưa tô ô nào
            answers[q_num] = None
        elif d_max2 > 0.25 and (d_max1 - d_max2) < 0.12:
            # Nghi vấn tô 2 ô hoặc tẩy lem nhem
            needs_review = True
            marked = [options[i] for i in range(4) if densities[i] >= 0.22]
            answers[q_num] = marked if len(marked) > 1 else best_opt
        else:
            answers[q_num] = best_opt

    return answers, needs_review


def extract_thpt_2025_answers(gray_img: np.ndarray) -> Tuple[Dict[str, Any], bool]:
    """
    Nhận diện đáp án Chế độ 2: Đề chuẩn THPT mới (Phần I, Phần II, Phần III)
    Trả về: (data_dict, needs_review: bool)
    """
    needs_review = False
    options = ['A', 'B', 'C', 'D']

    # -------------------------------------------------------------
    # 1. Nhận diện PHẦN I (12 câu 4 lựa chọn)
    # -------------------------------------------------------------
    part1 = {}
    for q_idx in range(12):
        q_num = q_idx + 1
        c_i = 0 if q_num <= 6 else 1
        bx = 140 if c_i == 0 else 640
        q_pos = (q_num - 1) if c_i == 0 else (q_num - 7)
        cy = 550 + q_pos * 40

        densities = [get_bubble_density(gray_img, bx + 130 + o * 70, cy, radius=11) for o in range(4)]
        sorted_d = sorted(densities, reverse=True)
        if sorted_d[0] < 0.22:
            part1[q_num] = None
        elif sorted_d[1] > 0.25 and (sorted_d[0] - sorted_d[1]) < 0.12:
            needs_review = True
            part1[q_num] = [options[i] for i in range(4) if densities[i] >= 0.22]
        else:
            part1[q_num] = options[int(np.argmax(densities))]

    # -------------------------------------------------------------
    # 2. Nhận diện PHẦN II (4 câu Đúng/Sai x 4 ý a,b,c,d)
    # -------------------------------------------------------------
    part2 = {}
    for q_idx in range(4):
        q_num = q_idx + 1
        bx = 130 if (q_idx % 2 == 0) else 640
        by = 880 if (q_idx < 2) else 1030
        part2[q_num] = {}

        for s_idx, sub in enumerate(['a', 'b', 'c', 'd']):
            sy = by + 10 + s_idx * 30
            d_d = get_bubble_density(gray_img, bx + 180, sy, radius=10) # Ô Đúng [D]
            d_s = get_bubble_density(gray_img, bx + 230, sy, radius=10) # Ô Sai [S]

            if max(d_d, d_s) < 0.20:
                part2[q_num][sub] = None
            elif abs(d_d - d_s) < 0.10 and min(d_d, d_s) > 0.20:
                needs_review = True
                part2[q_num][sub] = "Đ" if d_d > d_s else "S"
            else:
                part2[q_num][sub] = "Đ" if d_d > d_s else "S"

    # -------------------------------------------------------------
    # 3. Nhận diện PHẦN III (6 câu Trả lời ngắn - Bảng tô số 4 cột)
    # -------------------------------------------------------------
    part3 = {}
    for q_idx in range(6):
        q_num = q_idx + 1
        col_pos = q_idx % 3
        row_pos = q_idx // 3
        bx = 120 + col_pos * 340
        by = 1260 + row_pos * 160

        # Quét dấu '-' ở cột 0 và dấu ',' ở cột 1
        d_minus = get_bubble_density(gray_img, bx + 95, by + 16, radius=5)
        d_comma = get_bubble_density(gray_img, bx + 95 + 48, by + 16, radius=5)
        is_neg = (d_minus >= 0.40)
        has_comma = (d_comma >= 0.40)

        # Quét độc lập từng cột số 0, 1, 2, 3
        col_digits = [None, None, None, None]
        for c in range(4):
            cx = bx + 95 + c * 48
            col_densities = [get_bubble_density(gray_img, cx, by + 32 + d * 12, radius=5) for d in range(10)]
            sorted_d = sorted(col_densities, reverse=True)
            max_val = sorted_d[0]
            sec_val = sorted_d[1]
            best_d = int(col_densities.index(max_val))

            if max_val < 0.22:
                # Cột này để trống
                col_digits[c] = None
            elif sec_val >= 0.30 and (max_val - sec_val) < 0.15:
                # Tô trùng nhiều ô hoặc tẩy lem nhem trong cùng 1 cột
                needs_review = True
                col_digits[c] = "?"
            elif max_val >= 0.45 and (max_val - sec_val) >= 0.15:
                col_digits[c] = str(best_d)
            elif max_val >= 0.25:
                # Ô tô hơi mờ hoặc nghi vấn
                needs_review = True
                col_digits[c] = str(best_d)
            else:
                col_digits[c] = None

        # Kiểm tra xem cả câu có tô ô nào không
        filled_indices = [i for i, v in enumerate(col_digits) if v is not None]

        if not filled_indices and not is_neg and not has_comma:
            # Học sinh bỏ trống toàn bộ câu này
            part3[q_num] = ""
        else:
            # Kiểm tra lỗi: Có cột bị bỏ trống xen kẽ ở giữa không (ví dụ ['1', None, '5'])
            prefix = "-" if is_neg else ""
            if filled_indices:
                min_i = min(filled_indices)
                max_i = max(filled_indices)
                has_gap = any(col_digits[i] is None for i in range(min_i, max_i + 1))
                if has_gap:
                    # Báo cờ cần kiểm tra do bỏ trống cột ở giữa các chữ số
                    needs_review = True

                digits_list = [col_digits[i] if col_digits[i] is not None else "?" for i in range(min_i, max_i + 1)]
                if has_comma:
                    if len(digits_list) == 1:
                        val_res = prefix + digits_list[0]
                    else:
                        val_res = prefix + digits_list[0] + "." + "".join(digits_list[1:])
                else:
                    val_res = prefix + "".join(digits_list)
                part3[q_num] = val_res
            else:
                # Chỉ tô dấu '-' hoặc ',' mà không tô số
                needs_review = True
                part3[q_num] = prefix + ("." if has_comma else "?")

    result_data = {
        "part1": part1,
        "part2": part2,
        "part3": part3
    }
    return result_data, needs_review


def extract_all_data(
    aligned_bgr: np.ndarray, 
    mode: str = ExamMode.FULL_MCQ,
    num_questions: int = 40
) -> Dict[str, Any]:
    """
    Hàm tổng hợp trích xuất toàn bộ thông tin từ ảnh phiếu đã căn chỉnh.
    Tự động kiểm tra tính hợp lệ của SBD, Mã đề và cấu trúc đáp án.
    """
    gray = cv2.cvtColor(aligned_bgr, cv2.COLOR_BGR2GRAY) if len(aligned_bgr.shape) == 3 else aligned_bgr

    sbd, is_valid_sbd, conf_sbd = extract_sbd(gray)
    code, is_valid_code, conf_code = extract_exam_code(gray)

    header_warnings = []
    if not is_valid_sbd or "?" in sbd:
        header_warnings.append(f"SBD chưa rõ hoặc nghi vấn: '{sbd}'")
    if not is_valid_code or "?" in code:
        header_warnings.append(f"Mã đề chưa rõ hoặc nghi vấn: '{code}'")

    needs_review_header = (not is_valid_sbd) or (not is_valid_code) or (conf_sbd < 0.15) or (conf_code < 0.15)

    if mode == ExamMode.FULL_MCQ:
        answers, needs_rev = extract_full_mcq_answers(gray, num_questions=num_questions)
        return {
            "sbd": sbd,
            "is_valid_sbd": is_valid_sbd,
            "exam_code": code,
            "is_valid_code": is_valid_code,
            "header_warning": "; ".join(header_warnings),
            "answers": answers,
            "needs_review": needs_rev or needs_review_header
        }
    else:
        thpt_data, needs_rev = extract_thpt_2025_answers(gray)
        thpt_data["sbd"] = sbd
        thpt_data["is_valid_sbd"] = is_valid_sbd
        thpt_data["exam_code"] = code
        thpt_data["is_valid_code"] = is_valid_code
        thpt_data["header_warning"] = "; ".join(header_warnings)
        thpt_data["needs_review"] = needs_rev or needs_review_header
        return thpt_data
