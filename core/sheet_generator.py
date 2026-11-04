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


def generate_templates():
    """Generate the blank sheet from the active FormTHPT50 layout."""
    template_dir = os.path.join(PROJECT_ROOT, "templates")
    os.makedirs(template_dir, exist_ok=True)

    # 1. Phiếu trắng 50 câu
    blank_template = generate_50_mcq_template()
    imwrite_utf8(os.path.join(template_dir, "phieu_50_cau_chuan.png"), blank_template)

    print("Đã tạo mẫu phiếu trắng FormTHPT50 thành công!")


if __name__ == "__main__":
    generate_templates()
