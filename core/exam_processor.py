"""
Module: exam_processor.py
Cầu nối xử lý trọn gói quy trình Thị giác máy tính cho phiếu FormTHPT50:
  Ảnh chụp phiếu -> Căn chỉnh Warp -> Đọc phiếu -> Chấm điểm -> Vẽ Overlay -> Submission Object
"""

import os
import sys
import re
import cv2
import numpy as np
from typing import Dict, Optional, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.models import Submission
from core.cv_utils import imread_utf8, imwrite_utf8
from core.image_alignment import align_paper
from core.omr_extractor import extract_all_data
from core.grading_engine import grade_submission
from core.visualizer import draw_grading_overlay, remove_grading_overlay

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
    annotated_dir: str = "",
    total_questions: Optional[int] = None
) -> Submission:
    """
    Xử lý trọn gói 1 bài thi có từ 1 đến 50 câu từ file ảnh:
      1. Kiểm tra tính hợp lệ file
      2. Nắn phẳng phối cảnh theo canvas FormTHPT50
      3. Đọc số câu đã chọn trên lưới OMR FormTHPT50
      4. Chấm điểm so với đáp án chuẩn
      5. Vẽ overlay trực quan và lưu ảnh kết quả
    """
    save_dir = annotated_dir if annotated_dir else DEFAULT_ANNOTATED_DIR
    os.makedirs(save_dir, exist_ok=True)

    filename = os.path.basename(image_path)
    base_id, student_name = parse_student_info_from_filename(filename)

    submission = Submission(
        submission_id=f"sub_{base_id}",
        # Student ID must come from the SBD bubbles on the sheet.  The file
        # name is kept only for the internal submission ID and optional name.
        student_id="",
        student_name=student_name,
        image_path=image_path
    )
    question_count = (
        total_questions
        if total_questions is not None
        else len(answer_key) or 50
    )
    if not 1 <= question_count <= 50:
        submission.status = "Lỗi"
        submission.error_message = "Số câu phải nằm trong khoảng từ 1 đến 50."
        return submission
    if len(answer_key) != question_count or any(
        q not in answer_key for q in range(1, question_count + 1)
    ):
        submission.status = "Lỗi"
        submission.error_message = f"Đáp án chuẩn phải có đủ {question_count} câu."
        return submission

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

        processed_dir = os.path.join(os.path.dirname(save_dir), "processed")
        os.makedirs(processed_dir, exist_ok=True)
        processed_path = os.path.join(
            processed_dir, f"aligned_{os.path.splitext(filename)[0]}.png"
        )
        if not imwrite_utf8(processed_path, aligned):
            submission.status = "Lỗi"
            submission.error_message = (
                f"Không thể lưu ảnh đã cắt và căn phẳng: {processed_path}"
            )
            return submission
        submission.processed_image_path = processed_path
    except Exception as e:
        submission.status = "Lỗi"
        submission.error_message = f"Lỗi tiền xử lý ảnh: {str(e)}"
        return submission

    # Tự động dò tìm và bóc tách đáp án
    try:
        omr_data = extract_all_data(aligned, total_questions=question_count)
        clean_aligned = remove_grading_overlay(aligned)
        if not np.array_equal(clean_aligned, aligned):
            coords_map = omr_data.get("coords_map")
            if coords_map:
                omr_data = extract_all_data(
                    clean_aligned,
                    total_questions=question_count,
                    known_coords_map=coords_map,
                    known_layout_source=omr_data.get("layout_source", ""),
                )
            else:
                omr_data = extract_all_data(
                    clean_aligned,
                    total_questions=question_count,
                )
            aligned = clean_aligned
        if omr_data.get("layout_source") in ("unrecognized", "question_count_mismatch"):
            submission.status = "Lỗi"
            submission.error_message = omr_data.get(
                "warning_message",
                "Không thể nhận diện bố cục phiếu để chấm chính xác.",
            )
            return submission
        submission.answers = omr_data.get("answers", {})
        
        detected_sbd = omr_data.get("sbd", "")
        submission.sbd = detected_sbd
        if detected_sbd and "?" not in detected_sbd and detected_sbd.isdigit():
            submission.student_id = detected_sbd
        else:
            # Never use the image filename as a student ID when SBD reading
            # fails or is ambiguous.
            submission.student_id = ""
            
        submission.exam_code = omr_data.get("exam_code", "")
        submission.needs_review = omr_data.get("needs_review", False)
        submission.warning_message = omr_data.get("warning_message", "")
        coords_map = omr_data.get("coords_map")
    except Exception as e:
        submission.status = "Lỗi"
        submission.error_message = f"Lỗi nhận diện OMR: {str(e)}"
        return submission

    # Chấm điểm tự động
    try:
        grading = grade_submission(submission.answers, answer_key, total_questions=question_count)
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


