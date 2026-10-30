"""
Module: omr_extractor.py
Chức năng cốt lõi: TỰ ĐỘNG DÒ TÌM MẪU VÀ BÓC TÁCH ĐÁP ÁN PHIẾU 50 CÂU (OMR)
Đặc điểm:
  - Tự động dò tìm vị trí 50 câu hỏi trên ảnh phiếu (Dynamic Bubble Grid Detection)
  - Thích ứng tự động với cả mẫu 2 cột (2x25) và mẫu 4 cột (chuẩn Bộ GD&ĐT)
  - Phân tích mật độ pixel đen từng ô A, B, C, D
  - Phát hiện câu bỏ trống, câu tô nhiều đáp án, cảnh báo tẩy lem nhem
  - Quét SBD (6 số) và Mã đề (3 số)
"""

import os
import sys
import cv2
import numpy as np
from typing import Dict, Tuple, Any, Optional, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

OPTIONS = ['A', 'B', 'C', 'D']


def get_bubble_density(gray_img: np.ndarray, cx: int, cy: int, radius: int = 11) -> float:
    """
    Tính tỷ lệ pixel được tô đen trong vùng tròn tâm (cx, cy) bán kính radius.
    Trả về tỷ lệ từ 0.0 (trắng hoàn toàn) đến 1.0 (đen hoàn toàn).
    """
    h, w = gray_img.shape[:2]
    x1, x2 = max(0, int(cx - radius)), min(w, int(cx + radius + 1))
    y1, y2 = max(0, int(cy - radius)), min(h, int(cy + radius + 1))

    roi = gray_img[y1:y2, x1:x2]
    if roi.size == 0:
        return 0.0

    _, thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    mask = np.zeros(roi.shape, dtype=np.uint8)
    cv2.circle(mask, (int(cx - x1), int(cy - y1)), int(radius * 0.85), 255, -1)

    masked_pixels = cv2.bitwise_and(thresh, thresh, mask=mask)
    total_mask_pixels = cv2.countNonZero(mask)
    if total_mask_pixels == 0:
        return 0.0

    return float(cv2.countNonZero(masked_pixels)) / float(total_mask_pixels)


def get_default_50_coords(q_num: int) -> Tuple[int, List[int]]:
    """Tọa độ chuẩn dự phòng (Fallback) cho mẫu 50 câu 2 cột"""
    if q_num <= 25:
        base_x = 110
        q_row = q_num - 1
    else:
        base_x = 640
        q_row = q_num - 26

    cy = 585 + q_row * 39
    cx_list = [base_x + 130 + o * 75 for o in range(4)]
    return cy, cx_list


