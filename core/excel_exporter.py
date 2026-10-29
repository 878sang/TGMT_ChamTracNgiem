"""
Module: excel_exporter.py
Phụ trách: Xuất báo cáo kết quả thi ra file Excel hoàn chỉnh gồm 3 Sheet:
  - Sheet 1: Bảng điểm tổng hợp
  - Sheet 2: Chi tiết bài làm của từng học sinh
  - Sheet 3: Thống kê phổ điểm & ma trận câu hỏi
Hỗ trợ cả 2 chế độ: Full trắc nghiệm và Chuẩn THPT mới BGD&ĐT.
"""

import os
from typing import List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from core.models import Exam, Submission, ExamMode


def get_grade_rank(score: float) -> str:
    if score >= 8.0:
        return "Giỏi"
    elif score >= 6.5:
        return "Khá"
    elif score >= 5.0:
        return "Trung bình"
    else:
        return "Chưa đạt"


def export_exam_results_to_excel(exam: Exam, submissions: List[Submission], output_filepath: str) -> bool:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
        wb = openpyxl.Workbook()

        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        sec_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
        stripe_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
        green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
        red_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

        white_title_font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
        white_header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        bold_font = Font(name="Arial", size=11, bold=True)
        center_al = Alignment(horizontal="center", vertical="center")

        thin_border = Border(
            left=Side(style="thin", color="D9D9D9"), right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"), bottom=Side(style="thin", color="D9D9D9")
        )

        # -------------------------------------------------------------
        # SHEET 1: BẢNG ĐIỂM TỔNG HỢP
        # -------------------------------------------------------------
        ws1 = wb.active
        ws1.title = "Bang_Diem_Tong_Hop"

        mode_desc = "TRẮC NGHIỆM 4 LỰA CHỌN" if exam.mode == ExamMode.FULL_MCQ else "CHUẨN THI THPT MỚI BGD&ĐT"
        ws1.merge_cells("A1:I1")
        ws1["A1"] = f"BẢNG KẾT QUẢ ĐIỂM THI: {exam.title.upper()} ({mode_desc})"
        ws1["A1"].font = white_title_font
        ws1["A1"].fill = header_fill
        ws1["A1"].alignment = center_al

        ws1.merge_cells("A2:I2")
        ws1["A2"] = f"Môn: {exam.subject} | Lớp: {exam.class_name} | Ngày tạo: {exam.created_at} | Tổng số bài: {len(submissions)}"
        ws1["A2"].font = Font(name="Arial", size=10, italic=True)
        ws1["A2"].alignment = center_al

        if exam.mode == ExamMode.FULL_MCQ:
            headers1 = ["STT", "Mã HS / SBD", "Họ và tên", "Mã đề", "Số câu đúng", "Số câu sai", "Bỏ trống", "Điểm số", "Xếp loại"]
        else:
            headers1 = ["STT", "SBD", "Họ và tên", "Mã đề", "Điểm P1 (3đ)", "Điểm P2 (4đ)", "Điểm P3 (3đ)", "Tổng điểm", "Xếp loại"]

        for col_idx, h in enumerate(headers1, 1):
            cell = ws1.cell(row=4, column=col_idx, value=h)
            cell.font = white_header_font
            cell.fill = sec_fill
            cell.alignment = center_al
        ws1.row_dimensions[4].height = 25

        for idx, sub in enumerate(submissions, start=1):
            row_idx = idx + 4
            stt = idx
            sid = sub.student_id or f"HS_{idx:03d}"
            name = sub.student_name or f"Học sinh {idx}"
            code = sub.exam_code or "101"
            rank = get_grade_rank(sub.total_score)

            if exam.mode == ExamMode.FULL_MCQ:
                vals = [stt, sid, name, code, sub.correct_count, sub.wrong_count, sub.blank_count, sub.total_score, rank]
            else:
                vals = [stt, sid, name, code, sub.score_part1, sub.score_part2, sub.score_part3, sub.total_score, rank]

            for c_idx, val in enumerate(vals, 1):
                cell = ws1.cell(row=row_idx, column=c_idx, value=val)
                cell.alignment = center_al
                cell.border = thin_border
                if c_idx in (8, 9):  # Cột điểm và xếp loại
                    cell.font = bold_font
                if idx % 2 == 0:
                    cell.fill = stripe_fill

        for c_letter in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
            ws1.column_dimensions[c_letter].width = 16
        ws1.column_dimensions["C"].width = 24

        # -------------------------------------------------------------
        # SHEET 2: BẢNG CHI TIẾT BÀI LÀM
        # -------------------------------------------------------------
        ws2 = wb.create_sheet(title="Chi_Tiet_Bai_Lam")
        ws2["A1"] = "BẢNG CHI TIẾT BÀI LÀM TỪNG THÍ SINH"
        ws2["A1"].font = white_title_font
        ws2["A1"].fill = header_fill
        ws2.merge_cells("A1:F1")
        ws2["A1"].alignment = center_al

        if exam.mode == ExamMode.FULL_MCQ:
            num_q = exam.num_questions or 40
            headers2 = ["STT", "Mã HS", "Họ tên", "Mã đề"] + [f"C{i}" for i in range(1, num_q + 1)]
            for col_idx, h in enumerate(headers2, 1):
                c = ws2.cell(row=3, column=col_idx, value=h)
                c.font = white_header_font
                c.fill = sec_fill
                c.alignment = center_al

            for idx, sub in enumerate(submissions, start=1):
                r = idx + 3
                ws2.cell(row=r, column=1, value=idx).alignment = center_al
                ws2.cell(row=r, column=2, value=sub.student_id).alignment = center_al
                ws2.cell(row=r, column=3, value=sub.student_name).alignment = center_al
                ws2.cell(row=r, column=4, value=sub.exam_code).alignment = center_al
                
                # Chi tiết câu hỏi
                ans_map = sub.extracted_data.get("answers", {}) if isinstance(sub.extracted_data, dict) else {}
                for q_i in range(1, num_q + 1):
                    val = ans_map.get(q_i) or ans_map.get(str(q_i)) or "-"
                    c = ws2.cell(row=r, column=4 + q_i, value=str(val))
                    c.alignment = center_al
                    c.border = thin_border
        else:
            # Mode THPT 2025: 12 câu P1 + 4 câu P2 (16 ý) + 6 câu P3
            headers2 = ["STT", "SBD", "Họ tên", "Mã đề"]
            # Thêm header P1
            headers2 += [f"P1_C{i}" for i in range(1, 13)]
            # Thêm header P2
            for q_i in range(1, 5):
                for s_i in ['a', 'b', 'c', 'd']:
                    headers2.append(f"P2_C{q_i}{s_i}")
            # Thêm header P3
            headers2 += [f"P3_C{i}" for i in range(1, 7)]

            for col_idx, h in enumerate(headers2, 1):
                c = ws2.cell(row=3, column=col_idx, value=h)
                c.font = Font(name="Arial", size=9, bold=True, color="FFFFFF")
                c.fill = sec_fill
                c.alignment = center_al

            for idx, sub in enumerate(submissions, start=1):
                r = idx + 3
                ws2.cell(row=r, column=1, value=idx).alignment = center_al
                ws2.cell(row=r, column=2, value=sub.student_id).alignment = center_al
                ws2.cell(row=r, column=3, value=sub.student_name).alignment = center_al
                ws2.cell(row=r, column=4, value=sub.exam_code).alignment = center_al

                col_pointer = 5
                p1_data = sub.extracted_data.get("part1", {})
                for q_i in range(1, 13):
                    v = p1_data.get(q_i) or p1_data.get(str(q_i)) or "-"
                    c = ws2.cell(row=r, column=col_pointer, value=str(v))
                    c.alignment = center_al; c.border = thin_border
                    col_pointer += 1

                p2_data = sub.extracted_data.get("part2", {})
                for q_i in range(1, 5):
                    q_subs = p2_data.get(q_i) or p2_data.get(str(q_i)) or {}
                    for s_i in ['a', 'b', 'c', 'd']:
                        v = q_subs.get(s_i) or "-"
                        c = ws2.cell(row=r, column=col_pointer, value=str(v))
                        c.alignment = center_al; c.border = thin_border
                        col_pointer += 1

                p3_data = sub.extracted_data.get("part3", {})
                for q_i in range(1, 7):
                    v = p3_data.get(q_i) or p3_data.get(str(q_i)) or "-"
                    c = ws2.cell(row=r, column=col_pointer, value=str(v))
                    c.alignment = center_al; c.border = thin_border
                    col_pointer += 1

        # -------------------------------------------------------------
        # SHEET 3: THỐNG KÊ PHỔ ĐIỂM
        # -------------------------------------------------------------
        ws3 = wb.create_sheet(title="Thong_Ke_Pho_Diem")
        ws3.merge_cells("A1:D1")
        ws3["A1"] = "BẢNG THỐNG KÊ CHẤT LƯỢNG BÀI THI"
        ws3["A1"].font = white_title_font
        ws3["A1"].fill = header_fill
        ws3["A1"].alignment = center_al

        scores = [s.total_score for s in submissions] if submissions else [0.0]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        max_s = max(scores) if scores else 0.0
        min_s = min(scores) if scores else 0.0

        cnt_gioi = sum(1 for s in scores if s >= 8.0)
        cnt_kha = sum(1 for s in scores if 6.5 <= s < 8.0)
        cnt_tb = sum(1 for s in scores if 5.0 <= s < 6.5)
        cnt_yeu = sum(1 for s in scores if s < 5.0)

        stats_data = [
            ("Tổng số bài đã chấm", len(submissions)),
            ("Điểm trung bình", avg_score),
            ("Điểm cao nhất", max_s),
            ("Điểm thấp nhất", min_s),
            ("Số bài Giỏi (>= 8.0)", f"{cnt_gioi} ({cnt_gioi/max(len(submissions),1)*100:.1f}%)"),
            ("Số bài Khá (6.5 - 7.9)", f"{cnt_kha} ({cnt_kha/max(len(submissions),1)*100:.1f}%)"),
            ("Số bài Trung bình (5.0 - 6.4)", f"{cnt_tb} ({cnt_tb/max(len(submissions),1)*100:.1f}%)"),
            ("Số bài Chưa đạt (< 5.0)", f"{cnt_yeu} ({cnt_yeu/max(len(submissions),1)*100:.1f}%)")
        ]

        ws3.cell(row=3, column=1, value="Chỉ số").font = white_header_font
        ws3.cell(row=3, column=1).fill = sec_fill
        ws3.cell(row=3, column=2, value="Giá trị").font = white_header_font
        ws3.cell(row=3, column=2).fill = sec_fill

        for idx, (label, val) in enumerate(stats_data, start=4):
            c1 = ws3.cell(row=idx, column=1, value=label)
            c2 = ws3.cell(row=idx, column=2, value=val)
            c1.border = thin_border
            c2.border = thin_border
            c2.alignment = center_al
            c2.font = bold_font
            if idx % 2 == 0:
                c1.fill = stripe_fill
                c2.fill = stripe_fill

        ws3.column_dimensions["A"].width = 30
        ws3.column_dimensions["B"].width = 20

        wb.save(output_filepath)
        return True
    except Exception as e:
        print(f"Lỗi khi xuất báo cáo Excel: {e}")
        return False
