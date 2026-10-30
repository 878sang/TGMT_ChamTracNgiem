"""
Module: exam_processor.py
Cầu nối xử lý trọn gói quy trình Thị giác máy tính cho bài thi 50 câu:
  Ảnh chụp phiếu -> Căn chỉnh Warp -> Tự động dò ma trận 50 câu -> Chấm điểm -> Vẽ Overlay -> Submission Object
Hỗ trợ chức năng tự động dò tìm đáp án chuẩn từ ảnh phiếu mẫu (Scan Master Sheet).
"""

import os
import sys
import re
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.models import Submission
from core.cv_utils import imread_utf8, imwrite_utf8
from core.image_alignment import align_paper
from core.omr_extractor import extract_all_data
from core.grading_engine import grade_submission
from core.visualizer import draw_grading_overlay

DEFAULT_ANNOTATED_DIR = os.path.join(PROJECT_ROOT, "data", "annotated")


def parse_student_info_from_filename(filename: str) -> Tuple[str, str]:
    """Tách Mã học sinh và Họ tên từ tên file ảnh (VD: 'HS001.jpg' -> 'HS001')"""
    base = os.path.splitext(os.path.basename(filename))[0]
    parts = base.split("_")
    
    if len(parts) >= 2:
        student_id = parts[0]
        raw_name = "_".join(parts[1:])
        name = re.sub(r'(?<!^)(?=[A-Z])', ' ', raw_name)
        return student_id, name
    else:
        return base, ""


def process_single_submission(
    image_path: str,
    answer_key: Dict[int, str],
    annotated_dir: str = ""
) -> Submission:
    """
    Xử lý trọn gói 1 bài thi 50 câu từ file ảnh:
      1. Kiểm tra tính hợp lệ file
      2. Nắn phẳng phối cảnh 1200x1700 (Perspective Transform)
      3. Tự động dò tìm ma trận 50 câu (OMR Dynamic Detection)
      4. Chấm điểm so với đáp án chuẩn (mỗi câu 0.2đ)
      5. Vẽ overlay trực quan và lưu ảnh kết quả
    """
    save_dir = annotated_dir if annotated_dir else DEFAULT_ANNOTATED_DIR
    os.makedirs(save_dir, exist_ok=True)

    filename = os.path.basename(image_path)
    base_id, student_name = parse_student_info_from_filename(filename)

    submission = Submission(
        submission_id=f"sub_{base_id}",
        student_id=base_id,
        student_name=student_name,
        image_path=image_path
    )

    if not os.path.exists(image_path):
        submission.status = "Lỗi"
        submission.error_message = "File ảnh không tồn tại trên đĩa."
        return submission

    # Căn chỉnh nắn phẳng (Perspective Transform)
    try:
        success, aligned, msg = align_paper(image_path)
        if not success or aligned is None:
            submission.status = "Lỗi"
            submission.error_message = msg
            return submission
    except Exception as e:
        submission.status = "Lỗi"
        submission.error_message = f"Lỗi tiền xử lý ảnh: {str(e)}"
        return submission

    # Tự động dò tìm và bóc tách đáp án 50 câu
    try:
        omr_data = extract_all_data(aligned)
        submission.answers = omr_data.get("answers", {})
        
        detected_sbd = omr_data.get("sbd", "")
        if detected_sbd and "?" not in detected_sbd:
            submission.student_id = detected_sbd
            
        submission.exam_code = omr_data.get("exam_code", "101")
        submission.needs_review = omr_data.get("needs_review", False)
        submission.warning_message = omr_data.get("warning_message", "")
        coords_map = omr_data.get("coords_map")
    except Exception as e:
        submission.status = "Lỗi"
        submission.error_message = f"Lỗi nhận diện OMR: {str(e)}"
        return submission

    # Chấm điểm tự động 50 câu
    try:
        grading = grade_submission(submission.answers, answer_key, total_questions=50)
        submission.score = grading.get("score", 0.0)
        submission.correct_count = grading.get("correct_count", 0)
        submission.wrong_count = grading.get("wrong_count", 0)
        submission.blank_count = grading.get("blank_count", 0)
        submission.multiple_count = grading.get("multiple_count", 0)
        submission.details = grading.get("details", {})

        if submission.needs_review or submission.multiple_count > 0:
            submission.status = "Cảnh báo"
        else:
            submission.status = "Thành công"
    except Exception as e:
        submission.status = "Lỗi"
        submission.error_message = f"Lỗi chấm điểm: {str(e)}"
        return submission

    # Vẽ overlay trực quan và lưu ảnh kết quả
    try:
        annotated_img = draw_grading_overlay(
            aligned_img=aligned,
            student_answers=submission.answers,
            answer_key=answer_key,
            score_info=grading,
            student_id=submission.student_id,
            coords_map=coords_map
        )
        out_name = f"result_{os.path.splitext(filename)[0]}.png"
        out_path = os.path.join(save_dir, out_name)
        imwrite_utf8(out_path, annotated_img)
        submission.annotated_image_path = out_path
    except Exception as e:
        print(f"Lỗi vẽ ảnh overlay: {e}")

    return submission


def scan_answer_key_from_image(image_path: str) -> Tuple[bool, Dict[int, str], str]:
    """
    TỰ ĐỘNG DÒ ĐÁP ÁN CHUẨN TỪ ẢNH PHIẾU ĐÁP ÁN MẪU:
      Giáo viên chụp ảnh phiếu đã tô đáp án chuẩn -> Hệ thống tự dò tìm và đọc 50 câu!
    """
    if not os.path.exists(image_path):
        return False, {}, "File ảnh không tồn tại."

    success, aligned, msg = align_paper(image_path)
    if not success or aligned is None:
        return False, {}, f"Không thể căn chỉnh phiếu: {msg}"

    omr_data = extract_all_data(aligned)
    detected_answers = omr_data.get("answers", {})

    parsed_key = {}
    for q in range(1, 51):
        ans = detected_answers.get(q)
        if isinstance(ans, str) and ans in ['A', 'B', 'C', 'D']:
            parsed_key[q] = ans

    if len(parsed_key) < 5:
        return False, {}, "Không tìm thấy đủ đáp án được tô trên ảnh phiếu này."

    return True, parsed_key, f"Đã tự động dò tìm được {len(parsed_key)}/50 đáp án từ ảnh phiếu mẫu!"
