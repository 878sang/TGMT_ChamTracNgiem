"""
Module: models.py
Định nghĩa cấu trúc dữ liệu cho Hệ thống nhận diện và chấm trắc nghiệm THPT 50 câu.
Tinh giản, gọn gàng, tập trung đúng vào yêu cầu bài toán Thị giác máy tính.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import time


@dataclass
class Exam:
    """Thông tin đề thi và đáp án chuẩn 50 câu"""
    exam_id: str = "exam_50_cau"
    title: str = "Bài thi trắc nghiệm THPT - 50 câu"
    subject: str = "Toán / Khoa học"
    num_questions: int = 50
    max_score: float = 10.0
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    # answer_key: {1: 'A', 2: 'B', ..., 50: 'D'}
    answer_key: Dict[int, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Exam':
        # Chuyển đổi key của answer_key sang int
        key_data = data.get("answer_key", {})
        int_key = {int(k): str(v).upper() for k, v in key_data.items() if str(k).isdigit()}
        return cls(
            exam_id=data.get("exam_id", "exam_50_cau"),
            title=data.get("title", "Bài thi trắc nghiệm THPT - 50 câu"),
            subject=data.get("subject", "Toán / Khoa học"),
            num_questions=data.get("num_questions", 50),
            max_score=data.get("max_score", 10.0),
            created_at=data.get("created_at", ""),
            answer_key=int_key
        )


@dataclass
class Submission:
    """Kết quả xử lý và chấm điểm của một học sinh"""
    submission_id: str
    student_id: str = ""                # Mã học sinh (lấy từ tên file hoặc SBD)
    student_name: str = ""
    exam_code: str = "101"              # Mã đề thi (nếu có trên phiếu)
    image_path: str = ""                # Đường dẫn file ảnh gốc
    annotated_image_path: str = ""      # Đường dẫn ảnh đã vẽ overlay kết quả
    
    # Kết quả nhận diện OMR: {1: 'A', 2: 'B', 3: None (trống), 4: ['A', 'C'] (tô trùng)}
    answers: Dict[int, Any] = field(default_factory=dict)
    
    # Chi tiết chấm điểm từng câu: {1: {"student": 'A', "key": 'A', "is_correct": True}}
    details: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    
    # Điểm số và thống kê
    score: float = 0.0                  # Điểm theo thang 10.0
    correct_count: int = 0              # Số câu đúng
    wrong_count: int = 0                # Số câu sai
    blank_count: int = 0                # Số câu bỏ trống
    multiple_count: int = 0             # Số câu tô nhiều đáp án
    
    # Trạng thái xử lý: "Thành công", "Cảnh báo", "Lỗi"
    status: str = "Chưa xử lý"
    needs_review: bool = False
    warning_message: str = ""
    error_message: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Submission':
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)
