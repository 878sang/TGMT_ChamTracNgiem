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
  7. Cắt phiếu đã căn chỉnh theo kích thước canvas của layout đang hoạt động
"""

import os
import sys
import cv2
import numpy as np
from itertools import combinations
from typing import Any, Tuple, Optional, List, Dict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.cv_utils import imread_utf8
from core.layouts import load_layout

ACTIVE_LAYOUT = load_layout()
STANDARD_WIDTH = int(ACTIVE_LAYOUT["canvas_w"])
STANDARD_HEIGHT = int(ACTIVE_LAYOUT["canvas_h"])
_layout_markers = ACTIVE_LAYOUT["markers"]
_min_x = min(marker["x"] for marker in _layout_markers)
_max_x = max(marker["x"] for marker in _layout_markers)
_min_y = min(marker["y"] for marker in _layout_markers)
_max_y = max(marker["y"] for marker in _layout_markers)
_marker_corners = [
    min(
        _layout_markers,
        key=lambda marker: (marker["x"] - x) ** 2 + (marker["y"] - y) ** 2,
    )
    for x, y in (
        (_min_x, _min_y),
        (_max_x, _min_y),
        (_min_x, _max_y),
        (_max_x, _max_y),
    )
]
DST_MARKER_CENTERS = np.float32(
    [
        [_marker_corners[0]["x"], _marker_corners[0]["y"]],
        [_marker_corners[1]["x"], _marker_corners[1]["y"]],
        [_marker_corners[3]["x"], _marker_corners[3]["y"]],
        [_marker_corners[2]["x"], _marker_corners[2]["y"]],
    ]
)
DST_PAPER_CORNERS = np.float32(
    [[0, 0], [STANDARD_WIDTH, 0], [STANDARD_WIDTH, STANDARD_HEIGHT], [0, STANDARD_HEIGHT]]
)


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


def _select_marker_quad(
    candidates: List[Dict[str, Any]],
    image_width: int,
    image_height: int,
) -> Optional[np.ndarray]:
    """Choose the largest plausible page quad from the marker candidates."""
    edge_margin = max(4, int(round(min(image_width, image_height) * 0.01)))
    merge_distance = max(8, int(round(min(image_width, image_height) * 0.01)))
    unique_candidates = []

    for candidate in candidates:
        x, y, width, height = candidate["bbox"]
        if (
            x < edge_margin
            or y < edge_margin
            or x + width > image_width - edge_margin
            or y + height > image_height - edge_margin
        ):
            continue

        center = candidate["center"]
        duplicate_index = next(
            (
                index
                for index, existing in enumerate(unique_candidates)
                if np.linalg.norm(np.asarray(center) - np.asarray(existing["center"])) < merge_distance
            ),
            None,
        )
        if duplicate_index is None:
            unique_candidates.append(candidate)
        elif candidate["area"] > unique_candidates[duplicate_index]["area"]:
            unique_candidates[duplicate_index] = candidate

    if len(unique_candidates) < 4:
        return None

    minimum_span = 0.50 * min(image_width, image_height)
    target_width = np.linalg.norm(DST_MARKER_CENTERS[1] - DST_MARKER_CENTERS[0])
    target_height = np.linalg.norm(DST_MARKER_CENTERS[3] - DST_MARKER_CENTERS[0])
    target_ratio = target_width / target_height
    best_quad = None
    best_score = 0.0

    for group in combinations(unique_candidates, 4):
        areas = [candidate["area"] for candidate in group]
        if max(areas) / max(min(areas), 1) > 5.0:
            continue

        points = order_points(np.asarray([candidate["center"] for candidate in group], dtype=np.float32))
        if not cv2.isContourConvex(points.astype(np.int32)):
            continue

        top_width = np.linalg.norm(points[1] - points[0])
        bottom_width = np.linalg.norm(points[2] - points[3])
        left_height = np.linalg.norm(points[3] - points[0])
        right_height = np.linalg.norm(points[2] - points[1])
        average_width = (top_width + bottom_width) / 2.0
        average_height = (left_height + right_height) / 2.0
        if min(average_width, average_height) < minimum_span:
            continue

        page_ratio = min(average_width, average_height) / max(average_width, average_height)
        if not 0.45 <= page_ratio <= 0.90:
            continue
        if abs(np.log(page_ratio / target_ratio)) > np.log(1.5):
            continue

        area = abs(cv2.contourArea(points))
        ratio_error = abs(np.log(page_ratio / target_ratio))
        score = area * np.exp(-6 * ratio_error)
        if score > best_score:
            best_quad = points
            best_score = score

    return best_quad


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
    resolution_scale = min(1.0, min(w_img, h_img) / 1024.0)
    min_marker_area = max(100, int(round(50 * resolution_scale**2)))
    max_marker_area = max(
        min_marker_area + 1,
        int(round(15000 * resolution_scale**2)),
    )
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
        lambda img: cv2.morphologyEx(
            cv2.adaptiveThreshold(
                cv2.GaussianBlur(img, (5, 5), 0), 255,
                cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 10
            ),
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
        ),
        lambda img: cv2.threshold(
            cv2.GaussianBlur(img, (5, 5), 0), 0, 255, 
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]
    ]

    candidates = []
    max_marker_size = 0.04 * min(w_img, h_img)
    for get_thresh in threshold_methods:
        thresh = get_thresh(gray_img)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Marker kích thước ~50x50 px, trên ảnh chụp có diện tích khoảng 400 - 15000 px
            if area < min_marker_area or area > max_marker_area:
                continue

            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / float(h)
                if (
                    0.80 <= aspect_ratio <= 1.25
                    and max(w, h) <= max_marker_size
                ):
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

    return _select_marker_quad(candidates, w_img, h_img)


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

    # Woven or textured backgrounds often break the paper edge into many
    # short Canny segments. Segment the bright sheet and close those gaps
    # before looking for its outer boundary.
    _, bright = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    close_size = max(21, int(round(min(h, w) * 0.025)) | 1)
    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (close_size, close_size)
    )
    bright = cv2.morphologyEx(bright, cv2.MORPH_CLOSE, close_kernel, iterations=2)
    contours, _ = cv2.findContours(
        bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        hull = cv2.convexHull(cnt)
        area = cv2.contourArea(hull)
        if area < min_area or area > h * w * 0.98:
            continue
        perimeter = cv2.arcLength(hull, True)
        approx = cv2.approxPolyDP(hull, 0.025 * perimeter, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            return order_points(approx.reshape(4, 2).astype(np.float32))

    return None


def _portrait_quad(ordered_pts: np.ndarray) -> Tuple[np.ndarray, bool]:
    """Reorder a landscape page so its longer edges map to the portrait height."""
    top_length = np.linalg.norm(ordered_pts[1] - ordered_pts[0])
    side_length = np.linalg.norm(ordered_pts[3] - ordered_pts[0])
    if top_length > side_length:
        return np.roll(ordered_pts, -1, axis=0), True
    return ordered_pts, False


def _orientation_score(gray_img: np.ndarray) -> int:
    """Prefer the orientation with more answer bubbles below the form header."""
    gray = cv2.resize(gray_img, (600, 850), interpolation=cv2.INTER_AREA)
    thresh = cv2.adaptiveThreshold(
        cv2.GaussianBlur(gray, (5, 5), 0), 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 7
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    upper_count = 0
    lower_count = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if not 20 <= area <= 700:
            continue
        perimeter = cv2.arcLength(contour, True)
        if perimeter <= 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        x, y, width, height = cv2.boundingRect(contour)
        if not 0.60 <= circularity <= 1.50 or not 7 <= width <= 25 or not 7 <= height <= 25:
            continue
        if y < 360:
            upper_count += 1
        elif y < 790:
            lower_count += 1
    return lower_count - upper_count


def _layout_orientation_score(gray_img: np.ndarray) -> float:
    """Score how many THPT50 bubble outlines match their expected centers."""
    h, w = gray_img.shape[:2]
    matches = 0
    total = 0
    for block in ACTIVE_LAYOUT["blocks"]:
        radius = max(4, int(round(block["radius"])))
        outer_radius = radius + 8
        yy, xx = np.ogrid[-outer_radius:outer_radius + 1, -outer_radius:outer_radius + 1]
        distance_squared = xx * xx + yy * yy
        ring = (
            (distance_squared >= (radius - 1) ** 2)
            & (distance_squared <= (radius + 2) ** 2)
        )
        outside = (
            (distance_squared >= (radius + 4) ** 2)
            & (distance_squared <= outer_radius ** 2)
        )
        for row in block["questions"]:
            for point in row["options"].values():
                cx, cy = int(round(point["x"])), int(round(point["y"]))
                if (
                    cx - outer_radius < 0
                    or cy - outer_radius < 0
                    or cx + outer_radius >= w
                    or cy + outer_radius >= h
                ):
                    continue
                roi = gray_img[
                    cy - outer_radius:cy + outer_radius + 1,
                    cx - outer_radius:cx + outer_radius + 1,
                ]
                matches += float(np.mean(roi[outside]) - np.mean(roi[ring])) >= 15
                total += 1
    return matches / total if total else 0.0


def _template_feature_alignment(img: np.ndarray) -> Optional[np.ndarray]:
    """Register a difficult phone photo to the printed form using SIFT features."""
    template_path = os.path.join(
        PROJECT_ROOT, "templates", "layouts", "thpt50_base.png"
    )
    template = imread_utf8(template_path)
    if template is not None and template.ndim == 3:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    if template is None or not hasattr(cv2, "SIFT_create"):
        return None
    sift = cv2.SIFT_create(nfeatures=16000, contrastThreshold=0.01, edgeThreshold=8)
    template_keypoints, template_descriptors = sift.detectAndCompute(template, None)
    if template_descriptors is None:
        return None
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    best_warp = None
    best_score = 0.0
    rotations = (
        (img, None),
        (cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE), cv2.ROTATE_90_CLOCKWISE),
        (cv2.rotate(img, cv2.ROTATE_180), cv2.ROTATE_180),
        (cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE), cv2.ROTATE_90_COUNTERCLOCKWISE),
    )
    for rotated, _ in rotations:
        gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY) if rotated.ndim == 3 else rotated
        source_keypoints, source_descriptors = sift.detectAndCompute(gray, None)
        if source_descriptors is None:
            continue
        pairs = matcher.knnMatch(source_descriptors, template_descriptors, k=2)
        good = [first for first, second in pairs if first.distance < 0.78 * second.distance]
        if len(good) < 20:
            continue
        source_points = np.float32([source_keypoints[m.queryIdx].pt for m in good])
        target_points = np.float32([template_keypoints[m.trainIdx].pt for m in good])
        matrix, inliers = cv2.findHomography(source_points, target_points, cv2.RANSAC, 5.0)
        inlier_count = int(inliers.sum()) if inliers is not None else 0
        if matrix is None or inlier_count < 20 or inlier_count / len(good) < 0.18:
            continue
        h, w = gray.shape[:2]
        projected = cv2.perspectiveTransform(
            np.float32([[[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]]]),
            matrix,
        )[0]
        if not cv2.isContourConvex(projected.astype(np.int32)):
            continue
        candidate = cv2.warpPerspective(
            rotated, matrix, (STANDARD_WIDTH, STANDARD_HEIGHT)
        )
        candidate_gray = (
            cv2.cvtColor(candidate, cv2.COLOR_BGR2GRAY)
            if candidate.ndim == 3 else candidate
        )
        score = _layout_orientation_score(candidate_gray)
        if score > best_score:
            best_score, best_warp = score, candidate
    return best_warp


def _choose_alignment(img: np.ndarray, aligned: np.ndarray) -> Tuple[np.ndarray, bool]:
    """Use feature registration only when it clearly improves a weak page warp."""
    current_gray = (
        cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)
        if aligned.ndim == 3 else aligned
    )
    current_score = _layout_orientation_score(current_gray)
    if current_score >= 0.10:
        return aligned, False
    candidate = _template_feature_alignment(img)
    if candidate is None:
        return aligned, False
    candidate_gray = (
        cv2.cvtColor(candidate, cv2.COLOR_BGR2GRAY)
        if candidate.ndim == 3 else candidate
    )
    candidate_score = _layout_orientation_score(candidate_gray)
    candidate_marker_score = _template_marker_score(candidate_gray)
    is_strong_candidate = (
        candidate_score >= 0.50
        or (candidate_score >= 0.35 and candidate_marker_score >= 0.80)
    )
    if is_strong_candidate and candidate_score >= current_score + 0.20:
        return candidate, True
    return aligned, False


def _template_marker_score(gray_img: np.ndarray) -> float:
    """Measure how many expected registration squares align with the template."""
    h, w = gray_img.shape[:2]
    matched = 0
    total = 0
    for marker in ACTIVE_LAYOUT["markers"]:
        cx, cy = int(round(marker["x"])), int(round(marker["y"]))
        radius = max(3, int(round(marker["size"] * 0.30)))
        outer = max(radius + 2, int(round(marker["size"] * 0.60)))
        if cx - outer < 0 or cy - outer < 0 or cx + outer >= w or cy + outer >= h:
            continue
        roi = gray_img[cy-outer:cy+outer+1, cx-outer:cx+outer+1]
        yy, xx = np.ogrid[-outer:outer+1, -outer:outer+1]
        d2 = xx*xx + yy*yy
        center = roi[d2 <= radius*radius]
        paper = roi[(d2 >= (radius+2)**2) & (d2 <= outer*outer)]
        matched += float(np.mean(center) < 180 and np.mean(paper)-np.mean(center) >= 8)
        total += 1
    return matched / total if total else 0.0


def _warp_portrait(
    img: np.ndarray,
    ordered_pts: np.ndarray,
    use_markers: bool,
) -> Tuple[np.ndarray, bool, bool]:
    """Warp a page upright and resolve its 180-degree orientation."""
    portrait_pts, is_landscape = _portrait_quad(ordered_pts)
    destination = DST_MARKER_CENTERS if use_markers else DST_PAPER_CORNERS

    def warp(points: np.ndarray) -> np.ndarray:
        matrix = cv2.getPerspectiveTransform(points.astype(np.float32), destination)
        return cv2.warpPerspective(img, matrix, (STANDARD_WIDTH, STANDARD_HEIGHT))

    aligned = warp(portrait_pts)
    reversed_pts = np.roll(portrait_pts, 2, axis=0)
    reversed_aligned = warp(reversed_pts)
    aligned_gray = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY) if len(aligned.shape) == 3 else aligned
    reversed_gray = cv2.cvtColor(reversed_aligned, cv2.COLOR_BGR2GRAY) if len(reversed_aligned.shape) == 3 else reversed_aligned
    aligned_layout_score = _layout_orientation_score(aligned_gray)
    reversed_layout_score = _layout_orientation_score(reversed_gray)
    if abs(aligned_layout_score - reversed_layout_score) >= 0.10:
        if reversed_layout_score > aligned_layout_score:
            return reversed_aligned, is_landscape, True
        return aligned, is_landscape, False
    if _orientation_score(reversed_gray) > _orientation_score(aligned_gray):
        return reversed_aligned, is_landscape, True
    return aligned, is_landscape, False


def align_paper(image_input) -> Tuple[bool, Optional[np.ndarray], str]:
    """
    Hàm thực hiện Tiền xử lý và Căn chỉnh phối cảnh (Perspective Transform):
      1. Đọc ảnh đầu vào
      2. Chuyển Grayscale
      3. Tìm 4 Marker định vị hoặc viền mép giấy rồi cắt và nắn phẳng phiếu
      4. Warp Perspective về kích thước chuẩn của layout đang hoạt động
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
        aligned, is_landscape, was_reversed = _warp_portrait(img, marker_pts, use_markers=True)
        aligned, template_refined = _choose_alignment(img, aligned)
        if template_refined:
            return True, aligned, "Căn chỉnh thành công bằng đối chiếu đặc trưng FormTHPT50."
        if was_reversed and is_landscape:
            return True, aligned, "Căn chỉnh thành công bằng 4 Marker; đã tự xoay ảnh chụp ngang."
        if was_reversed:
            return True, aligned, "Căn chỉnh thành công bằng 4 Marker; đã xoay ảnh bị ngược 180 độ."
        if is_landscape:
            return True, aligned, "Căn chỉnh thành công bằng 4 Marker; đã tự xoay ảnh chụp ngang."
        return True, aligned, "Căn chỉnh thành công bằng 4 Marker định vị góc."

    # Bước 2: Dự phòng phát hiện viền tờ phiếu (Paper contour detection)
    paper_pts = find_paper_contour(gray)
    if paper_pts is not None and len(paper_pts) == 4:
        aligned, is_landscape, was_reversed = _warp_portrait(img, paper_pts, use_markers=False)
        aligned, template_refined = _choose_alignment(img, aligned)
        if template_refined:
            return True, aligned, "Căn chỉnh thành công bằng đối chiếu đặc trưng FormTHPT50."
        if was_reversed and is_landscape:
            return True, aligned, "Căn chỉnh thành công bằng viền phiếu; đã tự xoay ảnh chụp ngang."
        if was_reversed:
            return True, aligned, "Căn chỉnh thành công bằng viền phiếu; đã xoay ảnh bị ngược 180 độ."
        if is_landscape:
            return True, aligned, "Căn chỉnh thành công bằng viền phiếu; đã tự xoay ảnh chụp ngang."
        return True, aligned, "Căn chỉnh thành công bằng đường viền phiếu."

    template_aligned = _template_feature_alignment(img)
    if template_aligned is not None:
        template_gray = (
            cv2.cvtColor(template_aligned, cv2.COLOR_BGR2GRAY)
            if template_aligned.ndim == 3 else template_aligned
        )
        if (
            _layout_orientation_score(template_gray) >= 0.50
            or (
                _layout_orientation_score(template_gray) >= 0.35
                and _template_marker_score(template_gray) >= 0.80
            )
        ):
            return True, template_aligned, "Căn chỉnh thành công bằng đối chiếu đặc trưng FormTHPT50."

    return False, None, "Không tìm thấy 4 marker định vị hoặc viền phiếu hợp lệ. Vui lòng chụp rõ toàn bộ 4 góc phiếu!"
