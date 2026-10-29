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
    Tìm và xác thực chặt chẽ 4 ô vuông đen to (Fiducial Markers) ở 4 góc của phiếu trả lời.
    Yêu cầu:
      - Phải tìm thấy đúng 4 marker nằm ở 4 góc riêng biệt (TL, TR, BL, BR)
      - Kích thước và hình dáng hợp lệ (hình vuông đặc, aspect ratio ~1.0)
      - Nếu thiếu bất kỳ góc nào hoặc hình học không hợp lệ -> Trả về None (báo lỗi).
    """
    h_img, w_img = gray_img.shape[:2]
    mid_x = w_img / 2.0
    mid_y = h_img / 2.0

    # Thử các mức thresholding khác nhau để thích ứng ánh sáng (bóng đổ, thiếu sáng)
    threshold_methods = [
        lambda img: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, 
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10),
        lambda img: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, 
                                          cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 10),
        lambda img: cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, 
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    ]

    for get_thresh in threshold_methods:
        thresh = get_thresh(gray_img)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Marker kích thước ~50x50 px, trên ảnh chụp có diện tích khoảng 500 - 10000 px
            if area < 500 or area > 10000:
                continue

            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / float(h)
                if 0.70 <= aspect_ratio <= 1.40:
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
        quadrants = {
            "TL": [],  # Top-Left
            "TR": [],  # Top-Right
            "BL": [],  # Bottom-Left
            "BR": []   # Bottom-Right
        }

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

        # BẮT BUỘC: Cả 4 góc phải có ít nhất 1 candidate hợp lệ
        if not (quadrants["TL"] and quadrants["TR"] and quadrants["BL"] and quadrants["BR"]):
            continue

        # Ở mỗi góc, chọn candidate nằm gần góc ngoài nhất
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

        # Kiểm tra tính tương đồng về diện tích giữa 4 marker
        areas = [selected_markers[k]["area"] for k in ["TL", "TR", "BR", "BL"]]
        if max(areas) / max(min(areas), 1) > 4.5:
            continue

        # Kiểm tra tính hợp lệ hình học của tứ giác 4 marker
        if not (tr[0] > tl[0] + 0.35 * w_img and br[0] > bl[0] + 0.35 * w_img):
            continue
        if not (bl[1] > tl[1] + 0.35 * h_img and br[1] > tr[1] + 0.35 * h_img):
            continue

        pts = np.array([tl, tr, br, bl], dtype=np.float32)
        if not cv2.isContourConvex(pts.astype(np.int32)):
            continue

        # Sắp xếp đúng thứ tự: [TL, TR, BR, BL]
        ordered = order_points(pts)
        return ordered

    return None


def align_paper(image_input) -> Tuple[bool, Optional[np.ndarray], str]:
    """
    Nắn phẳng ảnh chụp về ảnh chuẩn 1200 x 1700 pixel.
    Chỉ căn chỉnh khi xác định được đúng 4 marker hợp lệ ở 4 góc; nếu không, báo ảnh lỗi.
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

    # Tìm đúng 4 marker định vị góc
    marker_pts = find_fiducial_markers(gray)
    if marker_pts is not None and len(marker_pts) == 4:
        matrix = cv2.getPerspectiveTransform(marker_pts, DST_MARKER_CENTERS)
        aligned = cv2.warpPerspective(img, matrix, (STANDARD_WIDTH, STANDARD_HEIGHT))
        return True, aligned, "Căn chỉnh thành công bằng 4 Marker định vị."

    # Không tìm thấy đủ 4 marker hợp lệ -> Báo lỗi ảnh rõ ràng
    return False, None, "Không xác định đủ 4 marker định vị góc hợp lệ trên phiếu thi. Vui lòng chụp rõ toàn bộ 4 góc phiếu!"


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
    test_photo_path = os.path.join(PROJECT_ROOT, "dataset", "sample_submissions", "photo_test_full_mcq.jpg")
    success, aligned, msg = align_paper(test_photo_path)
    print(f"Ket qua can chinh: {success} | {msg}")
    if success and aligned is not None:
        out_test = os.path.join(PROJECT_ROOT, "dataset", "sample_submissions", "aligned_result_test.png")
        imwrite_utf8(out_test, aligned)
        rois = crop_exam_rois(aligned, mode=ExamMode.FULL_MCQ)
        print("Da crop cac ROI thanh cong:", list(rois.keys()))

