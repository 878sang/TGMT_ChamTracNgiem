"""
Module: image_alignment.py
Phụ trách: Thành viên 1 (Computer Vision 1)
Chức năng:
  - Tiền xử lý ảnh (Grayscale, Blur, Threshold)
  - Tự động phát hiện 4 Marker định vị ở 4 góc phiếu
  - Biến đổi phối cảnh (Perspective Transform) nắn phẳng ảnh về kích thước chuẩn 1200 x 1700 px
  - Cắt các khối vùng quan tâm (ROI) theo chế độ thi
"""

import os
import sys

# Thêm đường dẫn gốc dự án vào sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict
from core.models import ExamMode
from core.cv_utils import imread_utf8, imwrite_utf8




STANDARD_WIDTH = 1200
STANDARD_HEIGHT = 1700

# Tọa độ tâm của 4 marker chuẩn trên canvas 1200x1700
# Marker TL: x=40, y=40, w=50, h=50 -> Tâm = (65, 65)
# Marker TR: x=1110, y=40 -> Tâm = (1135, 65)
# Marker BL: x=40, y=1610 -> Tâm = (65, 1635)
# Marker BR: x=1110, y=1610 -> Tâm = (1135, 1635)
DST_MARKER_CENTERS = np.float32([
    [65, 65],       # Top-Left
    [1135, 65],     # Top-Right
    [1135, 1635],   # Bottom-Right
    [65, 1635]      # Bottom-Left
])

DST_PAPER_CORNERS = np.float32([
    [0, 0],
    [STANDARD_WIDTH, 0],
    [STANDARD_WIDTH, STANDARD_HEIGHT],
    [0, STANDARD_HEIGHT]
])


