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


# Thư mục lưu ảnh chấm điểm mặc định (tương đối với thư mục dữ liệu của dự án)
from core.storage_manager import get_data_dir


def _get_annotated_dir() -> str:
    """Lấy thư mục lưu ảnh annotated từ thư mục data hiện tại (không hardcode)"""
    return os.path.join(get_data_dir(), "annotated")


ANNOTATED_DIR = os.path.join(PROJECT_ROOT, "data", "annotated")  # default fallback


def set_annotated_dir(custom_path: str):
    """Cho phép tùy biến thư mục lưu ảnh chấm điểm"""
    global ANNOTATED_DIR
    ANNOTATED_DIR = os.path.abspath(custom_path)
    annotated_dir = _get_annotated_dir()
    os.makedirs(annotated_dir, exist_ok=True)


def get_annotated_dir() -> str:
    return ANNOTATED_DIR


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
        num_q = getattr(exam, 'num_questions', 40)
        extracted = extract_all_data(aligned, mode=exam.mode, num_questions=num_q)
        submission.extracted_data = extracted
        
        # Nhận diện OCR trực tiếp từ khung tiêu đề phiếu thi (Họ tên, SBD)
        ocr_info = extract_header_info_ocr(aligned)
        submission.ocr_data = ocr_info

        detected_sbd = extracted.get("sbd", "???")
        detected_code = extracted.get("exam_code", "???")

        if not submission.student_id:
            submission.student_id = detected_sbd
        submission.exam_code = detected_code
        submission.needs_review = extracted.get("needs_review", False)

        # Cảnh báo header (SBD / Mã đề)
        warnings = []
        if not extracted.get("is_valid_sbd", True) or "?" in detected_sbd:
            warnings.append(f"SBD '{detected_sbd}' chưa tô rõ hoặc nghi vấn")
        if not extracted.get("is_valid_code", True) or "?" in detected_code:
            warnings.append(f"Mã đề '{detected_code}' chưa tô rõ hoặc nghi vấn")

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

        # 4. Lấy Key đáp án tương ứng với Mã đề
        # TUYỆT ĐỐI KHÔNG tự lấy đáp án mã đầu tiên nếu mã đề không khớp!
        available_keys = exam.answer_keys or {}
        active_key = available_keys.get(detected_code)

        if not active_key:
            submission.needs_review = True
            submission.total_score = 0.0
            if "?" in detected_code or not extracted.get("is_valid_code", True):
                submission.status = "Cần kiểm tra"
                submission.error_message = f"Mã đề '{detected_code}' không đọc được rõ ràng. Vui lòng xác nhận lại mã đề!"
            else:
                submission.status = "Cần kiểm tra"
                submission.error_message = f"Mã đề '{detected_code}' không tồn tại trong bộ đáp án của kỳ thi!"

            # Vẽ ảnh cảnh báo để giáo viên dễ đối chiếu khi xem lại bài
            annotated_canvas = aligned.copy()
            cv2.rectangle(annotated_canvas, (80, 15), (1120, 75), (0, 0, 200), -1)
            cv2.putText(
                annotated_canvas, 
                f"CAN KIEM TRA: MA DE '{detected_code}' KHONG HOP LE", 
                (100, 55), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2
            )
            annotated_path = os.path.join(annotated_dir, f"result_{filename}")
            imwrite_utf8(annotated_path, annotated_canvas)
            submission.annotated_image_path = annotated_path
            return submission

        # 5. Chấm điểm theo chế độ khi đã có key chuẩn xác
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

        # 6. Vẽ trực quan kết quả chấm lên ảnh
        annotated_img = draw_grading_overlay(
            aligned_img=aligned,
            mode=exam.mode,
            extracted_data=extracted,
            answer_key=active_key,
            score_info=grade_result
        )

        annotated_path = os.path.join(annotated_dir, f"result_{filename}")
        imwrite_utf8(annotated_path, annotated_img)
        submission.annotated_image_path = annotated_path

        # 7. Gán trạng thái và thông điệp cảnh báo
        if warnings:
            submission.needs_review = True
            submission.error_message = "; ".join(warnings)

        if submission.needs_review:
            submission.status = "Cần kiểm tra"
        else:
            submission.status = "Đã chấm"

        return submission

    except Exception as e:
        submission.status = "Lỗi"
        submission.error_message = f"Lỗi xử lý thuật toán: {str(e)}"
        return submission
