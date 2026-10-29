"""
Module: ocr_engine.py
Hệ thống Nhận diện Ký tự Quang học (Optical Character Recognition - OCR)
Chức năng:
  - Nhận diện Họ và tên viết tay / in chữ trên khung tiêu đề bài thi
  - Nhận diện các chữ số viết tay ở ô SBD và ô Mã đề thi
  - Đối chiếu chéo (Cross-validation) giữa kết quả OMR (ô tô tròn) và OCR (chữ số)
  - Tích hợp Windows Media OCR (winocr) siêu nhanh và chuẩn xác
"""

import os
import sys
import asyncio
from typing import Dict, Any, Tuple, Optional
import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import winocr
    HAS_WINOCR = True
except ImportError:
    HAS_WINOCR = False


def preprocess_roi_for_ocr(roi_bgr: np.ndarray, upscale: float = 2.0) -> Image.Image:
    """
    Tiền xử lý ảnh vùng quan tâm (ROI) để tối ưu độ chính xác nhận diện ký tự:
    - Resize phóng to
    - Grayscale + Khử nhiễu
    - Tăng độ tương phản nhẹ
    """
    if roi_bgr is None or roi_bgr.size == 0:
        return Image.new("RGB", (100, 40), (255, 255, 255))

    h, w = roi_bgr.shape[:2]
    new_w, new_h = max(int(w * upscale), 80), max(int(h * upscale), 30)
    resized = cv2.resize(roi_bgr, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    # Chuyển xám và cân bằng sáng nhẹ
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if len(resized.shape) == 3 else resized
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    enhanced = clahe.apply(gray)

    # Chuyển sang PIL Image (RGB)
    rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(rgb)


def recognize_text_from_crop(roi_bgr: np.ndarray) -> str:
    """
    Nhận diện văn bản từ ảnh cắt ROI (chạy đồng bộ an toàn)
    """
    if roi_bgr is None or roi_bgr.size == 0:
        return ""

    pil_img = preprocess_roi_for_ocr(roi_bgr)

    if HAS_WINOCR:
        try:
            # Tạo event loop mới nếu loop hiện tại đang chạy hoặc chưa có
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, winocr.recognize_pil(pil_img))
                        ocr_res = future.result(timeout=4)
                else:
                    ocr_res = loop.run_until_complete(winocr.recognize_pil(pil_img))
            except RuntimeError:
                ocr_res = asyncio.run(winocr.recognize_pil(pil_img))

            raw_txt = ocr_res.text if hasattr(ocr_res, "text") else str(ocr_res)
            return raw_txt.strip()
        except Exception as e:
            # Fallback nếu winocr gặp lỗi tạm thời
            pass

    return ""


def clean_student_name(raw_text: str) -> str:
    """Loại bỏ các nhãn tiền tố như 'Ho va ten:', 'Họ tên:', 'Tên:' nếu có"""
    cleaned = raw_text.strip()
    prefixes = ["HO VA TEN:", "HO TEN:", "HỌ VÀ TÊN:", "HỌ TÊN:", "TEN:", "TÊN:", "NAME:"]
    upper_c = cleaned.upper()
    for p in prefixes:
        if upper_c.startswith(p):
            cleaned = cleaned[len(p):].strip()
            break
    # Loại bỏ các dấu chấm hoặc gạch chân liên tiếp (dòng kẻ)
    cleaned = cleaned.replace("_", " ").replace(".", " ").strip()
    # Chuẩn hóa khoảng trắng
    return " ".join(cleaned.split())


def clean_digits_only(raw_text: str) -> str:
    """Lọc chỉ lấy các chữ số 0-9"""
    return "".join([c for c in raw_text if c.isdigit()])


def extract_header_info_ocr(aligned_img: np.ndarray) -> Dict[str, Any]:
    """
    Cắt các vùng tiêu đề trên phiếu đã nắn phẳng 1200x1700 px và chạy OCR:
      1. Khung Họ và tên: X=120..620, Y=100..138
      2. Khung Số báo danh (6 ô số viết tay): X=140..540, Y=168..198
      3. Khung Mã đề thi (3 ô số viết tay): X=660..860, Y=168..198
    """
    if aligned_img is None or aligned_img.shape[0] < 1200:
        return {"name": "", "sbd": "", "exam_code": "", "raw": {}}

    h_img, w_img = aligned_img.shape[:2]

    # 1. ROI Họ và tên
    # Vùng chứa tên: X từ 210 đến 620, Y từ 102 đến 138
    roi_name = aligned_img[100:140, 210:620]
    raw_name = recognize_text_from_crop(roi_name)
    cleaned_name = clean_student_name(raw_name)

    # 2. ROI 6 ô viết tay Số Báo Danh
    # X từ 135 đến 545, Y từ 166 đến 198
    roi_sbd_digits = aligned_img[166:198, 135:545]
    raw_sbd = recognize_text_from_crop(roi_sbd_digits)
    cleaned_sbd = clean_digits_only(raw_sbd)

    # 3. ROI 3 ô viết tay Mã Đề Thi
    # X từ 655 đến 865, Y từ 166 đến 198
    roi_code_digits = aligned_img[166:198, 655:865]
    raw_code = recognize_text_from_crop(roi_code_digits)
    cleaned_code = clean_digits_only(raw_code)

    return {
        "name": cleaned_name,
        "sbd": cleaned_sbd,
        "exam_code": cleaned_code,
        "raw": {
            "name": raw_name,
            "sbd": raw_sbd,
            "exam_code": raw_code
        }
    }


def cross_validate_omr_ocr(omr_val: str, ocr_val: str, expected_len: int = 6) -> Tuple[str, bool]:
    """
    Đối chiếu chéo giữa OMR (ô tô tròn) và OCR (chữ số viết tay):
    - Nếu OMR đọc rõ và khớp OCR -> Rất tin cậy (True)
    - Nếu OMR đọc được 6 chữ số nhưng OCR đọc thiếu (do viết ẩu) -> Ưu tiên OMR
    - Nếu OMR bị nghi vấn hoặc tẩy mờ mà OCR đọc rõ -> Hỗ trợ đối chiếu
    """
    omr_clean = str(omr_val).strip()
    ocr_clean = str(ocr_val).strip()

    if omr_clean == ocr_clean and len(omr_clean) == expected_len:
        return omr_clean, True

    # Nếu OMR đủ độ dài chuẩn
    if len(omr_clean) == expected_len and omr_clean != "0" * expected_len:
        return omr_clean, False

    # Nếu OCR đọc đủ độ dài chuẩn
    if len(ocr_clean) == expected_len:
        return ocr_clean, False

    return omr_clean or ocr_clean, False