def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Sắp xếp 4 toạ độ theo thứ tự: [Top-Left, Top-Right, Bottom-Right, Bottom-Left]
    """
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # Top-Left có x+y nhỏ nhất
    rect[2] = pts[np.argmax(s)]   # Bottom-Right có x+y lớn nhất

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-Right có y-x nhỏ nhất
    rect[3] = pts[np.argmax(diff)]  # Bottom-Left có y-x lớn nhất
    return rect


def find_fiducial_markers(gray_img: np.ndarray) -> Optional[np.ndarray]:
    """
    Tìm 4 ô vuông đen to (Fiducial Markers) ở 4 góc của phiếu trả lời
    """
    blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 25, 10)

    # Dùng RETR_LIST để tìm cả các contour bên trong viền phiếu
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    candidates = []
    h_img, w_img = gray_img.shape[:2]

    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Marker kích thước ~50x50 trên ảnh chụp có diện tích khoảng 700 - 4000
        if area < 600 or area > 5000:
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

        # Marker là hình tứ giác (4 đỉnh)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / float(h)
            if 0.75 <= aspect_ratio <= 1.35:
                # Kiểm tra độ đặc
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0 and (float(area) / hull_area) > 0.85:
                    cx = x + w / 2.0
                    cy = y + h / 2.0
                    candidates.append((cx, cy, area))

    if len(candidates) >= 4:
        # Nếu có từ 4 candidates trở lên, lấy 4 candidate gần 4 góc ngoài nhất
        pts = np.array([[c[0], c[1]] for c in candidates], dtype=np.float32)
        # Sắp xếp và lấy 4 điểm cực
        ordered = order_points(pts)
        return ordered

    return None



def find_paper_sheet_contour(gray_img: np.ndarray) -> Optional[np.ndarray]:
    """
    Phương án dự phòng: Tìm 4 góc của toàn bộ tờ giấy A4 nếu không bắt được 4 marker
    """
    blurred = cv2.GaussianBlur(gray_img, (7, 7), 0)
    edged = cv2.Canny(blurred, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edged, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
        if len(approx) == 4 and cv2.contourArea(cnt) > (gray_img.shape[0] * gray_img.shape[1] * 0.25):
            pts = approx.reshape(4, 2).astype(np.float32)
            return order_points(pts)

    return None


def align_paper(image_input) -> Tuple[bool, Optional[np.ndarray], str]:
    """
    Nắn phẳng ảnh chụp bất kỳ về ảnh chuẩn 1200 x 1700 pixel.
    - image_input: đường dẫn file hoặc numpy array ảnh BGR
    Trả về: (thành_công: bool, ảnh_chuẩn: np.ndarray, thông_báo: str)
    """
    if isinstance(image_input, str):
        img = imread_utf8(image_input)
        if img is None:
            return False, None, f"Không thể đọc file ảnh: {image_input}"
    else:
        img = image_input.copy()


    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()

    # Cách 1: Tìm 4 marker định vị góc
    marker_pts = find_fiducial_markers(gray)
    if marker_pts is not None and len(marker_pts) == 4:
        matrix = cv2.getPerspectiveTransform(marker_pts, DST_MARKER_CENTERS)
        aligned = cv2.warpPerspective(img, matrix, (STANDARD_WIDTH, STANDARD_HEIGHT))
        return True, aligned, "Căn chỉnh thành công bằng 4 Marker định vị."

    # Cách 2: Tìm 4 góc mép giấy A4
    paper_pts = find_paper_sheet_contour(gray)
    if paper_pts is not None and len(paper_pts) == 4:
        matrix = cv2.getPerspectiveTransform(paper_pts, DST_PAPER_CORNERS)
        aligned = cv2.warpPerspective(img, matrix, (STANDARD_WIDTH, STANDARD_HEIGHT))
        return True, aligned, "Căn chỉnh thành công theo mép viền phiếu."

    # Nếu ảnh đã có kích thước chuẩn xấp xỉ
    h, w = img.shape[:2]
    if abs(w - STANDARD_WIDTH) < 50 and abs(h - STANDARD_HEIGHT) < 50:
        resized = cv2.resize(img, (STANDARD_WIDTH, STANDARD_HEIGHT))
        return True, resized, "Ảnh đã chuẩn tỷ lệ kích thước."

    return False, None, "Không tìm thấy 4 góc định vị hoặc viền phiếu. Vui lòng chụp rõ toàn bộ tờ phiếu!"


def crop_exam_rois(aligned_img: np.ndarray, mode: str = ExamMode.FULL_MCQ) -> Dict[str, np.ndarray]:
    """
    Cắt các khối vùng quan tâm (ROI) dựa trên chế độ bài thi.
    Tất cả tọa độ đều là pixel tuyệt đối trên ảnh phẳng 1200x1700.
    """
    rois = {}

    # 1. Khối Header: SBD và Mã đề (dùng chung cho cả 2 mode)
    # SBD: X=120..560, Y=140..460
    # Mã đề: X=640..880, Y=140..460
    rois["sbd"] = aligned_img[140:460, 120:560]
    rois["exam_code"] = aligned_img[140:460, 640:880]

    if mode == ExamMode.FULL_MCQ:
        # Cột 1: Câu 1-20 (X: 110->560, Y: 520->1580)
        # Cột 2: Câu 21-40 (X: 630->1080, Y: 520->1580)
        rois["mcq_col1"] = aligned_img[520:1580, 110:560]
        rois["mcq_col2"] = aligned_img[520:1580, 630:1080]

    elif mode == ExamMode.THPT_2025:
        # Phần I: 12 câu 4 lựa chọn (Y: 480->800, X: 100->1130)
        rois["part1"] = aligned_img[480:800, 100:1130]
        # Phần II: 4 câu Đúng/Sai (Y: 820->1190, X: 100->1130)
        rois["part2"] = aligned_img[820:1190, 100:1130]
        # Phần III: 6 câu Trả lời ngắn (Y: 1210->1590, X: 100->1130)
        rois["part3"] = aligned_img[1210:1590, 100:1130]

    return rois


if __name__ == "__main__":
    # Test thử nghiệm căn chỉnh trên ảnh chụp nghiêng thực tế
    test_photo_path = "d:/Thị giác máy tính/Đồ Án/dataset/sample_submissions/photo_test_full_mcq.jpg"
    success, aligned, msg = align_paper(test_photo_path)
    print(f"Ket qua can chinh: {success} | {msg}")
    if success and aligned is not None:
        imwrite_utf8("d:/Thị giác máy tính/Đồ Án/dataset/sample_submissions/aligned_result_test.png", aligned)
        rois = crop_exam_rois(aligned, mode=ExamMode.FULL_MCQ)
        print("Da crop cac ROI thanh cong:", list(rois.keys()))

