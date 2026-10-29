"""
Module: excel_exporter.py
Phụ trách: Xuất báo cáo kết quả thi ra file Excel hoàn chỉnh gồm 3 Sheet:
  - Sheet 1: Bảng điểm tổng hợp (SBD, Họ tên, Mã đề, Điểm thành phần, Điểm tổng, Xếp loại, Trạng thái)
  - Sheet 2: Bảng chi tiết bài làm của từng học sinh theo từng câu hỏi
  - Sheet 3: Thống kê phổ điểm, chỉ số chất lượng, và tỷ lệ đúng/sai chi tiết theo từng câu & từng phần thi
Hỗ trợ cả 2 chế độ: Full trắc nghiệm và Chuẩn THPT mới BGD&ĐT.
Tuân thủ: Không đưa bài lỗi vào thống kê điểm số chung của lớp.
"""

import os
from typing import List, Dict, Any, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from core.models import Exam, Submission, ExamMode
from core.grading_engine import normalize_numeric_string


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
        yellow_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        red_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

        white_title_font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
        white_header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        sub_title_font = Font(name="Arial", size=11, bold=True, color="1F4E78")
        bold_font = Font(name="Arial", size=11, bold=True)
        center_al = Alignment(horizontal="center", vertical="center")
        left_al = Alignment(horizontal="left", vertical="center")

        thin_border = Border(
            left=Side(style="thin", color="D9D9D9"), right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"), bottom=Side(style="thin", color="D9D9D9")
        )

        # Phân loại bài nộp:
        valid_submissions = [s for s in submissions if s.status != "Lỗi"]
        error_submissions = [s for s in submissions if s.status == "Lỗi"]
        review_submissions = [s for s in submissions if s.status == "Cần kiểm tra"]
        # Bài có điểm hợp lệ (không lỗi và có mã đề hợp lệ)
        scored_submissions = [
            s for s in valid_submissions 
            if s.status == "Đã chấm" or (s.status == "Cần kiểm tra" and (s.exam_code in (exam.answer_keys or {})))
        ]

        # -------------------------------------------------------------
        # SHEET 1: BẢNG ĐIỂM TỔNG HỢP
        # -------------------------------------------------------------
        ws1 = wb.active
        ws1.title = "Bang_Diem_Tong_Hop"

        mode_desc = f"TRẮC NGHIỆM ({exam.num_questions or 40} CÂU)" if exam.mode == ExamMode.FULL_MCQ else "CHUẨN THI THPT MỚI BGD&ĐT (3 PHẦN)"
        ws1.merge_cells("A1:J1")
        ws1["A1"] = f"BẢNG KẾT QUẢ ĐIỂM THI: {exam.title.upper()} ({mode_desc})"
        ws1["A1"].font = white_title_font
        ws1["A1"].fill = header_fill
        ws1["A1"].alignment = center_al

        ws1.merge_cells("A2:J2")
        ws1["A2"] = (
            f"Môn: {exam.subject} | Lớp: {exam.class_name} | Ngày tạo: {exam.created_at} | "
            f"Tổng số bài: {len(submissions)} (Hợp lệ: {len(valid_submissions)} | Cần kiểm tra: {len(review_submissions)} | Lỗi: {len(error_submissions)})"
        )
        ws1["A2"].font = Font(name="Arial", size=10, italic=True)
        ws1["A2"].alignment = center_al

        if exam.mode == ExamMode.FULL_MCQ:
            headers1 = ["STT", "Mã HS / SBD", "Họ và tên", "Mã đề", "Số câu đúng", "Số câu sai", "Bỏ trống", "Điểm số", "Xếp loại", "Trạng thái & Ghi chú"]
        else:
            headers1 = ["STT", "SBD", "Họ và tên", "Mã đề", "Điểm P1 (3đ)", "Điểm P2 (4đ)", "Điểm P3 (3đ)", "Tổng điểm", "Xếp loại", "Trạng thái & Ghi chú"]

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
            code = sub.exam_code or "???"

            if sub.status == "Lỗi":
                status_note = f"Lỗi: {sub.error_message or 'Không đọc được bài làm'}"
                if exam.mode == ExamMode.FULL_MCQ:
                    vals = [stt, sid, name, code, "-", "-", "-", "-", "Lỗi", status_note]
                else:
                    vals = [stt, sid, name, code, "-", "-", "-", "-", "Lỗi", status_note]
            else:
                rank = get_grade_rank(sub.total_score)
                status_note = "Đã chấm" if sub.status == "Đã chấm" else f"Cần kiểm tra ({sub.error_message})"
                if exam.mode == ExamMode.FULL_MCQ:
                    vals = [stt, sid, name, code, sub.correct_count, sub.wrong_count, sub.blank_count, sub.total_score, rank, status_note]
                else:
                    vals = [stt, sid, name, code, sub.score_part1, sub.score_part2, sub.score_part3, sub.total_score, rank, status_note]

            for c_idx, val in enumerate(vals, 1):
                cell = ws1.cell(row=row_idx, column=c_idx, value=val)
                cell.alignment = left_al if c_idx == 10 else center_al
                cell.border = thin_border
                if c_idx in (8, 9):
                    cell.font = bold_font
                if sub.status == "Lỗi":
                    cell.fill = red_fill
                elif sub.status == "Cần kiểm tra":
                    cell.fill = yellow_fill
                elif idx % 2 == 0:
                    cell.fill = stripe_fill

        for c_letter in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
            ws1.column_dimensions[c_letter].width = 16
        ws1.column_dimensions["C"].width = 24
        ws1.column_dimensions["J"].width = 38

        # -------------------------------------------------------------
        # SHEET 2: BẢNG CHI TIẾT BÀI LÀM
        # -------------------------------------------------------------
        ws2 = wb.create_sheet(title="Chi_Tiet_Bai_Lam")
        ws2["A1"] = "BẢNG CHI TIẾT ĐÁP ÁN BÀI LÀM TỪNG THÍ SINH"
        ws2["A1"].font = white_title_font
        ws2["A1"].fill = header_fill
        ws2.merge_cells("A1:F1")
        ws2["A1"].alignment = center_al

        if exam.mode == ExamMode.FULL_MCQ:
            num_q = exam.num_questions or 40
            headers2 = ["STT", "Mã HS", "Họ tên", "Mã đề", "Trạng thái"] + [f"C{i}" for i in range(1, num_q + 1)]
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
                ws2.cell(row=r, column=5, value=sub.status).alignment = center_al

                ans_map = sub.extracted_data.get("answers", {}) if isinstance(sub.extracted_data, dict) else {}
                for q_i in range(1, num_q + 1):
                    val = ans_map.get(q_i) or ans_map.get(str(q_i)) or ("Lỗi" if sub.status == "Lỗi" else "-")
                    if isinstance(val, list):
                        val = "/".join(val)
                    c = ws2.cell(row=r, column=5 + q_i, value=str(val))
                    c.alignment = center_al
                    c.border = thin_border
        else:
            headers2 = ["STT", "SBD", "Họ tên", "Mã đề", "Trạng thái"]
            headers2 += [f"P1_C{i}" for i in range(1, 13)]
            for q_i in range(1, 5):
                for s_i in ['a', 'b', 'c', 'd']:
                    headers2.append(f"P2_C{q_i}{s_i}")
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
                ws2.cell(row=r, column=5, value=sub.status).alignment = center_al

                col_pointer = 6
                p1_data = sub.extracted_data.get("part1", {}) if isinstance(sub.extracted_data, dict) else {}
                for q_i in range(1, 13):
                    v = p1_data.get(q_i) or p1_data.get(str(q_i)) or ("Lỗi" if sub.status == "Lỗi" else "-")
                    if isinstance(v, list):
                        v = "/".join(v)
                    c = ws2.cell(row=r, column=col_pointer, value=str(v))
                    c.alignment = center_al; c.border = thin_border
                    col_pointer += 1

                p2_data = sub.extracted_data.get("part2", {}) if isinstance(sub.extracted_data, dict) else {}
                for q_i in range(1, 5):
                    q_subs = p2_data.get(q_i) or p2_data.get(str(q_i)) or {}
                    for s_i in ['a', 'b', 'c', 'd']:
                        v = q_subs.get(s_i) or ("Lỗi" if sub.status == "Lỗi" else "-")
                        c = ws2.cell(row=r, column=col_pointer, value=str(v))
                        c.alignment = center_al; c.border = thin_border
                        col_pointer += 1

                p3_data = sub.extracted_data.get("part3", {}) if isinstance(sub.extracted_data, dict) else {}
                for q_i in range(1, 7):
                    v = p3_data.get(q_i) or p3_data.get(str(q_i)) or ("Lỗi" if sub.status == "Lỗi" else "-")
                    c = ws2.cell(row=r, column=col_pointer, value=str(v))
                    c.alignment = center_al; c.border = thin_border
                    col_pointer += 1

        # -------------------------------------------------------------
        # SHEET 3: THỐNG KÊ PHỔ ĐIỂM & TỶ LỆ ĐÚNG/SAI THEO TỪNG CÂU
        # -------------------------------------------------------------
        ws3 = wb.create_sheet(title="Thong_Ke_Pho_Diem")
        ws3.merge_cells("A1:G1")
        ws3["A1"] = f"BÁO CÁO THỐNG KÊ CHẤT LƯỢNG KỲ THI: {exam.title.upper()}"
        ws3["A1"].font = white_title_font
        ws3["A1"].fill = header_fill
        ws3["A1"].alignment = center_al

        # 1. Chỉ số tổng quan (chỉ tính trên bài thi hợp lệ)
        scores = [s.total_score for s in scored_submissions]
        num_scored = len(scores)
        avg_score = round(sum(scores) / max(num_scored, 1), 2) if num_scored else 0.0
        max_s = max(scores) if scores else 0.0
        min_s = min(scores) if scores else 0.0

        cnt_gioi = sum(1 for s in scores if s >= 8.0)
        cnt_kha = sum(1 for s in scores if 6.5 <= s < 8.0)
        cnt_tb = sum(1 for s in scores if 5.0 <= s < 6.5)
        cnt_yeu = sum(1 for s in scores if s < 5.0)

        stats_summary = [
            ("Tổng số bài thi tiếp nhận", len(submissions)),
            ("Số bài chấm thành công (hợp lệ)", len(scored_submissions)),
            ("Số bài nghi vấn (Cần kiểm tra)", len(review_submissions)),
            ("Số bài lỗi (không chấm được)", len(error_submissions)),
            ("Điểm trung bình (chỉ tính bài hợp lệ)", avg_score),
            ("Điểm cao nhất", max_s),
            ("Điểm thấp nhất", min_s),
            ("Số bài Giỏi (>= 8.0 điểm)", f"{cnt_gioi} ({cnt_gioi/max(num_scored,1)*100:.1f}%)"),
            ("Số bài Khá (6.5 - 7.9 điểm)", f"{cnt_kha} ({cnt_kha/max(num_scored,1)*100:.1f}%)"),
            ("Số bài Trung bình (5.0 - 6.4 điểm)", f"{cnt_tb} ({cnt_tb/max(num_scored,1)*100:.1f}%)"),
            ("Số bài Chưa đạt (< 5.0 điểm)", f"{cnt_yeu} ({cnt_yeu/max(num_scored,1)*100:.1f}%)")
        ]

        ws3.merge_cells("A3:B3")
        ws3["A3"] = "I. CHỈ SỐ KPI CHẤT LƯỢNG KỲ THI"
        ws3["A3"].font = sub_title_font

        ws3.cell(row=4, column=1, value="Chỉ số đánh giá").font = white_header_font
        ws3.cell(row=4, column=1).fill = sec_fill
        ws3.cell(row=4, column=2, value="Giá trị thống kê").font = white_header_font
        ws3.cell(row=4, column=2).fill = sec_fill

        for idx, (label, val) in enumerate(stats_summary, start=5):
            c1 = ws3.cell(row=idx, column=1, value=label)
            c2 = ws3.cell(row=idx, column=2, value=val)
            c1.border = thin_border
            c2.border = thin_border
            c2.alignment = center_al
            c2.font = bold_font
            if idx % 2 == 0:
                c1.fill = stripe_fill
                c2.fill = stripe_fill

        # 2. Bảng phổ điểm theo khoảng (0-10)
        curr_row = 5 + len(stats_summary) + 2
        ws3.merge_cells(f"A{curr_row}:C{curr_row}")
        ws3[f"A{curr_row}"] = "II. BẢNG PHỔ ĐIỂM CHI TIẾT (KHOẢNG 1.0 ĐIỂM)"
        ws3[f"A{curr_row}"].font = sub_title_font
        curr_row += 1

        dist_headers = ["Khoảng điểm", "Số lượng bài", "Tỷ lệ (%)"]
        for c_i, h in enumerate(dist_headers, 1):
            cell = ws3.cell(row=curr_row, column=c_i, value=h)
            cell.font = white_header_font
            cell.fill = sec_fill
            cell.alignment = center_al
        curr_row += 1

        score_ranges = [
            ("[0.0 - 1.0)", lambda s: 0.0 <= s < 1.0),
            ("[1.0 - 2.0)", lambda s: 1.0 <= s < 2.0),
            ("[2.0 - 3.0)", lambda s: 2.0 <= s < 3.0),
            ("[3.0 - 4.0)", lambda s: 3.0 <= s < 4.0),
            ("[4.0 - 5.0)", lambda s: 4.0 <= s < 5.0),
            ("[5.0 - 6.0)", lambda s: 5.0 <= s < 6.0),
            ("[6.0 - 7.0)", lambda s: 6.0 <= s < 7.0),
            ("[7.0 - 8.0)", lambda s: 7.0 <= s < 8.0),
            ("[8.0 - 9.0)", lambda s: 8.0 <= s < 9.0),
            ("[9.0 - 10.0]", lambda s: 9.0 <= s <= 10.0),
        ]

        for label_range, fn_filter in score_ranges:
            cnt_in_range = sum(1 for s in scores if fn_filter(s))
            pct_in_range = (cnt_in_range / max(num_scored, 1)) * 100.0
            r_vals = [label_range, cnt_in_range, f"{pct_in_range:.1f}%"]
            for c_i, val in enumerate(r_vals, 1):
                cell = ws3.cell(row=curr_row, column=c_i, value=val)
                cell.alignment = center_al
                cell.border = thin_border
            curr_row += 1

        # 3. Tỷ lệ đúng / sai theo từng câu hỏi & từng phần thi
        curr_row += 2
        ws3.merge_cells(f"A{curr_row}:G{curr_row}")
        ws3[f"A{curr_row}"] = "III. MA TRẬN & TỶ LỆ ĐÚNG / SAI THEO TỪNG CÂU HỎI"
        ws3[f"A{curr_row}"].font = sub_title_font
        curr_row += 1

        q_headers = ["Câu hỏi", "Số bài Đúng", "Tỷ lệ Đúng (%)", "Số bài Sai", "Tỷ lệ Sai (%)", "Bỏ trống", "Tỷ lệ Trống (%)"]
        for c_i, h in enumerate(q_headers, 1):
            cell = ws3.cell(row=curr_row, column=c_i, value=h)
            cell.font = white_header_font
            cell.fill = sec_fill
            cell.alignment = center_al
        curr_row += 1

        if exam.mode == ExamMode.FULL_MCQ:
            num_q = exam.num_questions or 40
            for q_num in range(1, num_q + 1):
                n_correct = 0
                n_wrong = 0
                n_blank = 0

                for sub in scored_submissions:
                    ans_map = sub.extracted_data.get("answers", {}) if isinstance(sub.extracted_data, dict) else {}
                    st_val = ans_map.get(q_num) or ans_map.get(str(q_num))
                    sub_key = (exam.answer_keys or {}).get(sub.exam_code, {})
                    key_val = sub_key.get(q_num) or sub_key.get(str(q_num))

                    if not st_val or str(st_val).strip() == "" or str(st_val).strip() == "-":
                        n_blank += 1
                    elif key_val and str(st_val).strip().upper() == str(key_val).strip().upper():
                        n_correct += 1
                    else:
                        n_wrong += 1

                pct_c = (n_correct / max(num_scored, 1)) * 100.0
                pct_w = (n_wrong / max(num_scored, 1)) * 100.0
                pct_b = (n_blank / max(num_scored, 1)) * 100.0

                q_row_vals = [f"Câu {q_num:02d}", n_correct, f"{pct_c:.1f}%", n_wrong, f"{pct_w:.1f}%", n_blank, f"{pct_b:.1f}%"]
                for c_i, val in enumerate(q_row_vals, 1):
                    cell = ws3.cell(row=curr_row, column=c_i, value=val)
                    cell.alignment = center_al
                    cell.border = thin_border
                    if c_i == 3:  # Tỷ lệ đúng
                        cell.fill = green_fill if pct_c >= 70.0 else (red_fill if pct_c < 40.0 else stripe_fill)
                curr_row += 1

        else:
            # Mode THPT 2025: Thống kê 3 Phần
            # Phần I: 12 câu
            ws3.cell(row=curr_row, column=1, value="[PHẦN I: 12 CÂU 4 LỰA CHỌN]").font = bold_font
            curr_row += 1
            for q_num in range(1, 13):
                n_correct = 0; n_wrong = 0; n_blank = 0
                for sub in scored_submissions:
                    p1_data = sub.extracted_data.get("part1", {}) if isinstance(sub.extracted_data, dict) else {}
                    st_val = p1_data.get(q_num) or p1_data.get(str(q_num))
                    sub_key = (exam.answer_keys or {}).get(sub.exam_code, {}).get("part1", {})
                    key_val = sub_key.get(q_num) or sub_key.get(str(q_num))

                    if not st_val or str(st_val).strip() in {"", "-", "None"}:
                        n_blank += 1
                    elif key_val and str(st_val).strip().upper() == str(key_val).strip().upper():
                        n_correct += 1
                    else:
                        n_wrong += 1

                pct_c = (n_correct / max(num_scored, 1)) * 100.0
                pct_w = (n_wrong / max(num_scored, 1)) * 100.0
                pct_b = (n_blank / max(num_scored, 1)) * 100.0

                q_row_vals = [f"P1 - Câu {q_num:02d}", n_correct, f"{pct_c:.1f}%", n_wrong, f"{pct_w:.1f}%", n_blank, f"{pct_b:.1f}%"]
                for c_i, val in enumerate(q_row_vals, 1):
                    cell = ws3.cell(row=curr_row, column=c_i, value=val)
                    cell.alignment = center_al
                    cell.border = thin_border
                    if c_i == 3:
                        cell.fill = green_fill if pct_c >= 70.0 else (red_fill if pct_c < 40.0 else stripe_fill)
                curr_row += 1

            # Phần II: 4 câu x 4 ý (16 ý)
            curr_row += 1
            ws3.cell(row=curr_row, column=1, value="[PHẦN II: 4 CÂU ĐÚNG / SAI - 16 Ý]").font = bold_font
            curr_row += 1
            for q_num in range(1, 5):
                for sub_k in ['a', 'b', 'c', 'd']:
                    n_correct = 0; n_wrong = 0; n_blank = 0
                    for sub in scored_submissions:
                        p2_data = sub.extracted_data.get("part2", {}) if isinstance(sub.extracted_data, dict) else {}
                        q_data = p2_data.get(q_num) or p2_data.get(str(q_num)) or {}
                        st_val = q_data.get(sub_k)

                        sub_key = (exam.answer_keys or {}).get(sub.exam_code, {}).get("part2", {}).get(q_num, {}) or {}
                        key_val = sub_key.get(sub_k)

                        k_std = "Đ" if str(key_val).strip().upper() in {"Đ", "D", "T"} else ("S" if str(key_val).strip().upper() in {"S", "F"} else "")
                        s_std = "Đ" if str(st_val).strip().upper() in {"Đ", "D", "T"} else ("S" if str(st_val).strip().upper() in {"S", "F"} else "")

                        if not s_std:
                            n_blank += 1
                        elif s_std == k_std:
                            n_correct += 1
                        else:
                            n_wrong += 1

                    pct_c = (n_correct / max(num_scored, 1)) * 100.0
                    pct_w = (n_wrong / max(num_scored, 1)) * 100.0
                    pct_b = (n_blank / max(num_scored, 1)) * 100.0

                    q_row_vals = [f"P2 - Câu {q_num}{sub_k}", n_correct, f"{pct_c:.1f}%", n_wrong, f"{pct_w:.1f}%", n_blank, f"{pct_b:.1f}%"]
                    for c_i, val in enumerate(q_row_vals, 1):
                        cell = ws3.cell(row=curr_row, column=c_i, value=val)
                        cell.alignment = center_al
                        cell.border = thin_border
                    curr_row += 1

            # Phần III: 6 câu Trả lời ngắn
            curr_row += 1
            ws3.cell(row=curr_row, column=1, value="[PHẦN III: 6 CÂU TRẢ LỜI NGẮN]").font = bold_font
            curr_row += 1
            for q_num in range(1, 7):
                n_correct = 0; n_wrong = 0; n_blank = 0
                for sub in scored_submissions:
                    p3_data = sub.extracted_data.get("part3", {}) if isinstance(sub.extracted_data, dict) else {}
                    st_val = p3_data.get(q_num) or p3_data.get(str(q_num))
                    sub_key = (exam.answer_keys or {}).get(sub.exam_code, {}).get("part3", {})
                    key_val = sub_key.get(q_num) or sub_key.get(str(q_num))

                    s_norm = normalize_numeric_string(st_val)
                    k_norm = normalize_numeric_string(key_val)

                    if not s_norm:
                        n_blank += 1
                    elif k_norm and s_norm == k_norm:
                        n_correct += 1
                    else:
                        n_wrong += 1

                pct_c = (n_correct / max(num_scored, 1)) * 100.0
                pct_w = (n_wrong / max(num_scored, 1)) * 100.0
                pct_b = (n_blank / max(num_scored, 1)) * 100.0

                q_row_vals = [f"P3 - Câu {q_num:02d}", n_correct, f"{pct_c:.1f}%", n_wrong, f"{pct_w:.1f}%", n_blank, f"{pct_b:.1f}%"]
                for c_i, val in enumerate(q_row_vals, 1):
                    cell = ws3.cell(row=curr_row, column=c_i, value=val)
                    cell.alignment = center_al
                    cell.border = thin_border
                curr_row += 1

        ws3.column_dimensions["A"].width = 30
        ws3.column_dimensions["B"].width = 16
        ws3.column_dimensions["C"].width = 16
        ws3.column_dimensions["D"].width = 16
        ws3.column_dimensions["E"].width = 16
        ws3.column_dimensions["F"].width = 16
        ws3.column_dimensions["G"].width = 16

        wb.save(output_filepath)
        return True
    except PermissionError:
        print(f"Lỗi: Không thể ghi đè file '{output_filepath}' do file đang được mở bởi ứng dụng khác.")
        return False
    except Exception as e:
        print(f"Lỗi khi xuất báo cáo Excel: {e}")
        return False
