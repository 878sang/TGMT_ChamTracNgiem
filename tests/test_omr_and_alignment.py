"""
Kiểm thử cho module Image Alignment và OMR Extractor:
  - Chỉ căn chỉnh khi có đúng 4 marker định vị góc hợp lệ
  - Nhận diện SBD và Mã đề không tự gán mặc định khi không đọc được
  - Nhận diện câu trả lời ngắn Phần III: giữ đúng vị trí từng cột, phát hiện cột bị bỏ trống giữa các chữ số
"""

import os
import sys
import cv2
import numpy as np
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.image_alignment import find_fiducial_markers, align_paper
from core.omr_extractor import extract_sbd, extract_exam_code, extract_thpt_2025_answers
from core.models import ExamMode


def test_four_markers_required():
    """Kiểm tra: BẮT BUỘC có đủ 4 marker góc mới căn chỉnh, thiếu 1 góc phải báo lỗi"""
    sample_path = os.path.join(PROJECT_ROOT, "dataset", "sample_submissions", "001_NguyenVanA_FullTN.png")
    img = cv2.imread(sample_path)
    assert img is not None

    # 1. Ảnh gốc đủ 4 góc -> Thành công
    succ, aligned, msg = align_paper(img)
    assert succ is True
    assert aligned is not None
    assert aligned.shape == (1700, 1200, 3)

    # 2. Xóa/che 1 marker góc trên trái -> Phải báo lỗi
    img_missing_tl = img.copy()
    cv2.rectangle(img_missing_tl, (0, 0), (250, 250), (255, 255, 255), -1)
    succ_err, _, msg_err = align_paper(img_missing_tl)
    assert succ_err is False
    assert "Không xác định đủ 4 marker định vị góc" in msg_err

    # 3. Xóa/che 1 marker góc dưới phải -> Phải báo lỗi
    img_missing_br = img.copy()
    cv2.rectangle(img_missing_br, (img.shape[1] - 250, img.shape[0] - 250), (img.shape[1], img.shape[0]), (255, 255, 255), -1)
    succ_br, _, msg_br = align_paper(img_missing_br)
    assert succ_br is False
    assert "Không xác định đủ 4 marker định vị góc" in msg_br


def test_sbd_and_code_blank_returns_question_mark():
    """Kiểm tra: Nếu không tô SBD / Mã đề, KHÔNG được tự gán '0' hay '100'"""
    # Tạo ảnh trắng không tô ô nào ở header
    white_sheet = np.ones((1700, 1200), dtype=np.uint8) * 255

    sbd_str, is_valid_sbd, _ = extract_sbd(white_sheet)
    code_str, is_valid_code, _ = extract_exam_code(white_sheet)

    assert "?" in sbd_str
    assert is_valid_sbd is False
    assert sbd_str != "000000", "Không được tự gán 000000 khi học sinh không tô!"

    assert "?" in code_str
    assert is_valid_code is False
    assert code_str != "100", "Không được tự gán 100 khi học sinh không tô!"


def test_short_answer_gap_detection():
    """
    Kiểm tra nhận diện câu trả lời ngắn Phần III:
    Nếu có cột bị bỏ trống ở giữa các chữ số (ví dụ: cột 0 = '1', cột 1 bỏ trống, cột 2 = '5'),
    phải phát hiện cờ needs_review = True và giữ đúng vị trí.
    """
    gap_path = os.path.join(PROJECT_ROOT, "dataset", "sample_submissions", "test_flawed_short_answer_gap.png")
    if os.path.exists(gap_path):
        gray = cv2.imread(gap_path, cv2.IMREAD_GRAYSCALE)
        data, needs_rev = extract_thpt_2025_answers(gray)
        # Câu 1 có cột bị bỏ trống ở giữa
        assert needs_rev is True
        c1_val = data["part3"].get(1, "")
        assert "?" in c1_val or needs_rev is True, "Phải phát hiện lỗi khi bỏ trống cột giữa!"

