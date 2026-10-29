"""
Module: models.py
Định nghĩa cấu trúc dữ liệu cho Hệ thống chấm trắc nghiệm Đa năng
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import json
import time


class ExamMode:
    FULL_MCQ = "full_mcq"       # Chế độ 1: Trắc nghiệm 4 lựa chọn (20, 40, 50 câu)
    THPT_2025 = "thpt_2025"     # Chế độ 2: Chuẩn THPT mới BGD&ĐT (3 Phần)


@dataclass
class Exam:
    exam_id: str
    title: str
    subject: str = "Toán"
    class_name: str = "12A1"
    mode: str = ExamMode.FULL_MCQ
    num_questions: int = 40             # Áp dụng cho mode FULL_MCQ
    max_score: float = 10.0
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    # answer_keys: { "101": data, "102": data, ... }
    # Với FULL_MCQ: data = {1: 'A', 2: 'B', ...}
    # Với THPT_2025: data = {"part1": {1: 'A', ...}, "part2": {1: {'a':'Đ', ...}}, "part3": {1: '15', ...}}
    answer_keys: Dict[str, Any] = field(default_factory=dict)
    # Danh sách học sinh của kỳ thi: {"000001": {"name": "Nguyễn Văn An", "class": "12A1"}, ...}
    student_roster: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Exam':
        return cls(
            exam_id=data.get("exam_id", ""),
            title=data.get("title", ""),
            subject=data.get("subject", ""),
            class_name=data.get("class_name", ""),
            mode=data.get("mode", ExamMode.FULL_MCQ),
            num_questions=data.get("num_questions", 40),
            max_score=data.get("max_score", 10.0),
            created_at=data.get("created_at", ""),
            answer_keys=data.get("answer_keys", {}),
            student_roster=data.get("student_roster", {})
        )


@dataclass
class Submission:
    submission_id: str
    exam_id: str
    student_id: str = ""
    student_name: str = ""
    exam_code: str = "101"
    image_path: str = ""
    annotated_image_path: str = ""
    
    # Kết quả nhận diện OMR
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    # Kết quả nhận diện OCR (chữ viết tay / in)
    ocr_data: Dict[str, Any] = field(default_factory=dict)
    
    # Điểm thành phần
    score_part1: float = 0.0
    score_part2: float = 0.0
    score_part3: float = 0.0
    total_score: float = 0.0
    
    correct_count: int = 0
    wrong_count: int = 0
    blank_count: int = 0
    
    status: str = "Chưa chấm"     # "Đã chấm", "Cần kiểm tra", "Lỗi"
    needs_review: bool = False
    error_message: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Submission':
        # Chỉ giữ lại các trường hợp lệ của Submission
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)
