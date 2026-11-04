"""
Module: sheet_generator.py
Tạo phiếu FormTHPT50 từ layout PDF và các bài làm mẫu của giáo viên
và sinh tập dữ liệu bài làm mẫu có tô bút chì thực tế để thử nghiệm hệ thống.
"""

import os
import sys
import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.cv_utils import imread_utf8, imwrite_utf8
from core.layouts import load_layout

ACTIVE_LAYOUT = load_layout()
CANVAS_WIDTH = int(ACTIVE_LAYOUT["canvas_w"])
CANVAS_HEIGHT = int(ACTIVE_LAYOUT["canvas_h"])
LAYOUT_BASE_IMAGE = os.path.join(PROJECT_ROOT, "templates", "layouts", "thpt50_base.png")


def create_blank_canvas() -> np.ndarray:
    """Load a clean copy of the active THPT50 PDF sheet."""
    img = imread_utf8(LAYOUT_BASE_IMAGE)
    if img is None:
        raise FileNotFoundError(
            f"Missing THPT50 base sheet at {LAYOUT_BASE_IMAGE}; rebuild it from the supplied PDF."
        )
    return img


def generate_50_mcq_template(
    student_name: str = "", 
    sbd: str = "", 
    exam_code: str = ""
) -> np.ndarray:
    """Render a blank copy of the active THPT50 PDF sheet."""
    return create_blank_canvas()


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

    def fill_digit_block(block_id: str, value: str) -> None:
        block = ACTIVE_LAYOUT["id_blocks"][block_id]
        if not value:
            return
        text = f"{value:>0{block['columns']}}"[-block["columns"]:]
        for column, digit in zip(block["columns_data"], text):
            if digit.isdigit():
                bubble = column["digits"][int(digit)]
                fill_bubble(
                    img,
                    int(round(bubble["x"])),
                    int(round(bubble["y"])),
                    radius=max(4, int(round(block["radius"] * 0.75))),
                )

    fill_digit_block("student_id", sbd or "")
    fill_digit_block("exam_code", exam_code or "")

    active_answers = answers or {}
    for q_num, ans in active_answers.items():
        if not ans or q_num not in range(1, int(ACTIVE_LAYOUT["capacity"]) + 1):
            continue
        block = next(
            block
            for block in ACTIVE_LAYOUT["blocks"]
            if block["first_question"] <= q_num < block["first_question"] + block["rows"]
        )
        row = block["questions"][q_num - block["first_question"]]
        selected = [ans] if isinstance(ans, str) else ans if isinstance(ans, (list, tuple)) else []
        for option in selected:
            if option not in row["options"]:
                continue
            point = row["options"][option]
            fill_bubble(
                img,
                int(round(point["x"])),
                int(round(point["y"])),
                radius=max(5, int(round(block["radius"] * 0.72))),
            )

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


def generate_templates():
    """Generate the active THPT50 blank sheet and teacher answer-key sheet."""
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

    print("Đã tạo mẫu phiếu trắng và phiếu đáp án giáo viên thành công!")


if __name__ == "__main__":
    generate_templates()
