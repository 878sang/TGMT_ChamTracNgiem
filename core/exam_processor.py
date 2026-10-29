"""
Module: exam_processor.py
Cầu nối tổng hợp kết nối toàn bộ chuỗi xử lý:
  Ảnh chụp bài làm -> Align (Warp) -> OMR Extract -> Grade -> Visualize -> Submission Object
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import cv2
from typing import Tuple, Optional
from core.models import Exam, Submission, ExamMode
from core.cv_utils import imread_utf8, imwrite_utf8
from core.image_alignment import align_paper
from core.omr_extractor import extract_all_data
from core.grading_engine import grade_full_mcq, grade_thpt_2025
from core.visualizer import draw_grading_overlay
from core.ocr_engine import extract_header_info_ocr
from core.student_roster_handler import lookup_student_in_roster


ANNOTATED_DIR = "d:/Thị giác máy tính/Đồ Án/data/annotated"


def process_single_submission(
    image_path: str, 
    exam: Exam, 
    student_id_override: str = "",
    student_name_override: str = ""
) -> Submission:
    """
    Xử lý chấm trọn gói một bài thi từ đường dẫn ảnh chụp.
    Kết hợp: Căn chỉnh ảnh -> Bóc tách OMR -> Nhận diện OCR -> Đối chiếu DS Excel -> Chấm điểm
    """
    os.makedirs(ANNOTATED_DIR, exist_ok=True)
    filename = os.path.basename(image_path)
    base_id = os.path.splitext(filename)[0]

    submission = Submission(
        submission_id=f"sub_{base_id}",
        exam_id=exam.exam_id,
        image_path=image_path,
        student_id=student_id_override,
        student_name=student_name_override
    )

    # 1. Căn chỉnh ảnh (Perspective Transform)
    success, aligned, msg = align_paper(image_path)
    if not success or aligned is None:
        submission.status = "Lỗi"
        submission.error_message = msg
        return submission

    # 2. Bóc tách OMR & Nhận diện OCR
    try:
        extracted = extract_all_data(aligned, mode=exam.mode)
        submission.extracted_data = extracted
        
        # Nhận diện OCR trực tiếp từ khung tiêu đề phiếu thi (Họ tên, SBD)
        ocr_info = extract_header_info_ocr(aligned)
        submission.ocr_data = ocr_info

        detected_sbd = extracted.get("sbd", "000")
        detected_code = extracted.get("exam_code", "101")

        if not submission.student_id:
            submission.student_id = detected_sbd
        submission.exam_code = detected_code
        submission.needs_review = extracted.get("needs_review", False)

        # 3. Xác định Họ và tên thí sinh đa tầng (Multi-tier resolution):
        # Tầng 1 (Ưu tiên hàng đầu): Khớp nối SBD với Danh sách học sinh Excel của kỳ thi
        roster_name, roster_cls = lookup_student_in_roster(detected_sbd, getattr(exam, "student_roster", {}))
        
        if roster_name:
            submission.student_name = roster_name
        # Tầng 2: Nhận diện OCR chữ viết/in từ khung 'Ho va ten' trên phiếu
        elif ocr_info.get("name"):
            submission.student_name = ocr_info["name"]
        # Tầng 3: Tên từ override (nếu có, ví dụ từ tên file)
        elif student_name_override:
            submission.student_name = student_name_override
        # Tầng 4: Mặc định theo SBD đã quét
        elif not submission.student_name:
            submission.student_name = f"Thí sinh SBD {detected_sbd}"

        # 3. Lấy Key đáp án tương ứng với Mã đề
        # Nếu không có mã đề khớp, lấy key đầu tiên có trong bài kiểm tra
        available_keys = exam.answer_keys
        active_key = available_keys.get(detected_code)
        if not active_key and available_keys:
            active_key = list(available_keys.values())[0]

        if not active_key:
            submission.status = "Lỗi"
            submission.error_message = f"Chưa có đáp án cho mã đề {detected_code}!"
            return submission

        # 4. Chấm điểm theo chế độ
        if exam.mode == ExamMode.FULL_MCQ:
            grade_result = grade_full_mcq(
                student_answers=extracted.get("answers", {}),
                answer_key=active_key,
                max_score=exam.max_score
            )
            submission.total_score = grade_result["score"]
            submission.correct_count = grade_result["correct_count"]
            submission.wrong_count = grade_result["wrong_count"]
            submission.blank_count = grade_result["blank_count"]
        else:
            grade_result = grade_thpt_2025(
                student_data=extracted,
                answer_key=active_key
            )
            submission.score_part1 = grade_result["score_part1"]
            submission.score_part2 = grade_result["score_part2"]
            submission.score_part3 = grade_result["score_part3"]
            submission.total_score = grade_result["total_score"]
            submission.correct_count = grade_result["p1_correct"] + grade_result["p3_correct"]

        # 5. Vẽ trực quan kết quả chấm lên ảnh
        annotated_img = draw_grading_overlay(
            aligned_img=aligned,
            mode=exam.mode,
            extracted_data=extracted,
            answer_key=active_key,
            score_info=grade_result
        )

        annotated_path = os.path.join(ANNOTATED_DIR, f"result_{filename}")
        imwrite_utf8(annotated_path, annotated_img)
        submission.annotated_image_path = annotated_path

        # 6. Gán trạng thái
        if submission.needs_review:
            submission.status = "Cần kiểm tra"
        else:
            submission.status = "Đã chấm"

        return submission

    except Exception as e:
        submission.status = "Lỗi"
        submission.error_message = f"Lỗi xử lý thuật toán: {str(e)}"
        return submission
