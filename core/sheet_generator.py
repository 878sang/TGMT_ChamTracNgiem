"""
Module: sheet_generator.py
Tạo mẫu phiếu trắc nghiệm chuẩn 50 câu (A4 - 1200x1700 px), phiếu đáp án mẫu của giáo viên
và sinh tập dữ liệu bài làm mẫu có tô bút chì thực tế để thử nghiệm hệ thống.
"""

import os
import sys
import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.cv_utils import imwrite_utf8

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 1700
MARKER_SIZE = 50
MARGIN = 40

MARKER_TL = (MARGIN, MARGIN)
MARKER_TR = (CANVAS_WIDTH - MARGIN - MARKER_SIZE, MARGIN)
MARKER_BL = (MARGIN, CANVAS_HEIGHT - MARGIN - MARKER_SIZE)
MARKER_BR = (CANVAS_WIDTH - MARGIN - MARKER_SIZE, CANVAS_HEIGHT - MARGIN - MARKER_SIZE)


def create_blank_canvas() -> np.ndarray:
    """Tạo tờ giấy trắng 1200x1700 px và vẽ 4 Marker vuông màu đen đặc ở 4 góc"""
    img = np.ones((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8) * 255

    for (mx, my) in [MARKER_TL, MARKER_TR, MARKER_BL, MARKER_BR]:
        cv2.rectangle(img, (mx, my), (mx + MARKER_SIZE, my + MARKER_SIZE), (0, 0, 0), -1)

    cv2.rectangle(img, (MARGIN + 5, MARGIN + 5), 
                  (CANVAS_WIDTH - MARGIN - 5, CANVAS_HEIGHT - MARGIN - 5), (140, 140, 140), 2)
    return img


def draw_header_section(
    img: np.ndarray, 
    title: str = "PHIẾU TRẢ LỜI TRẮC NGHIỆM THPT (50 CÂU)", 
    student_name: str = "",
    sbd: str = "",
    exam_code: str = ""
) -> None:
    """Vẽ phần tiêu đề bài thi, khung thông tin thí sinh, khung SBD & Mã đề"""
    cv2.putText(img, "BO GIAO DUC VA DAO TAO", (120, 65), cv2.FONT_HERSHEY_DUPLEX, 0.65, (60, 60, 60), 1)
    cv2.putText(img, title, (120, 105), cv2.FONT_HERSHEY_DUPLEX, 0.85, (0, 0, 120), 2)

    # Khung Họ tên và Lớp
    cv2.rectangle(img, (120, 125), (600, 165), (80, 80, 80), 1)
    cv2.putText(img, "Ho va ten:", (128, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 1)
    if student_name:
        cv2.putText(img, str(student_name).upper(), (235, 152), cv2.FONT_HERSHEY_DUPLEX, 0.60, (0, 0, 100), 2)

    cv2.rectangle(img, (620, 125), (860, 165), (80, 80, 80), 1)
    cv2.putText(img, "Lop: ..............", (630, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 1)

    # Khung Số Báo Danh (6 cột x 10 hàng)
    cv2.rectangle(img, (120, 180), (540, 460), (0, 0, 0), 2)
    cv2.putText(img, "SO BAO DANH", (240, 202), cv2.FONT_HERSHEY_DUPLEX, 0.60, (0, 0, 0), 1)
    sbd_str = f"{sbd:>06}"[:6] if sbd else ""
    for col in range(6):
        cx = 155 + col * 65
        cv2.rectangle(img, (cx - 16, 210), (cx + 16, 232), (100, 100, 100), 1)
        if sbd_str and col < len(sbd_str) and sbd_str[col].isdigit():
            cv2.putText(img, sbd_str[col], (cx - 6, 227), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 120), 1)

        for row in range(10):
            cy = 245 + row * 20
            cv2.circle(img, (cx, cy), 8, (120, 120, 120), 1)
            cv2.putText(img, str(row), (cx - 4, cy + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (80, 80, 80), 1)

    # Khung Mã Đề Thi (3 cột x 10 hàng)
    cv2.rectangle(img, (570, 180), (790, 460), (0, 0, 0), 2)
    cv2.putText(img, "MA DE", (640, 202), cv2.FONT_HERSHEY_DUPLEX, 0.60, (0, 0, 0), 1)
    code_str = f"{exam_code:>03}"[:3] if exam_code else ""
    for col in range(3):
        cx = 605 + col * 65
        cv2.rectangle(img, (cx - 16, 210), (cx + 16, 232), (100, 100, 100), 1)
        if code_str and col < len(code_str) and code_str[col].isdigit():
            cv2.putText(img, code_str[col], (cx - 6, 227), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 120), 1)

        for row in range(10):
            cy = 245 + row * 20
            cv2.circle(img, (cx, cy), 8, (120, 120, 120), 1)
            cv2.putText(img, str(row), (cx - 4, cy + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (80, 80, 80), 1)

    # Khung Hướng dẫn tô
    cv2.rectangle(img, (820, 180), (1090, 460), (100, 100, 100), 1)
    cv2.putText(img, "HUONG DAN TO", (860, 210), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 0, 0), 1)
    cv2.circle(img, (860, 255), 10, (40, 40, 40), -1)
    cv2.putText(img, "Dung (To den kin)", (885, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 120, 0), 1)
    cv2.circle(img, (860, 305), 10, (100, 100, 100), 1)
    cv2.line(img, (852, 297), (868, 313), (0, 0, 200), 2)
    cv2.putText(img, "Sai (Gach cheo)", (885, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 200), 1)


def generate_50_mcq_template(
    student_name: str = "", 
    sbd: str = "", 
    exam_code: str = ""
) -> np.ndarray:
    """Tạo mẫu phiếu thi trắc nghiệm 50 câu chuẩn 1200x1700 (2 cột x 25 câu)"""
    img = create_blank_canvas()
    draw_header_section(
        img, 
        title="PHIEU TRA LOI TRAC NGHIEM THPT (50 CAU)",
        student_name=student_name, 
        sbd=sbd, 
        exam_code=exam_code
    )

    options = ['A', 'B', 'C', 'D']
    cv2.putText(img, "PHAN TRA LOI (50 CAU HOI - 4 LUA CHON)", (350, 495), cv2.FONT_HERSHEY_DUPLEX, 0.70, (0, 0, 120), 2)

    for col_idx, start_q in enumerate([1, 26]):
        base_x = 110 if col_idx == 0 else 640
        cv2.rectangle(img, (base_x - 10, 515), (base_x + 440, 1575), (0, 0, 0), 2)
        cv2.putText(img, "Cau", (base_x + 10, 545), cv2.FONT_HERSHEY_DUPLEX, 0.60, (0, 0, 0), 1)
        for o_idx, opt in enumerate(options):
            cv2.putText(img, opt, (base_x + 125 + o_idx * 75, 545), cv2.FONT_HERSHEY_DUPLEX, 0.60, (0, 0, 0), 1)
        cv2.line(img, (base_x - 10, 558), (base_x + 440, 558), (0, 0, 0), 2)

        for q in range(25):
            q_num = start_q + q
            y = 585 + q * 39
            cv2.putText(img, f"{q_num:02d}", (base_x + 8, y + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 1)
            for o_idx in range(4):
                bx = base_x + 130 + o_idx * 75
                cv2.circle(img, (bx, y), 12, (100, 100, 100), 2)
                cv2.putText(img, options[o_idx], (bx - 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (120, 120, 120), 1)
            cv2.line(img, (base_x - 10, y + 19), (base_x + 440, y + 19), (225, 225, 225), 1)

    return img


def fill_bubble(img: np.ndarray, center_x: int, center_y: int, radius: int = 11, intensity: int = 35) -> None:
    """Tô chì vào ô tròn mô phỏng bút chì 2B thực tế"""
    cv2.circle(img, (center_x, center_y), radius - 1, (intensity, intensity, intensity), -1)
    cv2.circle(img, (center_x, center_y), radius, (intensity + 35, intensity + 35, intensity + 35), 1)


def generate_sample_submission_50_mcq(
    student_id: str = "HS001",
    student_name: str = "Nguyen Van A",
    exam_code: str = "101",
    answers: dict = None,
    sbd: str = "000001"
) -> np.ndarray:
    """Sinh ảnh bài làm mẫu 50 câu đã tô chì"""
    img = generate_50_mcq_template(student_name=student_name, sbd=sbd, exam_code=exam_code)

    sbd_str = f"{sbd:>06}"[:6]
    for col, digit in enumerate(sbd_str):
        if digit.isdigit():
            row = int(digit)
            fill_bubble(img, 155 + col * 65, 245 + row * 20, radius=7)

    code_str = f"{exam_code:>03}"[:3]
    for col, digit in enumerate(code_str):
        if digit.isdigit():
            row = int(digit)
            fill_bubble(img, 605 + col * 65, 245 + row * 20, radius=7)

    opt_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    active_answers = answers or {}

    for q_num, ans in active_answers.items():
        if not ans:
            continue
        if q_num <= 25:
            base_x = 110
            q_in_col = q_num - 1
        else:
            base_x = 640
            q_in_col = q_num - 26

        by = 585 + q_in_col * 39

        if isinstance(ans, str) and ans in opt_map:
            fill_bubble(img, base_x + 130 + opt_map[ans] * 75, by, radius=11)
        elif isinstance(ans, (list, tuple)):
            for a_item in ans:
                if a_item in opt_map:
                    fill_bubble(img, base_x + 130 + opt_map[a_item] * 75, by, radius=11)

    return img


def add_perspective_and_noise(img: np.ndarray, angle_deg: float = 8.0) -> np.ndarray:
    """Tạo hiệu ứng ảnh chụp từ camera điện thoại bị lệch góc"""
    h, w = img.shape[:2]
    bg_h, bg_w = int(h * 1.25), int(w * 1.25)
    bg = np.ones((bg_h, bg_w, 3), dtype=np.uint8) * 190

    src_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    pad_x = 120
    pad_y = 120
    dst_pts = np.float32([
        [pad_x + 40, pad_y + 30],
        [pad_x + w - 30, pad_y + 10],
        [pad_x + w + 20, pad_y + h - 20],
        [pad_x - 20, pad_y + h + 15]
    ])

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(img, matrix, (bg_w, bg_h), borderValue=(190, 190, 190))
    gradient = np.linspace(0.85, 1.05, bg_w)
    gradient = np.tile(gradient, (bg_h, 1))
    warped_float = warped.astype(np.float32) * gradient[:, :, np.newaxis]
    return np.clip(warped_float, 0, 255).astype(np.uint8)


def generate_all_samples():
    """Tạo mẫu phiếu trắng 50 câu, phiếu đáp án mẫu giáo viên và 7 bài làm mẫu"""
    template_dir = os.path.join(PROJECT_ROOT, "templates")
    os.makedirs(template_dir, exist_ok=True)

    # 1. Phiếu trắng 50 câu
    blank_template = generate_50_mcq_template()
    imwrite_utf8(os.path.join(template_dir, "phieu_50_cau_chuan.png"), blank_template)

    # Đáp án chuẩn đề demo (50 câu)
    standard_key = {i: ['A', 'B', 'C', 'D'][(i * 3 + 1) % 4] for i in range(1, 51)}

    # 2. Phiếu đáp án mẫu của giáo viên (tô sẵn 50 câu để test tính năng tự dò đáp án từ ảnh)
    img_teacher_key = generate_sample_submission_50_mcq("GV01", "GIAO VIEN (DAP AN CHUAN)", "101", standard_key, "999999")
    imwrite_utf8(os.path.join(template_dir, "phieu_dap_an_mau_giao_vien.png"), img_teacher_key)

    # 3. Thư mục dataset 50 câu
    dataset_dir = os.path.join(PROJECT_ROOT, "dataset", "sample_submissions_50cau")
    os.makedirs(dataset_dir, exist_ok=True)

    # HS001 (10.0đ)
    img1 = generate_sample_submission_50_mcq("HS001", "Nguyen Van A", "101", standard_key, "000001")
    imwrite_utf8(os.path.join(dataset_dir, "HS001_NguyenVanA.png"), img1)

    # HS002 (8.0đ)
    ans2 = dict(standard_key)
    for q in [5, 12, 18, 25, 30, 36, 42, 48, 49, 50]:
        ans2[q] = 'A' if standard_key[q] != 'A' else 'B'
    img2 = generate_sample_submission_50_mcq("HS002", "Tran Thi B", "101", ans2, "000002")
    imwrite_utf8(os.path.join(dataset_dir, "HS002_TranThiB.png"), img2)

    # HS003 (Bỏ trống)
    ans3 = dict(standard_key)
    for q in [3, 8, 15, 27, 33, 44]:
        ans3[q] = None
    img3 = generate_sample_submission_50_mcq("HS003", "Le Van C", "101", ans3, "000003")
    imwrite_utf8(os.path.join(dataset_dir, "HS003_LeVanC_BoTrong.png"), img3)

    # HS004 (Tô trùng)
    ans4 = dict(standard_key)
    ans4[10] = ['A', 'B']
    ans4[22] = ['C', 'D']
    ans4[39] = ['A', 'C']
    img4 = generate_sample_submission_50_mcq("HS004", "Pham Thi D", "101", ans4, "000004")
    imwrite_utf8(os.path.join(dataset_dir, "HS004_PhamThiD_ToTrung.png"), img4)

    # HS005 (Chụp nghiêng)
    img5_skewed = add_perspective_and_noise(img1.copy(), angle_deg=10.0)
    imwrite_utf8(os.path.join(dataset_dir, "HS005_HoangVanE_ChupNghieng.jpg"), img5_skewed)

    # HS006 (Điểm trung bình)
    ans6 = {i: ['B', 'C', 'D', 'A'][i % 4] for i in range(1, 51)}
    img6 = generate_sample_submission_50_mcq("HS006", "Dang Thi F", "101", ans6, "000006")
    imwrite_utf8(os.path.join(dataset_dir, "HS006_DangThiF.png"), img6)

    # HS007 (Ảnh lỗi khuyết góc)
    img7 = img1.copy()
    img7[0:200, 0:200] = 255
    img7[0:200, 1000:1200] = 255
    imwrite_utf8(os.path.join(dataset_dir, "HS007_LoiMatGoc.png"), img7)

    print("Đã tạo mẫu phiếu trắng và bộ ảnh mẫu 50 câu thành công!")


if __name__ == "__main__":
    generate_all_samples()
