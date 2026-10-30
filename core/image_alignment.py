"""
Module: image_alignment.py
Chức năng 2: Tiền xử lý ảnh và Căn chỉnh phối cảnh (Perspective Transform)
Áp dụng các thuật toán OpenCV:
  1. Đọc ảnh an toàn với đường dẫn tiếng Việt
  2. Chuyển ảnh sang ảnh xám (Grayscale)
  3. Khử nhiễu bằng Gaussian Blur
  4. Nhị phân hóa bằng Adaptive Threshold và Otsu Threshold
  5. Phát hiện đường viền phiếu bằng Contour Detection (4 Marker định vị hoặc viền giấy)
  6. Căn chỉnh ảnh bị nghiêng/chụp lệch bằng Perspective Transform
  7. Chuẩn hóa kích thước phiếu về chuẩn 1200 x 1700 pixel
"""

import os
import sys
import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.cv_utils import imread_utf8, imwrite_utf8

# Kích thước chuẩn hóa của phiếu thi (A4 tỷ lệ chuẩn)
STANDARD_WIDTH = 1200
STANDARD_HEIGHT = 1700

# Tọa độ tâm của 4 marker chuẩn trên canvas 1200x1700
# Marker TL: x=40, y=40, w=50, h=50 -> Tâm = (65, 65)
# Marker TR: x=1110, y=40 -> Tâm = (1135, 65)
# Marker BR: x=1110, y=1610 -> Tâm = (1135, 1635)
# Marker BL: x=40, y=1610 -> Tâm = (65, 1635)
DST_MARKER_CENTERS = np.float32([
    [65, 65],       # Top-Left
    [1135, 65],     # Top-Right
    [1135, 1635],   # Bottom-Right
    [65, 1635]      # Bottom-Left
])

# 4 góc mép giấy chuẩn
DST_PAPER_CORNERS = np.float32([
    [0, 0],
    [STANDARD_WIDTH, 0],
    [STANDARD_WIDTH, STANDARD_HEIGHT],
    [0, STANDARD_HEIGHT]
])


