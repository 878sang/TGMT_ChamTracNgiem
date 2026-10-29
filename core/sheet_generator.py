"""
Module: sheet_generator.py
Tạo mẫu phiếu trắc nghiệm chuẩn (PNG/JPG) và sinh ảnh bài làm mẫu có tô chì
để thử nghiệm toàn bộ hệ thống Thị giác máy tính.
Hỗ trợ cả 2 mẫu:
  1. Mẫu Full trắc nghiệm 40 câu
  2. Mẫu Chuẩn THPT mới BGD&ĐT 2025 (3 Phần)
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import cv2
import numpy as np
from core.cv_utils import imwrite_utf8



CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 1700
MARKER_SIZE = 50
MARGIN = 40

# Tọa độ 4 marker góc
# TL: (40, 40), TR: (1110, 40), BL: (40, 1610), BR: (1110, 1610)
MARKER_TL = (MARGIN, MARGIN)
MARKER_TR = (CANVAS_WIDTH - MARGIN - MARKER_SIZE, MARGIN)
MARKER_BL = (MARGIN, CANVAS_HEIGHT - MARGIN - MARKER_SIZE)
MARKER_BR = (CANVAS_WIDTH - MARGIN - MARKER_SIZE, CANVAS_HEIGHT - MARGIN - MARKER_SIZE)


def create_blank_canvas() -> np.ndarray:
    """Tạo tờ giấy trắng 1200x1700 và vẽ 4 ô vuông đen to ở 4 góc định vị"""
    img = np.ones((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8) * 255

    # Vẽ 4 Marker vuông màu đen đặc
    for (mx, my) in [MARKER_TL, MARKER_TR, MARKER_BL, MARKER_BR]:
        cv2.rectangle(img, (mx, my), (mx + MARKER_SIZE, my + MARKER_SIZE), (0, 0, 0), -1)

    # Khung viền mỏng ngoài
    cv2.rectangle(img, (MARGIN + 5, MARGIN + 5), 
                  (CANVAS_WIDTH - MARGIN - 5, CANVAS_HEIGHT - MARGIN - 5), (100, 100, 100), 2)
    return img


def draw_header_section(
    img: np.ndarray, 
    title: str, 
    subtitle: str, 
    student_name: str = "",
    sbd: str = "",
    exam_code: str = ""
) -> None:
    """Vẽ phần tiêu đề bài thi, khung Họ và tên (OCR), khung SBD & Mã đề (OMR + OCR)"""
    # Tiêu đề
    cv2.putText(img, title, (200, 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (20, 20, 100), 2)
    cv2.putText(img, subtitle, (300, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 1)

    # Khung Họ và tên thí sinh (Dành cho nhận diện OCR): X: 120->620, Y: 98->136
    cv2.rectangle(img, (120, 98), (620, 136), (80, 80, 80), 1)
    cv2.putText(img, "Ho va ten:", (128, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 1)
    if student_name:
        cv2.putText(img, str(student_name).upper(), (230, 125), cv2.FONT_HERSHEY_DUPLEX, 0.65, (10, 10, 80), 2)

    # Khung Lớp
    cv2.rectangle(img, (640, 98), (880, 136), (80, 80, 80), 1)
    cv2.putText(img, "Lop: ..............", (648, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 1)

    # Khung Số Báo Danh (SBD: 6 cột x 10 hàng 0-9) tại X: 120->560, Y: 140->460
    cv2.rectangle(img, (120, 140), (560, 460), (0, 0, 0), 2)
    cv2.putText(img, "SO BAO DANH", (240, 162), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 0, 0), 1)
    
    # 6 ô chữ số viết tay SBD ở trên đỉnh (Dành cho OCR đối chiếu)
    sbd_str = f"{sbd:>06}"[:6] if sbd else ""
    for col in range(6):
        cx = 160 + col * 65
        cv2.rectangle(img, (cx - 16, 168), (cx + 16, 190), (100, 100, 100), 1)
        if sbd_str and col < len(sbd_str) and sbd_str[col].isdigit():
            cv2.putText(img, sbd_str[col], (cx - 5, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 120), 1)

        for row in range(10):
            cy = 200 + row * 25
            cv2.circle(img, (cx, cy), 9, (120, 120, 120), 1)
            cv2.putText(img, str(row), (cx - 4, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (80, 80, 80), 1)

    # Khung Mã Đề Thi (3 cột x 10 hàng 0-9) tại X: 640->880, Y: 140->460
    cv2.rectangle(img, (640, 140), (880, 460), (0, 0, 0), 2)
    cv2.putText(img, "MA DE", (720, 162), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 0, 0), 1)
    code_str = f"{exam_code:>03}"[:3] if exam_code else ""
    for col in range(3):
        cx = 680 + col * 65
        cv2.rectangle(img, (cx - 16, 168), (cx + 16, 190), (100, 100, 100), 1)
        if code_str and col < len(code_str) and code_str[col].isdigit():
            cv2.putText(img, code_str[col], (cx - 5, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 120), 1)

        for row in range(10):
            cy = 200 + row * 25
            cv2.circle(img, (cx, cy), 9, (120, 120, 120), 1)
            cv2.putText(img, str(row), (cx - 4, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (80, 80, 80), 1)

    # Khung Hướng dẫn tô
    cv2.rectangle(img, (920, 140), (1130, 460), (100, 100, 100), 1)
    cv2.putText(img, "HUONG DAN TO", (940, 175), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 0, 0), 1)
    cv2.circle(img, (960, 220), 10, (40, 40, 40), -1)
    cv2.putText(img, "Dung", (985, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 120, 0), 1)
    cv2.circle(img, (960, 260), 10, (100, 100, 100), 1)
    cv2.line(img, (952, 252), (968, 268), (0, 0, 200), 2)
    cv2.putText(img, "Sai", (985, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 1)


def generate_full_mcq_template(student_name: str = "", sbd: str = "", exam_code: str = "") -> np.ndarray:
    """Tạo mẫu phiếu thi Chế độ 1: Full trắc nghiệm 40 câu (2 cột x 20 câu)"""
    img = create_blank_canvas()
    draw_header_section(
        img, "PHIEU TRA LOI TRAC NGHIEM (40 CAU)", "Kiem tra dinh ky / Hoc ky",
        student_name=student_name, sbd=sbd, exam_code=exam_code
    )

    # Bảng 40 câu: Cột 1 (Câu 1-20): X=120, Cột 2 (Câu 21-40): X=640
    # Y bắt đầu từ 520, mỗi câu cách nhau 50px
    options = ['A', 'B', 'C', 'D']
    
    cv2.putText(img, "PHAN TRA LOI TRAC NGHIEM", (420, 500), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 120), 2)

    for col_idx, start_q in enumerate([1, 21]):
        base_x = 120 if col_idx == 0 else 640
        # Khung cột
        cv2.rectangle(img, (base_x - 10, 520), (base_x + 440, 1580), (0, 0, 0), 2)
        
        # Header cột
        cv2.putText(img, "Cau", (base_x + 10, 550), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 0), 1)
        for o_idx, opt in enumerate(options):
            cv2.putText(img, opt, (base_x + 120 + o_idx * 75, 550), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 0), 1)
        cv2.line(img, (base_x - 10, 565), (base_x + 440, 565), (0, 0, 0), 1)

        for q in range(20):
            q_num = start_q + q
            y = 600 + q * 48
            # Tên câu
            cv2.putText(img, f"{q_num:02d}", (base_x + 10, y + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1)
            # 4 ô A, B, C, D
            for o_idx in range(4):
                bx = base_x + 125 + o_idx * 75
                cv2.circle(img, (bx, y), 13, (100, 100, 100), 2)
                cv2.putText(img, options[o_idx], (bx - 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1)
            cv2.line(img, (base_x - 10, y + 24), (base_x + 440, y + 24), (220, 220, 220), 1)

    return img


def generate_thpt_2025_template(student_name: str = "", sbd: str = "", exam_code: str = "") -> np.ndarray:
    """Tạo mẫu phiếu thi Chế độ 2: Đề chuẩn THPT mới (Phần I, II, III)"""
    img = create_blank_canvas()
    draw_header_section(
        img, "PHIEU THI TOT NGHIEP THPT 2025 (CHUAN BGD&DT)", "Cau truc moi: 4 Lua chon | Dung-Sai | Tra loi ngan",
        student_name=student_name, sbd=sbd, exam_code=exam_code
    )

    # -------------------------------------------------------------
    # PHẦN I: TRẮC NGHIỆM 4 LỰA CHỌN (12 câu) tại Y = 490 -> 820
    # -------------------------------------------------------------
    cv2.rectangle(img, (100, 480), (1130, 800), (0, 0, 0), 2)
    cv2.rectangle(img, (100, 480), (1130, 515), (200, 220, 240), -1)
    cv2.putText(img, "PHAN I: TRAC NGHIEM 4 LUA CHON (12 Cau - 3.0 Diem)", (120, 505), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 100), 2)

    # Chia làm 2 cột: Cột 1 (Câu 1-6), Cột 2 (Câu 7-12)
    options = ['A', 'B', 'C', 'D']
    for c_i, start_q in enumerate([1, 7]):
        bx = 140 if c_i == 0 else 640
        for q in range(6):
            q_num = start_q + q
            y = 550 + q * 40
            cv2.putText(img, f"Cau {q_num:02d}:", (bx, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1)
            for o_i in range(4):
                cx = bx + 130 + o_i * 70
                cv2.circle(img, (cx, y), 12, (100, 100, 100), 2)
                cv2.putText(img, options[o_i], (cx - 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1)

    # -------------------------------------------------------------
    # PHẦN II: TRẮC NGHIỆM ĐÚNG / SAI (4 câu x 4 ý) tại Y = 820 -> 1210
    # -------------------------------------------------------------
    cv2.rectangle(img, (100, 820), (1130, 1190), (0, 0, 0), 2)
    cv2.rectangle(img, (100, 820), (1130, 855), (200, 220, 240), -1)
    cv2.putText(img, "PHAN II: TRAC NGHIEM DUNG / SAI (4 Cau - 4.0 Diem)", (120, 845), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 100), 2)

    # 4 câu: Mỗi câu gồm 4 ý a, b, c, d
    for q_idx in range(4):
        q_num = q_idx + 1
        # 2 câu trên, 2 câu dưới
        bx = 130 if (q_idx % 2 == 0) else 640
        by = 880 if (q_idx < 2) else 1030
        
        cv2.putText(img, f"Cau {q_num}:", (bx, by + 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 120), 1)
        # 4 ý a, b, c, d
        for s_idx, sub in enumerate(['a', 'b', 'c', 'd']):
            sy = by + 10 + s_idx * 30
            cv2.putText(img, f"{sub})", (bx + 110, sy + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1)
            # Ô Đúng [D] và Sai [S]
            cv2.circle(img, (bx + 180, sy), 11, (100, 100, 100), 2)
            cv2.putText(img, "D", (bx + 175, sy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1)
            cv2.circle(img, (bx + 230, sy), 11, (100, 100, 100), 2)
            cv2.putText(img, "S", (bx + 225, sy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1)

    # -------------------------------------------------------------
    # PHẦN III: TRẢ LỜI NGẮN (6 câu - Bảng tô số) tại Y = 1210 -> 1600
    # -------------------------------------------------------------
    cv2.rectangle(img, (100, 1210), (1130, 1590), (0, 0, 0), 2)
    cv2.rectangle(img, (100, 1210), (1130, 1245), (200, 220, 240), -1)
    cv2.putText(img, "PHAN III: TRAC NGHIEM TRA LOI NGAN (6 Cau - 3.0 Diem)", (120, 1235), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 100), 2)

    # 6 câu: Mỗi câu có 4 cột số (dấu trừ '-', ',', 0-9)
    # Xếp thành 6 block ngang: Câu 1, 2, 3 (hàng trên), Câu 4, 5, 6 (hàng dưới)
    for q_idx in range(6):
        q_num = q_idx + 1
        col_pos = q_idx % 3
        row_pos = q_idx // 3
        bx = 120 + col_pos * 340
        by = 1260 + row_pos * 160

        cv2.putText(img, f"Cau {q_num}", (bx + 10, by + 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 120), 1)
        # Vẽ 4 cột số
        for c in range(4):
            cx = bx + 95 + c * 48
            # Hàng trên: Dấu '-' ở cột 0, dấu ',' ở cột 1
            if c == 0:
                cv2.circle(img, (cx, by + 16), 6, (120, 120, 120), 1)
                cv2.putText(img, "-", (cx - 3, by + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (80, 80, 80), 1)
            elif c == 1:
                cv2.circle(img, (cx, by + 16), 6, (120, 120, 120), 1)
                cv2.putText(img, ",", (cx - 3, by + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (80, 80, 80), 1)

            # Các hàng số 0-9
            for d in range(10):
                cy = by + 32 + d * 12
                cv2.circle(img, (cx, cy), 5, (120, 120, 120), 1)
                cv2.putText(img, str(d), (cx - 3, cy + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.26, (80, 80, 80), 1)

    return img


def fill_bubble(img: np.ndarray, center_x: int, center_y: int, radius: int = 11, intensity: int = 35) -> None:
    """Tô chì vào một ô tròn với màu bút chì thực tế (đen đậm, hơi lem nhẹ)"""
    # Lõi đen đậm
    cv2.circle(img, (center_x, center_y), radius - 1, (intensity, intensity, intensity), -1)
    # Hơi lem viền cho giống bút chì tô tay thật
    cv2.circle(img, (center_x, center_y), radius, (intensity + 30, intensity + 30, intensity + 30), 1)


def generate_sample_submission_full_mcq(
    sbd: str = "000001", 
    exam_code: str = "101", 
    answers: dict = None,
    student_name: str = ""
) -> np.ndarray:
    """Tạo ảnh bài làm mẫu đã được tô chì cho Chế độ 1 (Full trắc nghiệm)"""
    img = generate_full_mcq_template(student_name=student_name, sbd=sbd, exam_code=exam_code)

    # 1. Tô SBD (6 số)
    sbd_str = f"{sbd:>06}"[:6]
    for col, digit in enumerate(sbd_str):
        row = int(digit)
        cx = 160 + col * 65
        cy = 200 + row * 25
        fill_bubble(img, cx, cy, radius=8)

    # 2. Tô Mã Đề (3 số)
    code_str = f"{exam_code:>03}"[:3]
    for col, digit in enumerate(code_str):
        row = int(digit)
        cx = 680 + col * 65
        cy = 200 + row * 25
        fill_bubble(img, cx, cy, radius=8)

    # 3. Tô 40 câu
    opt_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    default_answers = {i: ['A', 'B', 'C', 'D'][(i * 3 + 1) % 4] for i in range(1, 41)}
    active_answers = answers or default_answers

    for q_num, ans in active_answers.items():
        if ans not in opt_map:
            continue
        o_idx = opt_map[ans]
        if q_num <= 20:
            base_x = 120
            q_in_col = q_num - 1
        else:
            base_x = 640
            q_in_col = q_num - 21

        bx = base_x + 125 + o_idx * 75
        by = 600 + q_in_col * 48
        fill_bubble(img, bx, by, radius=12)

    return img


def generate_sample_submission_thpt_2025(
    sbd: str = "000011", 
    exam_code: str = "101",
    p1_answers: dict = None,
    p2_answers: dict = None,
    p3_answers: dict = None,
    student_name: str = ""
) -> np.ndarray:
    """Tạo ảnh bài làm mẫu đã được tô chì cho Chế độ 2 (Chuẩn THPT 2025)"""
    img = generate_thpt_2025_template(student_name=student_name, sbd=sbd, exam_code=exam_code)

    # 1. Tô SBD & Mã đề
    sbd_str = f"{sbd:>06}"[:6]
    for col, digit in enumerate(sbd_str):
        row = int(digit)
        fill_bubble(img, 160 + col * 65, 200 + row * 25, radius=8)

    code_str = f"{exam_code:>03}"[:3]
    for col, digit in enumerate(code_str):
        row = int(digit)
        fill_bubble(img, 680 + col * 65, 200 + row * 25, radius=8)

    # 2. Tô PHẦN I (12 câu)
    opt_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    default_p1 = {i: ['A', 'C', 'B', 'D'][i % 4] for i in range(1, 13)}
    use_p1 = p1_answers or default_p1

    for q_num, ans in use_p1.items():
        if ans not in opt_map:
            continue
        o_idx = opt_map[ans]
        c_i = 0 if q_num <= 6 else 1
        bx = 140 if c_i == 0 else 640
        q_pos = (q_num - 1) if c_i == 0 else (q_num - 7)
        cx = bx + 130 + o_idx * 70
        cy = 550 + q_pos * 40
        fill_bubble(img, cx, cy, radius=11)

    # 3. Tô PHẦN II (4 câu Đúng/Sai)
    default_p2 = {
        1: {'a': 'Đ', 'b': 'S', 'c': 'Đ', 'd': 'Đ'},
        2: {'a': 'S', 'b': 'Đ', 'c': 'S', 'd': 'Đ'},
        3: {'a': 'Đ', 'b': 'Đ', 'c': 'S', 'd': 'S'},
        4: {'a': 'S', 'b': 'S', 'c': 'Đ', 'd': 'Đ'}
    }
    use_p2 = p2_answers or default_p2

    for q_idx in range(4):
        q_num = q_idx + 1
        bx = 130 if (q_idx % 2 == 0) else 640
        by = 880 if (q_idx < 2) else 1030
        subs = use_p2.get(q_num, {})
        for s_idx, sub in enumerate(['a', 'b', 'c', 'd']):
            sy = by + 10 + s_idx * 30
            val = str(subs.get(sub, "")).strip().upper()
            if val in {"Đ", "D", "T"}:
                fill_bubble(img, bx + 180, sy, radius=10)
            elif val in {"S", "F"}:
                fill_bubble(img, bx + 230, sy, radius=10)

    # 4. Tô PHẦN III (6 câu trả lời ngắn)
    default_p3 = {1: "15", 2: "-2.5", 3: "0.75", 4: "120", 5: "-8", 6: "3.14"}
    use_p3 = p3_answers or default_p3

    for q_idx in range(6):
        q_num = q_idx + 1
        col_pos = q_idx % 3
        row_pos = q_idx // 3
        bx = 120 + col_pos * 340
        by = 1260 + row_pos * 160
        val_str = str(use_p3.get(q_num, "")).strip()
        if not val_str:
            continue

        # Nếu là số âm: tô dấu '-' ở cột 0
        is_neg = val_str.startswith("-")
        if is_neg:
            fill_bubble(img, bx + 95, by + 16, radius=5)
            val_str = val_str[1:]

        # Nếu có dấu phẩy/chấm: tô dấu ',' ở cột 1
        has_comma = ("," in val_str or "." in val_str)
        if has_comma:
            fill_bubble(img, bx + 95 + 48, by + 16, radius=5)
            val_str = val_str.replace(",", "").replace(".", "")

        # Tô các chữ số vào các cột
        for c_idx, ch in enumerate(val_str[:4]):
            if ch.isdigit():
                digit = int(ch)
                cx = bx + 95 + c_idx * 48
                cy = by + 32 + digit * 12
                fill_bubble(img, cx, cy, radius=5)

    return img


def simulate_camera_photo(perfect_img: np.ndarray, angle: float = 3.5, shadow: bool = True) -> np.ndarray:
    """
    Giả lập ảnh chụp bằng điện thoại ngoài đời thực:
    - Đặt trên nền bàn gỗ/gạch
    - Bị xoay/nghiêng góc (1-5 độ)
    - Phối cảnh biến dạng (Perspective skew)
    - Đổ bóng tay/điện thoại
    """
    h, w = perfect_img.shape[:2]
    # Nền bàn lớn hơn
    pad = 120
    bg_h, bg_w = h + pad * 2, w + pad * 2
    # Nền màu gỗ ấm (180, 200, 220)
    bg = np.ones((bg_h, bg_w, 3), dtype=np.uint8)
    bg[:, :] = [160, 190, 215]  # Nền bàn gỗ BGR

    # Thêm vân gỗ giả lập
    noise = np.random.normal(0, 10, bg.shape).astype(np.int16)
    bg = np.clip(bg.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Tọa độ 4 góc tờ giấy ban đầu
    pts1 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])

    # Tọa độ 4 góc trên nền có góc chụp nghiêng phối cảnh
    pts2 = np.float32([
        [pad + 25, pad + 15],
        [pad + w + 10, pad + 35],
        [pad + w - 20, pad + h + 10],
        [pad - 15, pad + h - 15]
    ])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    warped_paper = cv2.warpPerspective(perfect_img, matrix, (bg_w, bg_h))

    # Mask để dán lên nền
    mask = np.zeros((h, w), dtype=np.uint8)
    mask.fill(255)
    warped_mask = cv2.warpPerspective(mask, matrix, (bg_w, bg_h))

    # Hợp nhất giấy vào nền
    bg[warped_mask > 0] = warped_paper[warped_mask > 0]

    # Thêm bóng đổ nhẹ góc trái
    if shadow:
        cv2.ellipse(bg, (bg_w // 4, bg_h // 3), (350, 450), 30, 0, 360, (0, 0, 0), -1)
        bg = cv2.addWeighted(bg, 0.88, bg, 0.12, 0)

    return bg


if __name__ == "__main__":
    templates_dir = "d:/Thị giác máy tính/Đồ Án/templates"
    sample_dir = "d:/Thị giác máy tính/Đồ Án/dataset/sample_submissions"
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(sample_dir, exist_ok=True)

    # =============================================================
    # 1. TẠO 2 MẪU PHIẾU TRẮNG (DÙNG ĐỂ IN ẤN HOẶC TEST KHUNG GỐC)
    # =============================================================
    t_full = generate_full_mcq_template()
    imwrite_utf8(os.path.join(templates_dir, "phieu_full_40_cau.png"), t_full)

    t_thpt = generate_thpt_2025_template()
    imwrite_utf8(os.path.join(templates_dir, "phieu_thpt_2025.png"), t_thpt)

    # =============================================================
    # 2. BỘ ẢNH TEST CHẾ ĐỘ 1: FULL TRẮC NGHIỆM (40 CÂU)
    # =============================================================
    # Bài thi chuẩn 101 của đề mẫu
    key_full_101 = {i: ['A', 'D', 'C', 'B'][(i - 1) % 4] for i in range(1, 41)}

    # Thí sinh 1: Nguyễn Văn An (SBD: 000001, Mã đề: 101) - Làm đúng toàn bộ (10.0đ)
    s_full_1 = generate_sample_submission_full_mcq("000001", "101", answers=key_full_101, student_name="Nguyen Van An")
    imwrite_utf8(os.path.join(sample_dir, "001_NguyenVanA_FullTN.png"), s_full_1)

    # Thí sinh 2: Lê Thị Cúc (SBD: 000002, Mã đề: 101) - Làm đúng 32/40 câu (~8.0đ)
    ans_cuc = dict(key_full_101)
    for q_err in [3, 7, 12, 18, 25, 29, 34, 39]:
        ans_cuc[q_err] = ['B', 'C', 'A', 'D'][q_err % 4]
    s_full_2 = generate_sample_submission_full_mcq("000002", "101", answers=ans_cuc, student_name="Le Thi Cuc")
    imwrite_utf8(os.path.join(sample_dir, "002_LeThiC_FullTN.png"), s_full_2)

    # Thí sinh 3: Trần Văn Dũng (SBD: 000003, Mã đề: 101) - Có câu sai và câu bỏ trống (~6.0đ)
    ans_dung = dict(key_full_101)
    for q_err in [2, 5, 11, 16, 21, 26, 31, 36]:
        ans_dung[q_err] = ['C', 'A', 'D', 'B'][q_err % 4]
    for q_blank in [38, 39, 40]:
        ans_dung.pop(q_blank, None)
    s_full_3 = generate_sample_submission_full_mcq("000003", "101", answers=ans_dung, student_name="Tran Van Dung")
    imwrite_utf8(os.path.join(sample_dir, "003_TranVanD_FullTN.png"), s_full_3)

    # Ảnh chụp điện thoại thực tế của bài 1 (có nghiêng góc, nền bàn gỗ, bóng đổ nhẹ)
    photo_full_1 = simulate_camera_photo(s_full_1, angle=3.2, shadow=True)
    imwrite_utf8(os.path.join(sample_dir, "photo_001_NguyenVanA_ChupNghieng.jpg"), photo_full_1)
    # Giữ lại tên cũ để tương thích với các lệnh test cũ
    imwrite_utf8(os.path.join(sample_dir, "photo_test_full_mcq.jpg"), photo_full_1)

    # =============================================================
    # 3. BỘ ẢNH TEST CHẾ ĐỘ 2: CHUẨN THPT MỚI (3 PHẦN BỘ GD&ĐT)
    # =============================================================
    # Đáp án chuẩn đề THPT mẫu:
    key_thpt_p1 = {1: 'A', 2: 'C', 3: 'B', 4: 'D', 5: 'A', 6: 'B', 7: 'D', 8: 'C', 9: 'A', 10: 'B', 11: 'C', 12: 'D'}
    key_thpt_p2 = {
        1: {'a': 'Đ', 'b': 'S', 'c': 'Đ', 'd': 'Đ'},
        2: {'a': 'S', 'b': 'Đ', 'c': 'S', 'd': 'Đ'},
        3: {'a': 'Đ', 'b': 'Đ', 'c': 'S', 'd': 'S'},
        4: {'a': 'S', 'b': 'S', 'c': 'Đ', 'd': 'Đ'}
    }
    key_thpt_p3 = {1: "15", 2: "-2.5", 3: "0.75", 4: "120", 5: "-8", 6: "3.14"}

    # Thí sinh 1: Trần Thị Bình (SBD: 000011, Mã đề: 101) - Làm tốt gần tối đa
    s_thpt_1 = generate_sample_submission_thpt_2025(
        sbd="000011", exam_code="101",
        p1_answers=key_thpt_p1, p2_answers=key_thpt_p2, p3_answers=key_thpt_p3,
        student_name="Tran Thi Binh"
    )
    imwrite_utf8(os.path.join(sample_dir, "002_TranThiB_THPT.png"), s_thpt_1)
    imwrite_utf8(os.path.join(sample_dir, "101_TranThiB_THPT.png"), s_thpt_1)

    # Thí sinh 2: Hoàng Minh Châu (SBD: 000012, Mã đề: 101) - Điểm khá (sai 3 câu P1, P2 đúng 2-3 ý/câu, P3 đúng 4 câu)
    ans_p1_chau = dict(key_thpt_p1)
    ans_p1_chau[3] = 'D'; ans_p1_chau[8] = 'A'; ans_p1_chau[11] = 'B'
    ans_p2_chau = {
        1: {'a': 'Đ', 'b': 'Đ', 'c': 'Đ', 'd': 'Đ'}, # đúng 3 ý -> 0.5đ
        2: {'a': 'S', 'b': 'Đ', 'c': 'Đ', 'd': 'Đ'}, # đúng 3 ý -> 0.5đ
        3: {'a': 'Đ', 'b': 'Đ', 'c': 'S', 'd': 'S'}, # đúng 4 ý -> 1.0đ
        4: {'a': 'S', 'b': 'Đ', 'c': 'Đ', 'd': 'S'}  # đúng 2 ý -> 0.25đ
    }
    ans_p3_chau = {1: "15", 2: "-2.5", 3: "0.75", 4: "100", 5: "-8", 6: "3.00"} # câu 4 và 6 sai
    s_thpt_2 = generate_sample_submission_thpt_2025(
        sbd="000012", exam_code="101",
        p1_answers=ans_p1_chau, p2_answers=ans_p2_chau, p3_answers=ans_p3_chau,
        student_name="Hoang Minh Chau"
    )
    imwrite_utf8(os.path.join(sample_dir, "102_HoangMinhC_THPT.png"), s_thpt_2)

    # Thí sinh 3: Vũ Thị Dung (SBD: 000013, Mã đề: 101) - Điểm trung bình (Phần III bỏ trống câu 5, 6)
    ans_p1_dung = dict(key_thpt_p1)
    ans_p1_dung[2] = 'A'; ans_p1_dung[5] = 'C'; ans_p1_dung[9] = 'D'
    ans_p2_dung = {
        1: {'a': 'S', 'b': 'S', 'c': 'Đ', 'd': 'S'},
        2: {'a': 'S', 'b': 'S', 'c': 'S', 'd': 'Đ'},
        3: {'a': 'S', 'b': 'Đ', 'c': 'Đ', 'd': 'S'},
        4: {'a': 'S', 'b': 'S', 'c': 'Đ', 'd': 'Đ'}
    }
    ans_p3_dung = {1: "15", 2: "-2.5", 3: "0.75", 4: "120"} # bỏ trống 5 và 6
    s_thpt_3 = generate_sample_submission_thpt_2025(
        sbd="000013", exam_code="101",
        p1_answers=ans_p1_dung, p2_answers=ans_p2_dung, p3_answers=ans_p3_dung,
        student_name="Vu Thi Dung"
    )
    imwrite_utf8(os.path.join(sample_dir, "103_VuThiD_THPT.png"), s_thpt_3)

    # Ảnh chụp điện thoại thực tế của bài THPT (góc chụp nghiêng, nền bàn học, bóng đổ)
    photo_thpt_1 = simulate_camera_photo(s_thpt_1, angle=2.8, shadow=True)
    imwrite_utf8(os.path.join(sample_dir, "photo_101_TranThiB_ChupNghieng.jpg"), photo_thpt_1)
    # Giữ lại tên cũ để tương thích với các lệnh test cũ
    imwrite_utf8(os.path.join(sample_dir, "photo_test_thpt.jpg"), photo_thpt_1)

    print("Da sinh day du bo anh test mau cho ca 2 che do va anh chup dien thoai!")
