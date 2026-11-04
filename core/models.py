"""
Module: models.py
Định nghĩa cấu trúc dữ liệu cho Hệ thống nhận diện và chấm trắc nghiệm THPT 50 câu.
Tinh giản, gọn gàng, tập trung đúng vào yêu cầu bài toán Thị giác máy tính.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Submission:
    """Kết quả xử lý và chấm điểm của một học sinh"""
    submission_id: str
    student_id: str = ""                # Mã học sinh (lấy từ tên file hoặc SBD)
    student_name: str = ""
    exam_code: str = ""                 # Mã đề thi đọc từ phiếu
    image_path: str = ""                # Đường dẫn file ảnh gốc
    processed_image_path: str = ""      # Đường dẫn phiếu đã cắt và căn phẳng
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
    sbd: str = ""                       # Số báo danh đọc từ phiếu