def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Sắp xếp 4 tọa độ theo thứ tự hình học:
    [0: Top-Left, 1: Top-Right, 2: Bottom-Right, 3: Bottom-Left]
    """
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]       # Top-Left có tổng x+y nhỏ nhất
    rect[2] = pts[np.argmax(s)]       # Bottom-Right có tổng x+y lớn nhất

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]    # Top-Right có y - x nhỏ nhất
    rect[3] = pts[np.argmax(diff)]    # Bottom-Left có y - x lớn nhất
    return rect


def find_fiducial_markers(gray_img: np.ndarray) -> Optional[np.ndarray]:
    """
    Phát hiện 4 Marker định vị hình vuông màu đen ở 4 góc của phiếu thi.
    Sử dụng kết hợp:
      - Gaussian Blur khử nhiễu
      - Adaptive Threshold và Otsu Threshold
      - Contour Detection (cv2.findContours, approxPolyDP)
      - Kiểm tra tính chất hình học: đa giác 4 cạnh, aspect ratio ~1.0, đa giác lồi
    """
    h_img, w_img = gray_img.shape[:2]
    mid_x = w_img / 2.0
    mid_y = h_img / 2.0

    # Thử nhiều phương pháp nhị phân hóa để thích ứng với ánh sáng (bóng đổ, thiếu sáng)
    threshold_methods = [
        lambda img: cv2.adaptiveThreshold(
            cv2.GaussianBlur(img, (5, 5), 0), 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10
        ),
        lambda img: cv2.adaptiveThreshold(
            cv2.GaussianBlur(img, (5, 5), 0), 255, 
            cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 10
        ),
        lambda img: cv2.threshold(
            cv2.GaussianBlur(img, (5, 5), 0), 0, 255, 
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]
    ]

    for get_thresh in threshold_methods:
        thresh = get_thresh(gray_img)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Marker kích thước ~50x50 px, trên ảnh chụp có diện tích khoảng 400 - 15000 px
            if area < 400 or area > 15000:
                continue

            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / float(h)
                if 0.70 <= aspect_ratio <= 1.40:
                    # Kiểm tra ô vuông đen đặc (mean intensity thấp)
                    roi_crop = gray_img[y:y+h, x:x+w]
                    if roi_crop.size > 0 and np.mean(roi_crop) < 85:
                        hull = cv2.convexHull(cnt)
                        hull_area = cv2.contourArea(hull)
                        if hull_area > 0 and (float(area) / hull_area) > 0.80:
                            cx = x + w / 2.0
                            cy = y + h / 2.0
                            candidates.append({
                                "center": (cx, cy),
                                "area": area,
                                "bbox": (x, y, w, h)
                            })

        if len(candidates) < 4:
            continue

        # Phân loại candidate vào 4 góc (quadrants)
        quadrants = {"TL": [], "TR": [], "BL": [], "BR": []}
        corner_targets = {
            "TL": (0, 0),
            "TR": (w_img, 0),
            "BL": (0, h_img),
            "BR": (w_img, h_img)
        }

        for cand in candidates:
            cx, cy = cand["center"]
            if cx < mid_x and cy < mid_y:
                quadrants["TL"].append(cand)
            elif cx >= mid_x and cy < mid_y:
                quadrants["TR"].append(cand)
            elif cx < mid_x and cy >= mid_y:
                quadrants["BL"].append(cand)
            else:
                quadrants["BR"].append(cand)

        # Bắt buộc mỗi góc phải có ít nhất 1 candidate hợp lệ
        if not (quadrants["TL"] and quadrants["TR"] and quadrants["BL"] and quadrants["BR"]):
            continue

        selected_markers = {}
        for q_name, target in corner_targets.items():
            tx, ty = target
            best_cand = min(
                quadrants[q_name],
                key=lambda c: (c["center"][0] - tx)**2 + (c["center"][1] - ty)**2
            )
            selected_markers[q_name] = best_cand

        tl = selected_markers["TL"]["center"]
        tr = selected_markers["TR"]["center"]
        br = selected_markers["BR"]["center"]
        bl = selected_markers["BL"]["center"]

        # Kiểm tra tính tương đồng về kích thước giữa 4 marker
        areas = [selected_markers[k]["area"] for k in ["TL", "TR", "BR", "BL"]]
        if max(areas) / max(min(areas), 1) > 5.0:
            continue

        # Kiểm tra tính hợp lệ hình học tứ giác
        if not (tr[0] > tl[0] + 0.35 * w_img and br[0] > bl[0] + 0.35 * w_img):
            continue
        if not (bl[1] > tl[1] + 0.35 * h_img and br[1] > tr[1] + 0.35 * h_img):
            continue

        pts = np.array([tl, tr, br, bl], dtype=np.float32)
        if not cv2.isContourConvex(pts.astype(np.int32)):
            continue

        return order_points(pts)

    return None


def find_paper_contour(gray_img: np.ndarray) -> Optional[np.ndarray]:
    """
    Phát hiện đường viền toàn bộ tờ giấy bằng Contour Detection:
    - Gaussian Blur -> Canny edge detection / Otsu threshold
    - Tìm contour lồi lớn nhất có 4 đỉnh xấp xỉ tờ phiếu
    """
    h, w = gray_img.shape[:2]
    min_area = (h * w) * 0.20  # Tờ giấy phải chiếm ít nhất 20% khung hình
    blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # Thử phát hiện cạnh Canny
    edged = cv2.Canny(blurred, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edged, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            pts = approx.reshape(4, 2).astype(np.float32)
            return order_points(pts)

    return None


def align_paper(image_input) -> Tuple[bool, Optional[np.ndarray], str]:
    """
    Hàm thực hiện Tiền xử lý và Căn chỉnh phối cảnh (Perspective Transform):
      1. Đọc ảnh đầu vào
      2. Chuyển Grayscale
      3. Tìm 4 Marker định vị hoặc viền mép giấy
      4. Warp Perspective về kích thước chuẩn 1200 x 1700 px
    Trả về: (thành_công: bool, ảnh_chuẩn: np.ndarray, thông_báo: str)
    """
    if isinstance(image_input, str):
        img = imread_utf8(image_input)
        if img is None:
            return False, None, f"Không thể đọc file ảnh: {os.path.basename(image_input)}"
    else:
        img = image_input.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()

    # Bước 1: Ưu tiên phát hiện 4 Marker định vị chuẩn
    marker_pts = find_fiducial_markers(gray)
    if marker_pts is not None and len(marker_pts) == 4:
        matrix = cv2.getPerspectiveTransform(marker_pts, DST_MARKER_CENTERS)
        aligned = cv2.warpPerspective(img, matrix, (STANDARD_WIDTH, STANDARD_HEIGHT))
        return True, aligned, "Căn chỉnh thành công bằng 4 Marker định vị góc."

    # Bước 2: Dự phòng phát hiện viền tờ phiếu (Paper contour detection)
    paper_pts = find_paper_contour(gray)
    if paper_pts is not None and len(paper_pts) == 4:
        matrix = cv2.getPerspectiveTransform(paper_pts, DST_PAPER_CORNERS)
        aligned = cv2.warpPerspective(img, matrix, (STANDARD_WIDTH, STANDARD_HEIGHT))
        return True, aligned, "Căn chỉnh thành công bằng đường viền phiếu."

    return False, None, "Không tìm thấy 4 marker định vị hoặc viền phiếu hợp lệ. Vui lòng chụp rõ toàn bộ 4 góc phiếu!"
