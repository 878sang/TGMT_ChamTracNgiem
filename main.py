"""
==============================================================================
HỆ THỐNG QUÉT VÀ CHẤM BÀI TRẮC NGHIỆM ĐA NĂNG BẰNG PYTHON & COMPUTER VISION
ĐỒ ÁN MÔN HỌC: THỊ GIÁC MÁY TÍNH
HỖ TRỢ 2 CHẾ ĐỘ THI:
  1. FULL TRẮC NGHIỆM (4 LỰA CHỌN A-B-C-D)
  2. ĐỀ CHUẨN TỐT NGHIỆP THPT MỚI BỘ GIÁO DỤC & ĐÀO TẠO (3 PHẦN)
==============================================================================
"""

import os
import sys

# Đảm bảo import thư mục gốc
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.models import Exam, ExamMode
from core.storage_manager import get_all_exams, save_exam
from core.excel_answer_handler import import_thpt_answer_key_from_excel
from gui.app import OMRGradingApp


def init_sample_exams_if_empty():
    """Khởi tạo bài thi mẫu nếu hệ thống mới chạy lần đầu (chưa có file dữ liệu)"""
    from core.storage_manager import EXAMS_FILE
    if not os.path.exists(EXAMS_FILE):
        # Bài mẫu 1: Full trắc nghiệm 40 câu
        sample_key_full = {i: ['A', 'B', 'C', 'D'][(i * 3 + 1) % 4] for i in range(1, 41)}
        exam1 = Exam(
            exam_id="exam_demo_full_mcq",
            title="Kiểm Tra 1 Tiết Giữa Kỳ (Môn Toán)",
            subject="Toán",
            class_name="12A1",
            mode=ExamMode.FULL_MCQ,
            num_questions=40,
            answer_keys={"101": sample_key_full}
        )
        save_exam(exam1)

        # Bài mẫu 2: Chuẩn THPT mới BGD&ĐT (3 phần)
        thpt_excel = os.path.join(PROJECT_ROOT, "templates/mau_dap_an_thpt_2025.xlsx")
        thpt_keys = {}
        if os.path.exists(thpt_excel):
            thpt_keys["101"] = import_thpt_answer_key_from_excel(thpt_excel)
        else:
            p1 = {i: ['A', 'C', 'B', 'D'][i % 4] for i in range(1, 13)}
            p2 = {1: {'a':'Đ', 'b':'S', 'c':'Đ', 'd':'Đ'}, 2: {'a':'S', 'b':'Đ', 'c':'S', 'd':'Đ'}, 3: {'a':'Đ', 'b':'Đ', 'c':'S', 'd':'S'}, 4: {'a':'S', 'b':'S', 'c':'Đ', 'd':'Đ'}}
            p3 = {1: '15', 2: '-2.5', 3: '0.75', 4: '120', 5: '-8', 6: '3.14'}
            thpt_keys["101"] = {"part1": p1, "part2": p2, "part3": p3}

        exam2 = Exam(
            exam_id="exam_demo_thpt_2025",
            title="Thi Thử Tốt Nghiệp THPT 2025 (Bộ GD&ĐT)",
            subject="Toán",
            class_name="Khối 12",
            mode=ExamMode.THPT_2025,
            answer_keys=thpt_keys
        )
        save_exam(exam2)
        print("Đã khởi tạo 2 bài kiểm tra mẫu thành công!")


def main():
    print("=" * 70)
    print(" KHỞI ĐỘNG HỆ THỐNG CHẤM BÀI TRẮC NGHIỆM ĐA NĂNG (OMR - PYTHON)")
    print("=" * 70)
    init_sample_exams_if_empty()

    app = OMRGradingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
