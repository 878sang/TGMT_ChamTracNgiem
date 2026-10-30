"""
==============================================================================
HỆ THỐNG NHẬN DIỆN VÀ CHẤM PHIẾU TRẢ LỜI TRẮC NGHIỆM THPT (50 CÂU)
BÀI TẬP NHÓM MÔN HỌC: THỊ GIÁC MÁY TÍNH (COMPUTER VISION)
CÔNG NGHỆ: PYTHON & OPENCV & CUSTOMTKINTER
==============================================================================
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.sheet_generator import generate_all_samples
from gui.app import OMRGradingApp


def prepare_environment():
    """Kiểm tra và khởi tạo mẫu phiếu trắng cùng bộ dữ liệu mẫu 50 câu nếu chưa có"""
    template_path = os.path.join(PROJECT_ROOT, "templates", "phieu_50_cau_chuan.png")
    sample_dir = os.path.join(PROJECT_ROOT, "dataset", "sample_submissions_50cau")
    
    if not os.path.exists(template_path) or not os.path.exists(sample_dir):
        print("Đang khởi tạo mẫu phiếu chuẩn 50 câu và tập ảnh mẫu...")
        generate_all_samples()
        print("Khởi tạo hoàn tất!")


def main():
    print("=" * 72)
    print(" KHỞI ĐỘNG PHẦN MỀM CHẤM PHIẾU TRẮC NGHIỆM THPT (50 CÂU) - OPENCV")
    print("=" * 72)
    prepare_environment()

    app = OMRGradingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
