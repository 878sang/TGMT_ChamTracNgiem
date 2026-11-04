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

from gui.app import OMRGradingApp


def main():
    print("=" * 72)
    print(" KHỞI ĐỘNG PHẦN MỀM CHẤM PHIẾU TRẮC NGHIỆM THPT (50 CÂU) - OPENCV")
    print("=" * 72)
    app = OMRGradingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
