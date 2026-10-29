"""
Module: cv_utils.py
Cung cấp các hàm tiện ích hỗ trợ đọc/ghi ảnh với đường dẫn tiếng Việt có dấu trên Windows
"""

import os
import sys
import cv2
import numpy as np
from typing import Optional

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def imread_utf8(filepath: str, flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """
    Đọc ảnh an toàn trên Windows với đường dẫn chứa tiếng Việt có dấu.
    Tránh lỗi OpenCV C++ không đọc được Unicode path.
    """
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "rb") as f:
            bytes_data = f.read()
        nparr = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(nparr, flags)
        return img
    except Exception as e:
        print(f"Lỗi đọc ảnh imread_utf8: {e}")
        return None


def imwrite_utf8(filepath: str, img: np.ndarray) -> bool:
    """
    Ghi ảnh an toàn trên Windows với đường dẫn chứa tiếng Việt có dấu.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        ext = os.path.splitext(filepath)[1]
        if not ext:
            ext = ".png"
        is_success, buffer = cv2.imencode(ext, img)
        if is_success:
            with open(filepath, "wb") as f:
                f.write(buffer)
            return True
        return False
    except Exception as e:
        print(f"Lỗi ghi ảnh imwrite_utf8: {e}")
        return False