def detect_bubbles_50_questions(gray_img: np.ndarray) -> Dict[int, Tuple[int, List[int]]]:
    """
    THUẬT TOÁN TỰ ĐỘNG DÒ TÌM MA TRẬN 50 CÂU HỎI TRẮC NGHIỆM:
      1. Quét contour trong vùng bài làm (Y từ 510 đến 1620)
      2. Lọc các contour có diện tích và độ tròn Circularity đặc trưng ô OMR
      3. Gom nhóm theo hàng ngang Y (cùng cao độ)
      4. Tách các cụm 4 ô (A, B, C, D) và phân nhóm theo cột dọc từ trái sang phải
    Tự động thích ứng với cả mẫu 50 câu 2 cột lẫn mẫu 50 câu 4 cột!
    """
    h_img, w_img = gray_img.shape[:2]
    roi = gray_img[510:1620, :]
    
    thresh = cv2.adaptiveThreshold(
        cv2.GaussianBlur(roi, (5, 5), 0), 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 7
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 160 <= area <= 2500:
            peri = cv2.arcLength(cnt, True)
            if peri > 0:
                circ = 4 * np.pi * area / (peri * peri)
                if 0.50 <= circ <= 1.50:
                    x, y, w, h = cv2.boundingRect(cnt)
                    if 0.60 <= (w / h) <= 1.50 and w >= 15 and h >= 15:
                        candidates.append((x + w // 2, 510 + y + h // 2))

    # Khử trùng lặp
    unique_bubbles = []
    for cx, cy in candidates:
        if not any((cx - ux)**2 + (cy - uy)**2 < 64 for ux, uy in unique_bubbles):
            unique_bubbles.append((cx, cy))

    if len(unique_bubbles) < 100:
        # Nếu ảnh mờ hoặc không quét đủ ô tròn, dùng tọa độ chuẩn dự phòng
        return {q: get_default_50_coords(q) for q in range(1, 51)}

    # Gom nhóm theo hàng Y
    unique_bubbles.sort(key=lambda b: b[1])
    y_bands = []
    cur_band = [unique_bubbles[0]]
    for b in unique_bubbles[1:]:
        if abs(b[1] - cur_band[-1][1]) < 15:
            cur_band.append(b)
        else:
            y_bands.append(cur_band)
            cur_band = [b]
    y_bands.append(cur_band)

    col_questions = {}
    for band in y_bands:
        band.sort(key=lambda b: b[0])
        quartets = []
        cur_q = [band[0]]
        for b in band[1:]:
            if b[0] - cur_q[-1][0] > 110 or len(cur_q) == 4:
                if len(cur_q) == 4:
                    quartets.append(cur_q)
                cur_q = [b]
            else:
                cur_q.append(b)
        if len(cur_q) == 4:
            quartets.append(cur_q)

        for q in quartets:
            cx_center = sum(b[0] for b in q) / 4
            cy_avg = int(sum(b[1] for b in q) / 4)
            cx_list = [b[0] for b in q]
            col_id = int(cx_center // 200)
            if col_id not in col_questions:
                col_questions[col_id] = []
            col_questions[col_id].append((cy_avg, cx_list))

    final_questions = {}
    q_counter = 1
    for col_id in sorted(col_questions.keys()):
        rows = sorted(col_questions[col_id], key=lambda r: r[0])
        for r in rows:
            final_questions[q_counter] = r
            q_counter += 1

    # Nếu dò được đủ 50 câu -> dùng kết quả dò tự động
    if len(final_questions) >= 48:
        return final_questions

    # Nếu dò thiếu câu (do ảnh chụp lệch/nhiễu), fallback về tọa độ chuẩn
    return {q: get_default_50_coords(q) for q in range(1, 51)}


def extract_sbd(gray_img: np.ndarray) -> Tuple[str, bool, float]:
    """Quét khối Số Báo Danh (6 cột x 10 hàng 0-9)"""
    sbd_digits = []
    min_confidence = 1.0
    is_valid = True

    for col in range(6):
        cx = 155 + col * 65
        densities = [get_bubble_density(gray_img, cx, 245 + r * 20, radius=7) for r in range(10)]
        max_idx = int(np.argmax(densities))
        max_val = densities[max_idx]

        sorted_d = sorted(densities, reverse=True)
        conf = sorted_d[0] - sorted_d[1]
        min_confidence = min(min_confidence, conf)

        if max_val < 0.22:
            sbd_digits.append("")
            is_valid = False
        elif sorted_d[1] >= 0.22 and conf < 0.12:
            sbd_digits.append("?")
            is_valid = False
        else:
            sbd_digits.append(str(max_idx))

    res_str = "".join([d if d else "?" for d in sbd_digits])
    if all(d == "" for d in sbd_digits):
        return "", False, 0.0

    return res_str, is_valid, min_confidence


def extract_exam_code(gray_img: np.ndarray) -> Tuple[str, bool, float]:
    """Quét khối Mã Đề Thi (3 cột x 10 hàng 0-9)"""
    code_digits = []
    min_confidence = 1.0
    is_valid = True

    for col in range(3):
        cx = 605 + col * 65
        densities = [get_bubble_density(gray_img, cx, 245 + r * 20, radius=7) for r in range(10)]
        max_idx = int(np.argmax(densities))
        max_val = densities[max_idx]

        sorted_d = sorted(densities, reverse=True)
        conf = sorted_d[0] - sorted_d[1]
        min_confidence = min(min_confidence, conf)

        if max_val < 0.22:
            code_digits.append("")
            is_valid = False
        elif sorted_d[1] >= 0.22 and conf < 0.12:
            code_digits.append("?")
            is_valid = False
        else:
            code_digits.append(str(max_idx))

    res_str = "".join([d if d else "?" for d in code_digits])
    if all(d == "" for d in code_digits):
        return "", False, 0.0

    return res_str, is_valid, min_confidence


def extract_all_data(aligned_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Hàm tự động dò tìm vị trí và bóc tách đáp án 50 câu:
      - Tự dò tọa độ 50 câu trên tờ phiếu
      - Tính mật độ pixel từng ô A, B, C, D
      - Nhận diện câu được tô, câu bỏ trống, câu tô trùng
      - Nhận diện SBD và Mã đề thi
    """
    gray = cv2.cvtColor(aligned_bgr, cv2.COLOR_BGR2GRAY) if len(aligned_bgr.shape) == 3 else aligned_bgr

    # 1. Tự động dò tìm tọa độ 50 câu
    coords_map = detect_bubbles_50_questions(gray)

    answers = {}
    warnings = []
    needs_rev = False
    radius = 11
    threshold_filled = 0.30

    for q_num in range(1, 51):
        if q_num not in coords_map:
            answers[q_num] = None
            continue

        cy, cx_list = coords_map[q_num]
        densities = [get_bubble_density(gray, cx, cy, radius=radius) for cx in cx_list]

        sorted_d = sorted(densities, reverse=True)
        max_val = sorted_d[0]
        second_val = sorted_d[1]
        best_opt = OPTIONS[int(np.argmax(densities))]

        marked_opts = [OPTIONS[i] for i in range(4) if densities[i] >= threshold_filled]

        # Bỏ trống
        if max_val < 0.25:
            answers[q_num] = None
        # Tô nhiều đáp án
        elif len(marked_opts) > 1 and (max_val - second_val) < 0.20:
            answers[q_num] = marked_opts
            needs_rev = True
            warnings.append(f"Câu {q_num}: Tô {len(marked_opts)} đáp án ({', '.join(marked_opts)})")
        # Tô 1 đáp án
        else:
            answers[q_num] = best_opt
            if second_val >= 0.25 and (max_val - second_val) < 0.15:
                needs_rev = True
                warnings.append(f"Câu {q_num}: Nghi vấn tẩy lem nhem")
            elif max_val < 0.35:
                needs_rev = True
                warnings.append(f"Câu {q_num}: Tô mờ")

    # 2. Quét SBD & Mã đề
    sbd, is_valid_sbd, _ = extract_sbd(gray)
    code, is_valid_code, _ = extract_exam_code(gray)

    header_warnings = []
    if sbd and ("?" in sbd or not is_valid_sbd):
        header_warnings.append(f"SBD chưa rõ: '{sbd}'")
        needs_rev = True
    if code and ("?" in code or not is_valid_code):
        header_warnings.append(f"Mã đề chưa rõ: '{code}'")
        needs_rev = True

    all_warnings = header_warnings + warnings

    return {
        "num_questions": 50,
        "coords_map": coords_map,
        "sbd": sbd,
        "is_valid_sbd": is_valid_sbd,
        "exam_code": code,
        "is_valid_code": is_valid_code,
        "answers": answers,
        "needs_review": needs_rev,
        "warnings": all_warnings,
        "warning_message": "; ".join(all_warnings[:3]) if all_warnings else ""
    }


def get_question_coords(q_num: int) -> Tuple[int, List[int]]:
    """Tọa độ câu hỏi 50 câu chuẩn"""
    return get_default_50_coords(q_num)
