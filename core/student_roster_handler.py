"""
Module: student_roster_handler.py
Quản lý Danh sách Thí sinh / Học sinh theo Số Báo Danh (SBD) từ file Excel.
Chức năng:
  - Đọc (Import) danh sách học sinh từ file Excel (.xlsx, .xls)
  - Tự động chuẩn hóa SBD (hỗ trợ cả SBD 6 số '000001' và số ngắn '001', '1')
  - Tự động tra cứu Họ tên & Lớp của học sinh khi máy quét đọc được SBD OMR
  - Xuất file mẫu danh sách học sinh chuyên nghiệp để giáo viên sử dụng
"""

import os
import sys
from typing import Dict, Any, Tuple, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def normalize_sbd_key(sbd_raw: Any) -> str:
    """Chuẩn hóa chuỗi SBD: bỏ khoảng trắng và chuẩn hóa về dạng chữ số"""
    if sbd_raw is None:
        return ""
    s = str(sbd_raw).strip()
    # Nếu là float trong excel (ví dụ 1.0) -> '1'
    try:
        f = float(s)
        if f.is_integer():
            s = str(int(f))
    except ValueError:
        pass
    return "".join([c for c in s if c.isdigit()])


def import_student_roster_from_excel(filepath: str) -> Dict[str, Dict[str, str]]:
    """
    Đọc danh sách học sinh từ file Excel.
    Cột nhận diện linh hoạt:
      - SBD: 'SBD', 'Số báo danh', 'Mã HS', 'Mã thí sinh', 'ID'
      - Họ tên: 'Họ và tên', 'Họ tên', 'Tên học sinh', 'Tên thí sinh', 'Họ và Tên'
      - Lớp: 'Lớp', 'Lớp học', 'Class'
    Trả về mapping:
      {
         "000001": {"name": "Nguyễn Văn An", "class": "12A1"},
         "1": {"name": "Nguyễn Văn An", "class": "12A1"},  # Hỗ trợ tra cứu nhanh
         ...
      }
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Không tìm thấy file: {filepath}")

    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active

    roster: Dict[str, Dict[str, str]] = {}
    col_sbd = -1
    col_name = -1
    col_class = -1
    header_row = -1

    # Tìm dòng tiêu đề
    for row_idx in range(1, min(15, ws.max_row + 1)):
        row_vals = [str(ws.cell(row=row_idx, column=c).value or "").strip().lower() for c in range(1, ws.max_column + 1)]
        for c_idx, val in enumerate(row_vals, 1):
            if any(k in val for k in ["sbd", "số báo danh", "so bao danh", "mã hs", "ma hs"]):
                col_sbd = c_idx
            elif any(k in val for k in ["họ và tên", "ho va ten", "họ tên", "ho ten", "tên học sinh", "ten"]):
                col_name = c_idx
            elif any(k in val for k in ["lớp", "lop", "class"]):
                col_class = c_idx

        if col_sbd != -1 and col_name != -1:
            header_row = row_idx
            break

    # Nếu không tìm thấy header rõ ràng, mặc định Cột A: SBD, Cột B: Họ tên, Cột C: Lớp
    if col_sbd == -1 or col_name == -1:
        col_sbd = 1
        col_name = 2
        col_class = 3
        header_row = 1

    # Đọc dữ liệu từ các hàng tiếp theo
    for row_idx in range(header_row + 1, ws.max_row + 1):
        raw_sbd = ws.cell(row=row_idx, column=col_sbd).value
        raw_name = ws.cell(row=row_idx, column=col_name).value
        raw_cls = ws.cell(row=row_idx, column=col_class).value if col_class != -1 else ""

        if raw_sbd is None or raw_name is None:
            continue

        clean_sbd = normalize_sbd_key(raw_sbd)
        clean_name = str(raw_name).strip()
        clean_cls = str(raw_cls or "").strip()

        if not clean_sbd or not clean_name:
            continue

        info = {"name": clean_name, "class": clean_cls, "sbd": clean_sbd}

        # Lưu cả dạng 6 số '000001', 3 số '001', và số rút gọn '1' để tra cứu không trượt
        sbd_6 = clean_sbd.zfill(6)
        sbd_3 = clean_sbd.zfill(3)
        sbd_short = clean_sbd.lstrip("0") or "0"

        roster[sbd_6] = info
        roster[sbd_3] = info
        roster[sbd_short] = info
        roster[clean_sbd] = info

    return roster


def lookup_student_in_roster(sbd: str, roster: Dict[str, Dict[str, str]]) -> Tuple[str, str]:
    """
    Tra cứu thí sinh từ SBD.
    Trả về: (Họ_và_tên, Lớp) hoặc ("", "") nếu không tìm thấy.
    """
    if not roster or not sbd:
        return "", ""

    clean = normalize_sbd_key(sbd)
    sbd_6 = clean.zfill(6)
    sbd_short = clean.lstrip("0") or "0"

    for candidate in [clean, sbd_6, sbd_short]:
        if candidate in roster:
            item = roster[candidate]
            return item.get("name", ""), item.get("class", "")

    return "", ""


def export_sample_roster_to_excel(output_filepath: str) -> bool:
    """
    Tạo file Excel mẫu danh sách học sinh chuẩn gồm các cột:
      STT, Số Báo Danh (SBD), Họ và Tên, Lớp, Ghi Chú
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Danh_Sach_Hoc_Sinh"

        # Tiêu đề chính
        ws.merge_cells("A1:E1")
        ws["A1"] = "DANH SÁCH HỌC SINH THI TRẮC NGHIỆM"
        ws["A1"].font = Font(name="Arial", size=14, bold=True, color="FFFFFF")
        ws["A1"].fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 32

        # Ghi chú hướng dẫn
        ws.merge_cells("A2:E2")
        ws["A2"] = "Hướng dẫn: Nhập SBD và Họ Tên học sinh. Hệ thống sẽ tự động đối chiếu SBD trên bài làm OMR để lấy đúng Họ Tên."
        ws["A2"].font = Font(name="Arial", size=9, italic=True)
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 20

        # Header cột
        headers = ["STT", "Số Báo Danh (SBD)", "Họ và Tên Thí Sinh", "Lớp", "Ghi Chú"]
        for c_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=3, column=c_idx, value=h)
            cell.font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 25

        # Dữ liệu mẫu 5 học sinh
        samples = [
            (1, "000001", "Nguyễn Văn An", "12A1", "Học sinh chính thức"),
            (2, "000002", "Lê Thị Cúc", "12A1", "Học sinh chính thức"),
            (3, "000003", "Trần Văn Dũng", "12A1", "Học sinh chính thức"),
            (4, "000011", "Trần Thị Bình", "Khối 12", "Thí sinh thi THPT"),
            (5, "000012", "Hoàng Minh Châu", "Khối 12", "Thí sinh thi THPT"),
        ]

        thin_border = Border(
            left=Side(style="thin", color="D9D9D9"), right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"), bottom=Side(style="thin", color="D9D9D9")
        )
        stripe_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")

        for r_i, (stt, sbd, name, cls_name, note) in enumerate(samples, start=4):
            vals = [stt, sbd, name, cls_name, note]
            for c_i, val in enumerate(vals, 1):
                cell = ws.cell(row=r_i, column=c_i, value=val)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center" if c_i in (1, 2, 4) else "left", vertical="center")
                if r_i % 2 == 0:
                    cell.fill = stripe_fill

        ws.column_dimensions["A"].width = 8
        ws.column_dimensions["B"].width = 20
        ws.column_dimensions["C"].width = 28
        ws.column_dimensions["D"].width = 14
        ws.column_dimensions["E"].width = 25

        wb.save(output_filepath)
        return True
    except Exception as e:
        print(f"Lỗi tạo file mẫu danh sách học sinh: {e}")
        return False
