"""
Module: app.py
Giao diện người dùng Desktop hiện đại xây dựng bằng CustomTkinter
Hệ thống quét & chấm trắc nghiệm đa năng (Computer Vision OMR).
Hỗ trợ 2 Chế độ: Full Trắc nghiệm & Chuẩn THPT mới BGD&ĐT (3 Phần).
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Optional, Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import customtkinter as ctk
from PIL import Image, ImageTk

from core.models import Exam, Submission, ExamMode
from core.storage_manager import (
    get_all_exams, get_exam_by_id, save_exam, delete_exam, 
    get_submissions, save_submissions
)
from core.excel_answer_handler import (
    import_answer_key_from_excel, export_answer_key_to_excel,
    import_thpt_answer_key_from_excel, export_thpt_answer_key_to_excel,
    parse_quick_answer_string
)
from core.excel_exporter import export_exam_results_to_excel
from core.student_roster_handler import (
    import_student_roster_from_excel, export_sample_roster_to_excel,
    lookup_student_in_roster
)
from core.exam_processor import process_single_submission
from core.image_alignment import align_paper
from core.grading_engine import grade_full_mcq, grade_thpt_2025
from core.visualizer import draw_grading_overlay
from core.cv_utils import imread_utf8, imwrite_utf8


# Cài đặt giao diện CustomTkinter
ctk.set_appearance_mode("System")  # "Dark", "Light", "System"
ctk.set_default_color_theme("blue")


class OMRGradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HỆ THỐNG CHẤM BÀI TRẮC NGHIỆM ĐA NĂNG (COMPUTER VISION OMR)")
        self.geometry("1320, 840")
        self.minsize(1080, 700)

        self.current_exam: Optional[Exam] = None
        self.current_submissions: List[Submission] = []
        self.selected_image_files: List[str] = []
        self.new_exam_roster: Dict[str, Any] = {}

        # Khởi tạo giao diện
        self.setup_ui()
        self.load_initial_exam_data()

    def setup_ui(self):
        # Grid layout: Sidebar trái (240px), Nội dung chính bên phải
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # SIDEBAR TRÁI
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🎯 OMR GRADER", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5))

        self.sub_logo = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Hệ thống chấm thi OpenCV", 
            font=ctk.CTkFont(size=12)
        )
        self.sub_logo.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Các nút điều hướng
        self.btn_nav_exams = ctk.CTkButton(
            self.sidebar_frame, text="📋 Danh sách bài thi", 
            command=self.show_exam_list_view, height=38
        )
        self.btn_nav_exams.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.btn_nav_new = ctk.CTkButton(
            self.sidebar_frame, text="➕ Tạo bài thi mới", 
            command=self.show_new_exam_view, height=38
        )
        self.btn_nav_new.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        self.btn_nav_grade = ctk.CTkButton(
            self.sidebar_frame, text="📸 Quét & Chấm bài", 
            command=self.show_grading_view, height=38
        )
        self.btn_nav_grade.grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        self.btn_nav_stats = ctk.CTkButton(
            self.sidebar_frame, text="📊 Thống kê & Xuất Excel", 
            command=self.show_stats_view, height=38
        )
        self.btn_nav_stats.grid(row=5, column=0, padx=15, pady=8, sticky="ew")

        # Theme selector ở cuối sidebar
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Giao diện:")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0), sticky="w")
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.sidebar_frame, values=["Dark", "Light", "System"],
            command=ctk.set_appearance_mode
        )
        self.appearance_mode_menu.grid(row=9, column=0, padx=20, pady=(5, 20), sticky="ew")

        # -------------------------------------------------------------
        # VÙNG HIỂN THỊ NỘI DUNG CHÍNH (CONTENT AREA)
        # -------------------------------------------------------------
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def get_exam_display_options(self) -> List[str]:
        """Tạo danh sách nhãn hiển thị cho dropdown chọn kỳ thi"""
        exams = get_all_exams()
        if not exams:
            return ["(Chưa có bài thi nào)"]
        return [f"{e.title} - Môn {e.subject} ({e.class_name}) [ID:{e.exam_id}]" for e in exams]

    def get_exam_from_display_label(self, label: str) -> Optional[Exam]:
        """Tìm đối tượng Exam từ nhãn dropdown"""
        exams = get_all_exams()
        for e in exams:
            if f"[ID:{e.exam_id}]" in label:
                return e
        return exams[0] if exams else None

    def get_current_exam_display_label(self) -> str:
        if not self.current_exam:
            return "(Chưa có bài thi nào)"
        return f"{self.current_exam.title} - Môn {self.current_exam.subject} ({self.current_exam.class_name}) [ID:{self.current_exam.exam_id}]"

    def load_initial_exam_data(self):
        exams = get_all_exams()
        if exams:
            self.current_exam = exams[0]
            self.current_submissions = get_submissions(self.current_exam.exam_id)
        self.show_exam_list_view()

    # =================================================================
    # VIEW 1: DANH SÁCH BÀI KIỂM TRA
    # =================================================================
    def show_exam_list_view(self):
        self.clear_content()

        container = ctk.CTkScrollableFrame(self.content_frame)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            header_frame, text="Danh Sách Bài Kiểm Tra", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(side="left")

        btn_add = ctk.CTkButton(
            header_frame, text="+ Thêm bài mới", 
            command=self.show_new_exam_view
        )
        btn_add.pack(side="right")

        exams = get_all_exams()
        if not exams:
            empty_lbl = ctk.CTkLabel(
                container, 
                text="Chưa có bài kiểm tra nào trong hệ thống.\nVui lòng bấm '+ Thêm bài mới' để thiết lập bài thi!",
                font=ctk.CTkFont(size=14, slant="italic")
            )
            empty_lbl.pack(pady=50)
            return

        for exam in exams:
            card = ctk.CTkFrame(container, corner_radius=8)
            card.pack(fill="x", pady=8, padx=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=12, fill="both", expand=True)

            mode_tag = "🎯 Full Trắc Nghiệm (40 câu)" if exam.mode == ExamMode.FULL_MCQ else "🏛️ Chuẩn THPT mới BGD&ĐT (3 Phần)"
            subs_count = len(get_submissions(exam.exam_id))

            is_active = (self.current_exam and self.current_exam.exam_id == exam.exam_id)
            title_prefix = "⭐ [ĐANG CHỌN] " if is_active else ""

            card_title = ctk.CTkLabel(
                info_frame, 
                text=f"{title_prefix}{exam.title} - Môn {exam.subject} ({exam.class_name})", 
                font=ctk.CTkFont(size=16, weight="bold")
            )
            card_title.pack(anchor="w")

            num_codes = len(exam.answer_keys)
            card_sub = ctk.CTkLabel(
                info_frame, 
                text=f"Loại đề: {mode_tag} | Ngày tạo: {exam.created_at} | Thang điểm: {exam.max_score} | Đã chấm: {subs_count} bài | Số mã đề: {num_codes}",
                font=ctk.CTkFont(size=12)
            )
            card_sub.pack(anchor="w", pady=(3, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15, pady=12)

            btn_select = ctk.CTkButton(
                btn_frame, text="📸 Chấm bài này", width=110,
                command=lambda e=exam: self.select_and_open_exam(e)
            )
            btn_select.pack(side="left", padx=5)

            btn_del = ctk.CTkButton(
                btn_frame, text="Xóa", width=60, fg_color="#C0392B", hover_color="#962D22",
                command=lambda eid=exam.exam_id: self.delete_exam_action(eid)
            )
            btn_del.pack(side="left", padx=5)

    def select_and_open_exam(self, exam: Exam):
        self.current_exam = exam
        self.current_submissions = get_submissions(exam.exam_id)
        self.selected_image_files = []
        self.show_grading_view()

    def delete_exam_action(self, exam_id: str):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa bài kiểm tra này cùng toàn bộ kết quả chấm?"):
            delete_exam(exam_id)
            exams = get_all_exams()
            if self.current_exam and self.current_exam.exam_id == exam_id:
                self.current_exam = exams[0] if exams else None
                self.current_submissions = get_submissions(self.current_exam.exam_id) if self.current_exam else []
            self.show_exam_list_view()

    # =================================================================
    # VIEW 2: TẠO & CÀI ĐẶT BÀI KIỂM TRA MỚI (BỎ CÁC DEMO CỨNG)
    # =================================================================
    def show_new_exam_view(self):
        self.clear_content()

        container = ctk.CTkScrollableFrame(self.content_frame)
        container.pack(fill="both", expand=True, padx=25, pady=20)

        title = ctk.CTkLabel(
            container, text="Thiết Lập Bài Kiểm Tra Mới", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 15))

        # 1. Thông tin chung
        form_frame = ctk.CTkFrame(container)
        form_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(form_frame, text="Tên bài kiểm tra:").grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.ent_title = ctk.CTkEntry(form_frame, placeholder_text="Ví dụ: Kiểm tra 1 tiết Toán Học Kỳ 1", width=340)
        self.ent_title.grid(row=0, column=1, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(form_frame, text="Môn học:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.ent_subject = ctk.CTkEntry(form_frame, placeholder_text="Toán", width=160)
        self.ent_subject.grid(row=1, column=1, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(form_frame, text="Lớp:").grid(row=1, column=2, padx=15, pady=10, sticky="w")
        self.ent_class = ctk.CTkEntry(form_frame, placeholder_text="12A1", width=140)
        self.ent_class.grid(row=1, column=3, padx=15, pady=10, sticky="w")

        # 2. Chọn chế độ thi
        mode_frame = ctk.CTkFrame(container)
        mode_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(mode_frame, text="Chọn Chế độ thi:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=8)

        self.mode_var = ctk.StringVar(value=ExamMode.FULL_MCQ)
        
        mode_full_row = ctk.CTkFrame(mode_frame, fg_color="transparent")
        mode_full_row.pack(fill="x", padx=25, pady=5)

        self.rb_full = ctk.CTkRadioButton(
            mode_full_row, text="Chế độ 1: Trắc nghiệm 4 lựa chọn (Phiếu chuẩn A-B-C-D)", 
            variable=self.mode_var, value=ExamMode.FULL_MCQ, command=self.update_answer_key_input_ui
        )
        self.rb_full.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(mode_full_row, text="Số câu hỏi:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        self.cbo_num_q = ctk.CTkComboBox(mode_full_row, values=["40", "20"], width=80)
        self.cbo_num_q.set("40")
        self.cbo_num_q.pack(side="left", padx=5)

        self.rb_thpt = ctk.CTkRadioButton(
            mode_frame, text="Chế độ 2: Đề chuẩn Tốt nghiệp THPT mới (Bộ GD&ĐT - 3 Phần)", 
            variable=self.mode_var, value=ExamMode.THPT_2025, command=self.update_answer_key_input_ui
        )
        self.rb_thpt.pack(anchor="w", padx=25, pady=5)

        # 3. Khu vực nhập đáp án
        self.ans_container = ctk.CTkFrame(container)
        self.ans_container.pack(fill="x", pady=10, padx=5)

        self.active_answer_keys = {}
        self.update_answer_key_input_ui()

        # 4. Danh sách học sinh (Tùy chọn - Import Excel để tự map SBD sang Họ tên)
        roster_frame = ctk.CTkFrame(container)
        roster_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            roster_frame, 
            text="4. Danh sách học sinh (Tùy chọn - Tự động map SBD sang Họ tên từ Excel):", 
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=15, pady=(8, 4))

        roster_toolbar = ctk.CTkFrame(roster_frame, fg_color="transparent")
        roster_toolbar.pack(fill="x", padx=15, pady=4)

        btn_import_roster = ctk.CTkButton(
            roster_toolbar, text="📥 Nạp Danh sách học sinh (.xlsx)", width=230,
            command=self.import_roster_for_new_exam_action
        )
        btn_import_roster.pack(side="left", padx=5)

        btn_sample_roster = ctk.CTkButton(
            roster_toolbar, text="📄 Xuất file Excel mẫu DS", width=180, fg_color="#5D6D7E",
            command=self.export_sample_roster_action
        )
        btn_sample_roster.pack(side="left", padx=5)

        btn_clear_roster = ctk.CTkButton(
            roster_toolbar, text="🗑️ Hủy nạp", width=90, fg_color="#C0392B", hover_color="#962D22",
            command=self.clear_roster_for_new_exam_action
        )
        btn_clear_roster.pack(side="left", padx=5)

        self.lbl_roster_status = ctk.CTkLabel(
            roster_frame, 
            text="Chưa nạp file Excel (Khi quét, phần mềm sẽ nhận diện tên tự động bằng OCR hoặc SBD mặc định).",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#7F8C8D"
        )
        self.lbl_roster_status.pack(anchor="w", padx=20, pady=(4, 10))

        # Nút Lưu
        btn_save = ctk.CTkButton(
            container, text="💾 LƯU BÀI KIỂM TRA & BẮT ĐẦU CHẤM", height=45, 
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.save_new_exam_action
        )
        btn_save.pack(fill="x", pady=25, padx=5)

    def update_answer_key_input_ui(self):
        for widget in self.ans_container.winfo_children():
            widget.destroy()

        mode = self.mode_var.get()
        header_text = "Nhập đáp án: Full trắc nghiệm (Mã đề 101)" if mode == ExamMode.FULL_MCQ else "Nhập đáp án: Chuẩn THPT mới 3 Phần (Mã đề 101)"
        ctk.CTkLabel(self.ans_container, text=header_text, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=8)

        # Thanh công cụ Import/Export
        tool_bar = ctk.CTkFrame(self.ans_container, fg_color="transparent")
        tool_bar.pack(fill="x", padx=15, pady=5)

        btn_import_excel = ctk.CTkButton(
            tool_bar, text="📥 Import từ Excel", width=140, 
            command=self.import_answers_from_excel_action
        )
        btn_import_excel.pack(side="left", padx=5)

        btn_export_excel = ctk.CTkButton(
            tool_bar, text="📤 Xuất file mẫu Excel", width=150,
            command=self.export_sample_answers_action
        )
        btn_export_excel.pack(side="left", padx=5)

        btn_sample_fill = ctk.CTkButton(
            tool_bar, text="🎲 Nạp gợi ý mẫu (Test)", width=150, fg_color="#5D6D7E",
            command=self.fill_sample_answer_keys
        )
        btn_sample_fill.pack(side="left", padx=5)

        if mode == ExamMode.FULL_MCQ:
            ctk.CTkLabel(self.ans_container, text="Gõ nhanh chuỗi 40 đáp án (cách nhau bởi khoảng trắng hoặc viết liền):").pack(anchor="w", padx=15, pady=(10, 2))
            self.txt_quick_ans = ctk.CTkEntry(
                self.ans_container, 
                placeholder_text="Ví dụ: A B C D A B C D A B C D ... (hoặc ABCD...)",
                width=650
            )
            self.txt_quick_ans.pack(fill="x", padx=15, pady=5)
        else:
            # Giao diện nhập trực tiếp 3 phần cho đề chuẩn THPT
            thpt_box = ctk.CTkFrame(self.ans_container, fg_color="transparent")
            thpt_box.pack(fill="x", padx=15, pady=8)

            # Phần I
            ctk.CTkLabel(thpt_box, text="[Phần I: 12 câu 4 lựa chọn A-B-C-D]", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
            self.txt_thpt_p1 = ctk.CTkEntry(thpt_box, placeholder_text="Ví dụ: A C B D A B D C A B C D", width=650)
            self.txt_thpt_p1.pack(fill="x", pady=2)

            # Phần II
            ctk.CTkLabel(thpt_box, text="[Phần II: 4 câu Đúng/Sai (16 ý theo thứ tự câu 1-4, mỗi câu a-b-c-d)]", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
            self.txt_thpt_p2 = ctk.CTkEntry(thpt_box, placeholder_text="Ví dụ: D S D D S D S D D D S S S S D D (hoặc Đ S Đ Đ...)", width=650)
            self.txt_thpt_p2.pack(fill="x", pady=2)

            # Phần III
            ctk.CTkLabel(thpt_box, text="[Phần III: 6 câu Trả lời ngắn - Nhập 6 kết quả số cách nhau bởi dấu phẩy]", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
            self.txt_thpt_p3 = ctk.CTkEntry(thpt_box, placeholder_text="Ví dụ: 15, -2.5, 0.75, 120, -8, 3.14", width=650)
            self.txt_thpt_p3.pack(fill="x", pady=2)

    def fill_sample_answer_keys(self):
        """Tiện ích nạp mẫu nhanh khi người dùng bấm nút gợi ý"""
        mode = self.mode_var.get()
        if mode == ExamMode.FULL_MCQ:
            sample_str = "A D C B A D C B A D C B A D C B A D C B A D C B A D C B A D C B A D C B A D C B"
            self.txt_quick_ans.delete(0, "end")
            self.txt_quick_ans.insert(0, sample_str)
        else:
            self.txt_thpt_p1.delete(0, "end")
            self.txt_thpt_p1.insert(0, "A C B D A B D C A B C D")

            self.txt_thpt_p2.delete(0, "end")
            self.txt_thpt_p2.insert(0, "Đ S Đ Đ S Đ S Đ Đ Đ S S S S Đ Đ")

            self.txt_thpt_p3.delete(0, "end")
            self.txt_thpt_p3.insert(0, "15, -2.5, 0.75, 120, -8, 3.14")

    def import_answers_from_excel_action(self):
        filepath = filedialog.askopenfilename(
            title="Chọn file Excel đáp án",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not filepath:
            return
        mode = self.mode_var.get()
        try:
            if mode == ExamMode.FULL_MCQ:
                ans = import_answer_key_from_excel(filepath)
                if ans:
                    self.active_answer_keys["101"] = ans
                    quick_str = " ".join([ans[k] for k in sorted(ans.keys(), key=lambda x: int(x))])
                    self.txt_quick_ans.delete(0, "end")
                    self.txt_quick_ans.insert(0, quick_str)
                    messagebox.showinfo("Thành công", f"Đã nạp {len(ans)} câu đáp án từ Excel!")
                else:
                    messagebox.showwarning("Cảnh báo", "Không đọc được câu hỏi nào từ file Excel.")
            else:
                ans_thpt = import_thpt_answer_key_from_excel(filepath)
                p1_len = len(ans_thpt.get("part1", {}))
                p2_len = len(ans_thpt.get("part2", {}))
                p3_len = len(ans_thpt.get("part3", {}))
                if p1_len or p2_len or p3_len:
                    self.active_answer_keys["101"] = ans_thpt
                    # Cập nhật hiển thị lên UI
                    p1_str = " ".join([ans_thpt["part1"][k] for k in sorted(ans_thpt["part1"].keys(), key=lambda x: int(x))])
                    self.txt_thpt_p1.delete(0, "end")
                    self.txt_thpt_p1.insert(0, p1_str)

                    p2_tokens = []
                    for q in sorted(ans_thpt["part2"].keys(), key=lambda x: int(x)):
                        for s in ['a', 'b', 'c', 'd']:
                            p2_tokens.append(ans_thpt["part2"][q].get(s, ""))
                    self.txt_thpt_p2.delete(0, "end")
                    self.txt_thpt_p2.insert(0, " ".join(p2_tokens))

                    p3_str = ", ".join([str(ans_thpt["part3"][k]) for k in sorted(ans_thpt["part3"].keys(), key=lambda x: int(x))])
                    self.txt_thpt_p3.delete(0, "end")
                    self.txt_thpt_p3.insert(0, p3_str)

                    messagebox.showinfo("Thành công", f"Đã nạp đáp án THPT: P1({p1_len} câu), P2({p2_len} câu), P3({p3_len} câu)!")
                else:
                    messagebox.showwarning("Cảnh báo", "Không đọc được đáp án THPT từ file.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")

    def export_sample_answers_action(self):
        out_path = filedialog.asksaveasfilename(
            title="Lưu file mẫu Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not out_path:
            return
        mode = self.mode_var.get()
        if mode == ExamMode.FULL_MCQ:
            sample_answers = {i: ['A', 'B', 'C', 'D'][i % 4] for i in range(1, 41)}
            export_answer_key_to_excel(sample_answers, out_path, "ĐÁP ÁN MẪU FULL TRẮC NGHIỆM")
        else:
            p1 = {i: ['A', 'C', 'B', 'D'][i % 4] for i in range(1, 13)}
            p2 = {1: {'a':'Đ', 'b':'S', 'c':'Đ', 'd':'Đ'}, 2: {'a':'S', 'b':'Đ', 'c':'S', 'd':'Đ'}, 3: {'a':'Đ', 'b':'Đ', 'c':'S', 'd':'S'}, 4: {'a':'S', 'b':'S', 'c':'Đ', 'd':'Đ'}}
            p3 = {1: '15', 2: '-2.5', 3: '0.75', 4: '120', 5: '-8', 6: '3.14'}
            export_thpt_answer_key_to_excel("101", p1, p2, p3, out_path)
        messagebox.showinfo("Thành công", f"Đã xuất file mẫu tại:\n{out_path}")

    def import_roster_for_new_exam_action(self):
        filepath = filedialog.askopenfilename(
            title="Chọn file Excel Danh sách học sinh",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not filepath:
            return
        try:
            roster = import_student_roster_from_excel(filepath)
            if not roster:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy dữ liệu học sinh hợp lệ trong file Excel!")
                return
            self.new_exam_roster = roster
            fname = os.path.basename(filepath)
            if hasattr(self, 'lbl_roster_status'):
                self.lbl_roster_status.configure(
                    text=f"✅ Đã nạp {len(roster)} học sinh từ file '{fname}'! (Sẽ tự động khớp Họ tên khi quét).",
                    text_color="#27AE60"
                )
            messagebox.showinfo("Thành công", f"Đã nạp danh sách {len(roster)} học sinh từ Excel!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc danh sách học sinh: {e}")

    def export_sample_roster_action(self):
        out_path = filedialog.asksaveasfilename(
            title="Lưu file Excel mẫu danh sách học sinh",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not out_path:
            return
        success = export_sample_roster_to_excel(out_path)
        if success:
            messagebox.showinfo("Thành công", f"Đã xuất file mẫu danh sách học sinh tại:\n{out_path}")
        else:
            messagebox.showerror("Lỗi", "Không thể xuất file mẫu Excel.")

    def clear_roster_for_new_exam_action(self):
        self.new_exam_roster = {}
        if hasattr(self, 'lbl_roster_status'):
            self.lbl_roster_status.configure(
                text="Chưa nạp file Excel (Khi quét, phần mềm sẽ nhận diện tên tự động bằng OCR hoặc SBD mặc định).",
                text_color="#7F8C8D"
            )

    def save_new_exam_action(self):
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Tên bài kiểm tra!")
            return

        subject = self.ent_subject.get().strip() or "Toán"
        class_name = self.ent_class.get().strip() or "12A1"
        mode = self.mode_var.get()
        import uuid
        exam_id = f"exam_{uuid.uuid4().hex[:8]}"

        answer_keys = {}
        if mode == ExamMode.FULL_MCQ:
            raw_text = self.txt_quick_ans.get().strip()
            if not raw_text and "101" not in self.active_answer_keys:
                messagebox.showwarning("Thiếu đáp án", "Vui lòng nhập chuỗi đáp án hoặc Import từ Excel!")
                return
            if raw_text:
                parsed = parse_quick_answer_string(raw_text)
                if not parsed:
                    messagebox.showwarning("Sai định dạng", "Chuỗi đáp án không hợp lệ!")
                    return
                answer_keys["101"] = parsed
            else:
                answer_keys["101"] = self.active_answer_keys["101"]
        else:
            # Thu thập 3 phần THPT
            p1_raw = self.txt_thpt_p1.get().strip()
            p2_raw = self.txt_thpt_p2.get().strip()
            p3_raw = self.txt_thpt_p3.get().strip()

            if not (p1_raw or p2_raw or p3_raw) and "101" not in self.active_answer_keys:
                messagebox.showwarning("Thiếu đáp án", "Vui lòng nhập đáp án cho các phần hoặc Import từ Excel!")
                return

            if "101" in self.active_answer_keys:
                answer_keys["101"] = self.active_answer_keys["101"]
            else:
                # Xử lý chuỗi nhập
                p1_parsed = parse_quick_answer_string(p1_raw) if p1_raw else {}
                # Xử lý P2: 16 ký tự Đ/S
                p2_tokens = [t.strip().upper() for t in p2_raw.replace(',', ' ').split() if t.strip()]
                # Chuẩn hóa Đ/S/D
                clean_p2 = []
                for tok in p2_tokens:
                    for ch in tok:
                        if ch in {"Đ", "D", "T", "1"}: clean_p2.append("Đ")
                        elif ch in {"S", "F", "0"}: clean_p2.append("S")
                p2_dict = {}
                token_idx = 0
                for q_num in range(1, 5):
                    p2_dict[q_num] = {}
                    for sub in ['a', 'b', 'c', 'd']:
                        val = clean_p2[token_idx] if token_idx < len(clean_p2) else "Đ"
                        p2_dict[q_num][sub] = val
                        token_idx += 1

                # Xử lý P3: các số phân cách bởi phẩy hoặc khoảng trắng
                p3_tokens = [t.strip() for t in p3_raw.replace(';', ',').split(',') if t.strip()]
                p3_dict = {idx: tok for idx, tok in enumerate(p3_tokens, start=1)}

                answer_keys["101"] = {
                    "part1": p1_parsed,
                    "part2": p2_dict,
                    "part3": p3_dict
                }

        try:
            num_q = int(self.cbo_num_q.get()) if mode == ExamMode.FULL_MCQ else 40
        except Exception:
            num_q = 40

        exam = Exam(
            exam_id=exam_id,
            title=title,
            subject=subject,
            class_name=class_name,
            mode=mode,
            num_questions=num_q,
            answer_keys=answer_keys,
            student_roster=getattr(self, "new_exam_roster", {})
        )
        self.new_exam_roster = {}

        save_exam(exam)
        self.current_exam = exam
        self.current_submissions = []
        self.selected_image_files = []
        messagebox.showinfo("Thành công", f"Đã tạo bài kiểm tra: {title}")
        self.show_grading_view()

    # =================================================================
    # VIEW 3: QUÉT & CHẤM BÀI HÀNG LOẠT (HỖ TRỢ CHỌN KỲ THI TRỰC TIẾP)
    # =================================================================
    def show_grading_view(self):
        self.clear_content()

        exams = get_all_exams()
        if not exams:
            messagebox.showinfo("Thông báo", "Chưa có bài kiểm tra nào. Vui lòng tạo bài mới!")
            self.show_new_exam_view()
            return

        if not self.current_exam:
            self.current_exam = exams[0]
            self.current_submissions = get_submissions(self.current_exam.exam_id)

        container = ctk.CTkFrame(self.content_frame)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # -------------------------------------------------------------
        # THANH CHỌN KỲ THI TRỰC TIẾP (EXAM SELECTOR BAR)
        # -------------------------------------------------------------
        exam_bar = ctk.CTkFrame(container, fg_color="#1F4E78", corner_radius=8)
        exam_bar.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            exam_bar, text="🎯 Chọn kỳ thi:", 
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF"
        ).pack(side="left", padx=(15, 8), pady=10)

        exam_options = self.get_exam_display_options()
        current_opt = self.get_current_exam_display_label()
        if current_opt not in exam_options:
            current_opt = exam_options[0]

        self.cbo_grading_exam = ctk.CTkOptionMenu(
            exam_bar, values=exam_options, width=420,
            command=self.on_grading_exam_changed
        )
        self.cbo_grading_exam.set(current_opt)
        self.cbo_grading_exam.pack(side="left", padx=5, pady=10)

        btn_new_from_grading = ctk.CTkButton(
            exam_bar, text="➕ Tạo bài mới", width=110, fg_color="#2980B9", hover_color="#1F618D",
            command=self.show_new_exam_view
        )
        btn_new_from_grading.pack(side="right", padx=15, pady=10)

        # -------------------------------------------------------------
        # THẺ THÔNG TIN CHI TIẾT BÀI THI ĐANG CHỌN
        # -------------------------------------------------------------
        mode_desc = "Full Trắc Nghiệm (40 câu)" if self.current_exam.mode == ExamMode.FULL_MCQ else "Chuẩn THPT mới BGD&ĐT (3 Phần)"
        keys_list = ", ".join(self.current_exam.answer_keys.keys()) or "Chưa có"

        info_card = ctk.CTkFrame(container, fg_color=("gray90", "gray20"), corner_radius=6)
        info_card.pack(fill="x", pady=(0, 10))

        lbl_desc = ctk.CTkLabel(
            info_card,
            text=f"📌 Môn: {self.current_exam.subject} | Lớp: {self.current_exam.class_name} | Thang điểm: {self.current_exam.max_score} | Loại đề: {mode_desc} | Các mã đề đã có: [{keys_list}]",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        lbl_desc.pack(padx=12, pady=(6, 2), anchor="w")

        # Khung Danh sách học sinh trong Thẻ bài thi
        roster_dict = getattr(self.current_exam, "student_roster", {})
        roster_count = len(roster_dict)
        roster_info_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        roster_info_frame.pack(fill="x", padx=12, pady=(2, 6))

        if roster_count > 0:
            roster_label_text = f"👥 Danh sách học sinh: Đã nạp {roster_count} em (Tự động map SBD ➔ Họ tên từ Excel)"
            roster_label_color = "#27AE60"
        else:
            roster_label_text = "👥 Danh sách học sinh: Chưa nạp Excel (Hệ thống sẽ dùng OCR quét Họ tên trực tiếp từ bài thi)"
            roster_label_color = "#E67E22"

        self.lbl_grading_roster = ctk.CTkLabel(
            roster_info_frame,
            text=roster_label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=roster_label_color
        )
        self.lbl_grading_roster.pack(side="left")

        btn_import_roster_now = ctk.CTkButton(
            roster_info_frame, text="📥 Nạp/Đổi DS Excel", width=140, height=26,
            command=self.import_roster_for_current_exam_action
        )
        btn_import_roster_now.pack(side="left", padx=10)

        btn_dl_sample_roster = ctk.CTkButton(
            roster_info_frame, text="📄 Tải mẫu Excel", width=120, height=26, fg_color="#5D6D7E",
            command=self.export_sample_roster_action
        )
        btn_dl_sample_roster.pack(side="left", padx=5)

        if roster_count > 0:
            btn_view_roster = ctk.CTkButton(
                roster_info_frame, text=f"👁️ Xem DS ({roster_count})", width=110, height=26, fg_color="#2980B9",
                command=self.show_current_roster_modal
            )
            btn_view_roster.pack(side="left", padx=5)

        # -------------------------------------------------------------
        # THANH THAO TÁC CHỌN ẢNH VÀ CHẤM
        # -------------------------------------------------------------
        action_bar = ctk.CTkFrame(container, fg_color="transparent")
        action_bar.pack(fill="x", pady=5)

        btn_pick_files = ctk.CTkButton(
            action_bar, text="🖼️ Chọn ảnh bài làm", width=140,
            command=self.pick_submission_images
        )
        btn_pick_files.pack(side="left", padx=5)

        btn_pick_folder = ctk.CTkButton(
            action_bar, text="📁 Chọn thư mục ảnh", width=140,
            command=self.pick_submission_folder
        )
        btn_pick_folder.pack(side="left", padx=5)

        btn_clear_picks = ctk.CTkButton(
            action_bar, text="🗑️ Hủy chọn", width=90, fg_color="#7F8C8D", hover_color="#626567",
            command=self.clear_selected_images
        )
        btn_clear_picks.pack(side="left", padx=5)

        # Nút nạp mẫu test (rõ ràng, không tự ép buộc)
        btn_sample = ctk.CTkButton(
            action_bar, text="🧪 Nạp ảnh mẫu test", width=140, fg_color="#5D6D7E", hover_color="#34495E",
            command=self.load_sample_test_images
        )
        btn_sample.pack(side="left", padx=10)

        self.btn_start_grading = ctk.CTkButton(
            action_bar, text="🚀 BẮT ĐẦU CHẤM TẤT CẢ", width=190,
            fg_color="#27AE60", hover_color="#1E8449",
            font=ctk.CTkFont(weight="bold"),
            command=self.start_batch_grading_thread
        )
        self.btn_start_grading.pack(side="right", padx=5)

        # Trạng thái ảnh đã chọn & Thanh tiến trình
        self.progress_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(8, 4))

        count_txt = f"Đã chọn {len(self.selected_image_files)} file ảnh." if self.selected_image_files else "Chưa chọn ảnh nào. Vui lòng bấm 'Chọn ảnh bài làm' hoặc 'Chọn thư mục ảnh' để quét."
        self.lbl_selected_status = ctk.CTkLabel(self.progress_frame, text=count_txt, font=ctk.CTkFont(size=12, slant="italic"))
        self.lbl_selected_status.pack(anchor="w", padx=5)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=5, pady=4)
        self.progress_bar.set(0)

        self.lbl_progress = ctk.CTkLabel(self.progress_frame, text="Sẵn sàng quét và chấm bài.")
        self.lbl_progress.pack(anchor="w", padx=5)

        # -------------------------------------------------------------
        # BẢNG KẾT QUẢ ĐÃ CHẤM CHO KỲ THI ĐANG CHỌN
        # -------------------------------------------------------------
        tbl_header_bar = ctk.CTkFrame(container, fg_color="transparent")
        tbl_header_bar.pack(fill="x", pady=(12, 4))

        tbl_title = ctk.CTkLabel(
            tbl_header_bar, 
            text=f"Kết quả bài làm đã chấm ({len(self.current_submissions)} bài):", 
            font=ctk.CTkFont(weight="bold", size=14)
        )
        tbl_title.pack(side="left")

        btn_clear_results = ctk.CTkButton(
            tbl_header_bar, text="🗑️ Xóa toàn bộ kết quả", width=140, fg_color="#C0392B", hover_color="#962D22",
            command=self.clear_all_submissions_for_exam
        )
        btn_clear_results.pack(side="right", padx=5)

        btn_refresh_tbl = ctk.CTkButton(
            tbl_header_bar, text="🔄 Tải lại", width=80,
            command=self.render_submission_table
        )
        btn_refresh_tbl.pack(side="right", padx=5)

        self.table_scroll = ctk.CTkScrollableFrame(container)
        self.table_scroll.pack(fill="both", expand=True, pady=5)

        self.render_submission_table()

    def import_roster_for_current_exam_action(self):
        if not self.current_exam:
            return
        filepath = filedialog.askopenfilename(
            title="Chọn file Excel Danh sách học sinh",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not filepath:
            return
        try:
            roster = import_student_roster_from_excel(filepath)
            if not roster:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy dữ liệu học sinh hợp lệ trong file Excel!")
                return
            self.current_exam.student_roster = roster
            save_exam(self.current_exam)

            # Tự động cập nhật lại tên cho các bài thi đã chấm nếu khớp SBD!
            updated_count = 0
            if self.current_submissions:
                for sub in self.current_submissions:
                    r_name, r_cls = lookup_student_in_roster(sub.student_id, roster)
                    if r_name and sub.student_name != r_name:
                        sub.student_name = r_name
                        updated_count += 1
                if updated_count > 0:
                    save_submissions(self.current_exam.exam_id, self.current_submissions)

            msg = f"Đã nạp thành công danh sách {len(roster)} học sinh cho kỳ thi!"
            if updated_count > 0:
                msg += f"\nĐã tự động cập nhật lại Họ tên cho {updated_count} bài làm hiện có."
            messagebox.showinfo("Thành công", msg)
            self.show_grading_view()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nạp danh sách học sinh: {e}")

    def show_current_roster_modal(self):
        if not self.current_exam or not getattr(self.current_exam, "student_roster", {}):
            messagebox.showinfo("Thông báo", "Kỳ thi chưa có danh sách học sinh.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title(f"Danh sách học sinh - {self.current_exam.title}")
        modal.geometry("540, 520")
        modal.attributes("-topmost", True)
        modal.focus_force()

        ctk.CTkLabel(
            modal, 
            text=f"DANH SÁCH HỌC SINH ({len(self.current_exam.student_roster)} em)", 
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=10)

        scroll = ctk.CTkScrollableFrame(modal)
        scroll.pack(fill="both", expand=True, padx=15, pady=10)

        # Header
        hdr = ctk.CTkFrame(scroll, fg_color="#1F4E78")
        hdr.pack(fill="x", pady=2)
        ctk.CTkLabel(hdr, text="STT", width=40, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="SBD", width=90, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="Họ và tên", width=220, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="Lớp", width=80, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)

        for idx, (sbd, info) in enumerate(sorted(self.current_exam.student_roster.items()), start=1):
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=str(idx), width=40).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=sbd, width=90, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=info.get("name", ""), width=220, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=info.get("class", ""), width=80).pack(side="left", padx=5)

    def on_grading_exam_changed(self, selected_label: str):
        """Xử lý sự kiện khi giáo viên chuyển kỳ thi trên dropdown Quét & Chấm"""
        exam = self.get_exam_from_display_label(selected_label)
        if exam:
            self.current_exam = exam
            self.current_submissions = get_submissions(exam.exam_id)
            self.selected_image_files = []
            self.show_grading_view()

    def clear_selected_images(self):
        self.selected_image_files = []
        self.lbl_selected_status.configure(text="Đã xóa danh sách ảnh đã chọn.")
        self.progress_bar.set(0)

    def load_sample_test_images(self):
        """Tiện ích rõ ràng cho phép giáo viên nạp các bài mẫu nếu muốn thử nghiệm"""
        sample_dir = os.path.join(PROJECT_ROOT, "dataset/sample_submissions")
        if os.path.exists(sample_dir):
            valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}
            # Chỉ lấy các ảnh bài làm thí sinh thật
            found = [
                os.path.join(sample_dir, f) for f in os.listdir(sample_dir) 
                if os.path.splitext(f)[1].lower() in valid_exts and not f.startswith("aligned_")
            ]
            if found:
                self.selected_image_files = found
                self.lbl_selected_status.configure(text=f"Đã nạp {len(found)} ảnh mẫu từ thư mục dataset/sample_submissions.")
                messagebox.showinfo("Đã nạp ảnh mẫu", f"Đã nạp {len(found)} ảnh thử nghiệm. Bấm 'BẮT ĐẦU CHẤM' để kiểm tra!")
                return
        messagebox.showwarning("Thông báo", "Không tìm thấy thư mục ảnh mẫu.")

    def render_submission_table(self):
        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        if not self.current_submissions:
            ctk.CTkLabel(
                self.table_scroll, 
                text="Chưa có bài làm nào được chấm cho kỳ thi này.\nHãy chọn ảnh và bấm 'BẮT ĐẦU CHẤM TẤT CẢ'!",
                font=ctk.CTkFont(slant="italic")
            ).pack(pady=40)
            return

        # Header bảng
        hdr = ctk.CTkFrame(self.table_scroll, fg_color="#2F5597")
        hdr.pack(fill="x", pady=2)

        ctk.CTkLabel(hdr, text="STT", width=40, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="SBD", width=90, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="Họ tên", width=180, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="Mã đề", width=60, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="Điểm số", width=90, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="Trạng thái", width=120, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(hdr, text="Thao tác", width=160, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=5)

        for idx, sub in enumerate(self.current_submissions, start=1):
            row = ctk.CTkFrame(self.table_scroll)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=str(idx), width=40).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=sub.student_id or "---", width=90).pack(side="left", padx=5)
            
            # Hiển thị Họ tên kèm nguồn gốc (Excel / OCR)
            src_tag = ""
            r_name, _ = lookup_student_in_roster(sub.student_id, getattr(self.current_exam, "student_roster", {}))
            if r_name and sub.student_name == r_name:
                src_tag = " [Excel]"
            elif (sub.ocr_data or {}).get("name") and sub.student_name == sub.ocr_data.get("name"):
                src_tag = " [OCR]"

            disp_name = (sub.student_name or f"Thí sinh SBD {sub.student_id}") + src_tag
            ctk.CTkLabel(row, text=disp_name, width=180, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=sub.exam_code or "???", width=60).pack(side="left", padx=5)
            
            if sub.status == "Lỗi":
                score_str = "-"
                score_color = "#C0392B"
            else:
                score_str = f"{sub.total_score:.2f}"
                score_color = "#27AE60" if sub.total_score >= 5.0 else "#C0392B"
            ctk.CTkLabel(row, text=score_str, width=90, font=ctk.CTkFont(weight="bold"), text_color=score_color).pack(side="left", padx=5)

            # Màu trạng thái
            st_color = "#27AE60" if sub.status == "Đã chấm" else ("#D4AC0D" if sub.status == "Cần kiểm tra" else "#C0392B")
            ctk.CTkLabel(row, text=sub.status, width=120, text_color=st_color, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

            # Khung nút thao tác
            action_sub_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_sub_frame.pack(side="left", padx=5)

            btn_view = ctk.CTkButton(
                action_sub_frame, text="🔍 Xem & Sửa", width=85, height=26,
                command=lambda s=sub: self.show_review_modal(s)
            )
            btn_view.pack(side="left", padx=3)

            btn_del_single = ctk.CTkButton(
                action_sub_frame, text="❌", width=28, height=26, fg_color="#C0392B", hover_color="#962D22",
                command=lambda sid=sub.submission_id: self.delete_single_submission(sid)
            )
            btn_del_single.pack(side="left", padx=3)

    def delete_single_submission(self, submission_id: str):
        if messagebox.askyesno("Xác nhận", "Xóa kết quả chấm của bài này?"):
            self.current_submissions = [s for s in self.current_submissions if s.submission_id != submission_id]
            save_submissions(self.current_exam.exam_id, self.current_submissions)
            self.render_submission_table()

    def clear_all_submissions_for_exam(self):
        if not self.current_submissions:
            return
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa TOÀN BỘ {len(self.current_submissions)} bài chấm của kỳ thi này?"):
            self.current_submissions = []
            save_submissions(self.current_exam.exam_id, self.current_submissions)
            self.render_submission_table()
            messagebox.showinfo("Thành công", "Đã xóa toàn bộ kết quả chấm của bài thi này!")

    def pick_submission_images(self):
        files = filedialog.askopenfilenames(
            title="Chọn các file ảnh bài làm",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if files:
            self.selected_image_files = list(files)
            self.lbl_selected_status.configure(text=f"Đã chọn {len(files)} file ảnh.")

    def pick_submission_folder(self):
        folder = filedialog.askdirectory(title="Chọn thư mục chứa ảnh bài làm")
        if folder:
            valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}
            found = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in valid_exts]
            if found:
                self.selected_image_files = found
                self.lbl_selected_status.configure(text=f"Đã chọn {len(found)} file ảnh từ thư mục.")
            else:
                messagebox.showwarning("Thông báo", "Không tìm thấy file ảnh hợp lệ trong thư mục này.")

    def start_batch_grading_thread(self):
        # KHÔNG tự ý lấy sample demo khi người dùng chưa chọn ảnh
        if not self.selected_image_files:
            messagebox.showwarning(
                "Chưa chọn ảnh", 
                "Vui lòng chọn ít nhất một file ảnh bài làm để bắt đầu chấm!\n(Bấm '🖼️ Chọn ảnh bài làm' hoặc '📁 Chọn thư mục ảnh')"
            )
            return

        self.btn_start_grading.configure(state="disabled")
        threading.Thread(target=self.run_batch_grading, daemon=True).start()

    def run_batch_grading(self):
        total = len(self.selected_image_files)
        new_submissions = list(self.current_submissions)

        for idx, img_path in enumerate(self.selected_image_files, start=1):
            fname = os.path.basename(img_path)
            
            # Cập nhật tiến độ trên luồng chính (Thread-safe)
            self.after(0, lambda i=idx, f=fname: (
                self.lbl_progress.configure(text=f"Đang chấm {i}/{total}: {f}..."),
                self.progress_bar.set(i / total)
            ))

            name_part = os.path.splitext(fname)[0]
            tokens = name_part.split("_")
            s_name = tokens[1] if len(tokens) > 1 and not tokens[1].isdigit() else ""

            try:
                sub = process_single_submission(
                    image_path=img_path,
                    exam=self.current_exam,
                    student_name_override=s_name
                )
            except Exception as e:
                sub = Submission(
                    submission_id=f"sub_{name_part}",
                    exam_id=self.current_exam.exam_id,
                    image_path=img_path,
                    status="Lỗi",
                    error_message=f"Lỗi khi đọc file: {str(e)}"
                )

            # Thay thế nếu đã tồn tại cùng submission_id, hoặc thêm mới
            existing_idx = next((i for i, s in enumerate(new_submissions) if s.submission_id == sub.submission_id), -1)
            if existing_idx >= 0:
                new_submissions[existing_idx] = sub
            else:
                new_submissions.append(sub)

        # Chuyển toàn bộ cập nhật dữ liệu và giao diện về luồng chính (Thread-safe)
        def on_grading_complete():
            self.current_submissions = new_submissions
            save_submissions(self.current_exam.exam_id, self.current_submissions)
            self.lbl_progress.configure(text=f"Hoàn thành! Đã chấm xong {total} bài thi.")
            self.btn_start_grading.configure(state="normal")
            self.render_submission_table()
            messagebox.showinfo("Hoàn thành", f"Đã quét và chấm xong {total} bài làm!")

        self.after(0, on_grading_complete)

    # =================================================================
    # VIEW 4: REVIEW CHI TIẾT & SỬA LỖI TAY (CHỈNH SỬA & CHẤM LẠI TRỰC TIẾP)
    # =================================================================
    def show_review_modal(self, sub: Submission):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Xem chi tiết & Sửa bài: {sub.student_name or sub.student_id}")
        modal.geometry("1180, 800")
        modal.minsize(980, 680)

        # Đưa modal lên trên cùng
        modal.attributes("-topmost", True)
        modal.focus_force()

        # Layout 2 cột: Trái là ảnh overlay, Phải là bảng kết quả và nút sửa
        modal.grid_columnconfigure(0, weight=3)
        modal.grid_columnconfigure(1, weight=2)
        modal.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # CỘT TRÁI: HIỂN THỊ ẢNH OVERLAY KẾT QUẢ CHẤM
        # -------------------------------------------------------------
        left_frame = ctk.CTkFrame(modal)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(left_frame, text="Ảnh bài thi đã chấm (OpenCV Overlay):", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=5)

        img_path = sub.annotated_image_path if (sub.annotated_image_path and os.path.exists(sub.annotated_image_path)) else sub.image_path
        if os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path)
                pil_img.thumbnail((620, 720))
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                lbl_img = ctk.CTkLabel(left_frame, image=ctk_img, text="")
                lbl_img.pack(expand=True, padx=5, pady=5)
            except Exception as e:
                ctk.CTkLabel(left_frame, text=f"Lỗi hiển thị ảnh: {e}").pack(pady=20)
        else:
            ctk.CTkLabel(left_frame, text="Không tìm thấy file ảnh bài làm.").pack(pady=40)

        # -------------------------------------------------------------
        # CỘT PHẢI: KẾT QUẢ VÀ BẢNG SỬA TAY
        # -------------------------------------------------------------
        right_frame = ctk.CTkScrollableFrame(modal)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(right_frame, text="THÔNG TIN & SỬA BÀI THI", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))

        info_box = ctk.CTkFrame(right_frame)
        info_box.pack(fill="x", pady=5)

        # Họ tên
        ctk.CTkLabel(info_box, text="Họ tên thí sinh:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ent_modal_name = ctk.CTkEntry(info_box, width=200)
        ent_modal_name.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ent_modal_name.insert(0, sub.student_name or f"Thí sinh SBD {sub.student_id}")

        # SBD & Mã đề
        ctk.CTkLabel(info_box, text="Số báo danh:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ent_modal_sbd = ctk.CTkEntry(info_box, width=120)
        ent_modal_sbd.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        ent_modal_sbd.insert(0, sub.student_id or "000")

        ctk.CTkLabel(info_box, text="Mã đề thi:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ent_modal_code = ctk.CTkEntry(info_box, width=120)
        ent_modal_code.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        ent_modal_code.insert(0, sub.exam_code or "101")

        # Điểm số hiện tại
        lbl_modal_score = ctk.CTkLabel(
            info_box, 
            text=f"Tổng điểm: {sub.total_score:.2f} / 10.0", 
            font=ctk.CTkFont(weight="bold", size=15), text_color="#E74C3C"
        )
        lbl_modal_score.grid(row=3, column=0, columnspan=2, padx=10, pady=(5, 5), sticky="w")

        # Cảnh báo SBD / Mã đề nghi vấn nếu có
        if "?" in (sub.exam_code or "") or "?" in (sub.student_id or "") or sub.error_message:
            warn_header_txt = f"⚠️ Cảnh báo: {sub.error_message or 'SBD/Mã đề chưa rõ ràng'}. Vui lòng kiểm tra và sửa lại!"
            lbl_modal_warn = ctk.CTkLabel(
                info_box, text=warn_header_txt, text_color="#C0392B",
                font=ctk.CTkFont(weight="bold", size=12), wraplength=420, justify="left"
            )
            lbl_modal_warn.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="w")

        # Bảng đối soát thông minh: OCR & Excel Roster
        roster_name, roster_cls = lookup_student_in_roster(sub.student_id, getattr(self.current_exam, "student_roster", {}))
        ocr_name = (sub.ocr_data or {}).get("name", "")

        match_frame = ctk.CTkFrame(right_frame, fg_color=("gray95", "gray25"), corner_radius=6)
        match_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            match_frame, 
            text="🔍 ĐỐI SOÁT TÊN (OCR & EXCEL ROSTER):", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(6, 2))

        # Dòng thông tin OCR
        ocr_row = ctk.CTkFrame(match_frame, fg_color="transparent")
        ocr_row.pack(fill="x", padx=10, pady=2)
        ocr_text = f"• OCR trên phiếu: '{ocr_name}'" if ocr_name else "• OCR trên phiếu: (Không nhận dạng được chữ in)"
        ctk.CTkLabel(ocr_row, text=ocr_text, font=ctk.CTkFont(size=12)).pack(side="left")
        if ocr_name:
            def apply_ocr_name():
                ent_modal_name.delete(0, "end")
                ent_modal_name.insert(0, ocr_name)
            ctk.CTkButton(ocr_row, text="Dùng tên OCR", width=95, height=22, command=apply_ocr_name).pack(side="right")

        # Dòng thông tin Excel Roster
        roster_row = ctk.CTkFrame(match_frame, fg_color="transparent")
        roster_row.pack(fill="x", padx=10, pady=(2, 6))
        if roster_name:
            r_text = f"• File Excel ({roster_cls}): '{roster_name}'"
            ctk.CTkLabel(roster_row, text=r_text, text_color="#27AE60", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            def apply_roster_name():
                ent_modal_name.delete(0, "end")
                ent_modal_name.insert(0, roster_name)
            ctk.CTkButton(roster_row, text="Dùng tên Excel", width=95, height=22, command=apply_roster_name).pack(side="right")
        else:
            ctk.CTkLabel(roster_row, text="• File Excel: SBD chưa có trong danh sách", text_color="#7F8C8D", font=ctk.CTkFont(size=12)).pack(side="left")

        if sub.needs_review:
            warn_lbl = ctk.CTkLabel(
                right_frame, text="⚠️ BÀI CẦN KIỂM TRA (Tẩy mờ/tô trùng ô)", 
                text_color="#F39C12", font=ctk.CTkFont(weight="bold")
            )
            warn_lbl.pack(anchor="w", pady=5)

        ctk.CTkLabel(
            right_frame, text="Chi tiết từng câu (Có thể chọn sửa lại đáp án):", 
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(15, 5))

        # Lưu trữ các widget chỉnh sửa đáp án
        editor_widgets: Dict[str, Any] = {}

        # 1. Chế độ Full MCQ
        if self.current_exam.mode == ExamMode.FULL_MCQ:
            ans_dict = sub.extracted_data.get("answers", {})
            active_key = self.current_exam.answer_keys.get(sub.exam_code, {})
            if not active_key and self.current_exam.answer_keys:
                valid_codes = ", ".join(self.current_exam.answer_keys.keys()) or "Chưa có"
                ctk.CTkLabel(
                    right_frame,
                    text=f"⚠️ Mã đề '{sub.exam_code}' không có đáp án! (Mã hợp lệ: {valid_codes}). Hãy sửa mã đề rồi bấm 'Lưu & Chấm lại'.",
                    text_color="#C0392B", font=ctk.CTkFont(weight="bold", size=12),
                    wraplength=420, justify="left"
                ).pack(anchor="w", pady=5, padx=5)
            _num_q_editor = getattr(self.current_exam, "num_questions", 40) or 40

            for q_i in range(1, _num_q_editor + 1):
                ans_val = ans_dict.get(q_i) or ans_dict.get(str(q_i)) or ""
                correct_k = active_key.get(q_i) or active_key.get(str(q_i)) or ""

                item_row = ctk.CTkFrame(right_frame)
                item_row.pack(fill="x", pady=2)

                ctk.CTkLabel(item_row, text=f"Câu {q_i:02d}:", width=65).pack(side="left", padx=5)

                opt_cbo = ctk.CTkOptionMenu(
                    item_row, values=["A", "B", "C", "D", "Trống"], width=90
                )
                cur_sel = ans_val if ans_val in ["A", "B", "C", "D"] else "Trống"
                opt_cbo.set(cur_sel)
                opt_cbo.pack(side="left", padx=5)
                editor_widgets[f"mcq_{q_i}"] = opt_cbo

                # Hiển thị đáp án đúng để đối chiếu
                is_correct = (cur_sel == correct_k)
                res_tag = "✓ Đúng" if is_correct else f"✗ Sai (Đ.Án: {correct_k})"
                tag_col = "#27AE60" if is_correct else "#C0392B"
                ctk.CTkLabel(item_row, text=res_tag, text_color=tag_col, width=120).pack(side="left", padx=5)

        # 2. Chế độ THPT mới
        else:
            active_key = self.current_exam.answer_keys.get(sub.exam_code, {})
            if not active_key and self.current_exam.answer_keys:
                valid_codes = ", ".join(self.current_exam.answer_keys.keys()) or "Chưa có"
                ctk.CTkLabel(
                    right_frame,
                    text=f"⚠️ Mã đề '{sub.exam_code}' không có đáp án! (Mã hợp lệ: {valid_codes}). Hãy sửa mã đề rồi bấm 'Lưu & Chấm lại'.",
                    text_color="#C0392B", font=ctk.CTkFont(weight="bold", size=12),
                    wraplength=420, justify="left"
                ).pack(anchor="w", pady=5, padx=5)

            # PHẦN I
            ctk.CTkLabel(right_frame, text="[Phần I: 12 câu 4 lựa chọn]", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
            p1_dict = sub.extracted_data.get("part1", {})
            key_p1 = active_key.get("part1", {}) if active_key else {}

            for q_i in range(1, 13):
                ans_val = p1_dict.get(q_i) or p1_dict.get(str(q_i)) or ""
                correct_k = key_p1.get(q_i) or key_p1.get(str(q_i)) or ""

                item_row = ctk.CTkFrame(right_frame)
                item_row.pack(fill="x", pady=2)

                ctk.CTkLabel(item_row, text=f"Câu {q_i:02d}:", width=65).pack(side="left", padx=5)
                opt_cbo = ctk.CTkOptionMenu(item_row, values=["A", "B", "C", "D", "Trống"], width=90)
                cur_sel = ans_val if ans_val in ["A", "B", "C", "D"] else "Trống"
                opt_cbo.set(cur_sel)
                opt_cbo.pack(side="left", padx=5)
                editor_widgets[f"p1_{q_i}"] = opt_cbo

                is_correct = (cur_sel == correct_k)
                res_tag = "✓ Đúng" if is_correct else f"✗ Sai (Key: {correct_k})"
                tag_col = "#27AE60" if is_correct else "#C0392B"
                ctk.CTkLabel(item_row, text=res_tag, text_color=tag_col, width=120).pack(side="left", padx=5)

            # PHẦN II
            ctk.CTkLabel(right_frame, text="[Phần II: 4 câu Đúng / Sai]", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
            p2_dict = sub.extracted_data.get("part2", {})
            key_p2 = active_key.get("part2", {}) if active_key else {}

            for q_i in range(1, 5):
                q_subs = p2_dict.get(q_i) or p2_dict.get(str(q_i)) or {}
                k_subs = key_p2.get(q_i) or key_p2.get(str(q_i)) or {}

                ctk.CTkLabel(right_frame, text=f"Câu {q_i}:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(4, 0))
                for sub_k in ['a', 'b', 'c', 'd']:
                    val_s = str(q_subs.get(sub_k, "")).strip().upper()
                    key_val = str(k_subs.get(sub_k, "")).strip().upper()
                    item_row = ctk.CTkFrame(right_frame)
                    item_row.pack(fill="x", pady=1)

                    ctk.CTkLabel(item_row, text=f"  ý {sub_k}):", width=70).pack(side="left", padx=5)
                    cbo_ds = ctk.CTkOptionMenu(item_row, values=["Đ", "S", "Trống"], width=80)
                    cur_sel = "Đ" if val_s in {"Đ", "D"} else ("S" if val_s in {"S", "F"} else "Trống")
                    cbo_ds.set(cur_sel)
                    cbo_ds.pack(side="left", padx=5)
                    editor_widgets[f"p2_{q_i}_{sub_k}"] = cbo_ds

                    is_c = (cur_sel == key_val)
                    tag_text = "✓" if is_c else f"✗ (Key: {key_val})"
                    tag_col = "#27AE60" if is_c else "#C0392B"
                    ctk.CTkLabel(item_row, text=tag_text, text_color=tag_col, width=90).pack(side="left", padx=5)

            # PHẦN III
            ctk.CTkLabel(right_frame, text="[Phần III: 6 câu Trả lời ngắn]", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
            p3_dict = sub.extracted_data.get("part3", {})
            key_p3 = active_key.get("part3", {}) if active_key else {}

            for q_i in range(1, 7):
                val_num = str(p3_dict.get(q_i) or p3_dict.get(str(q_i)) or "")
                key_num = str(key_p3.get(q_i) or key_p3.get(str(q_i)) or "")

                item_row = ctk.CTkFrame(right_frame)
                item_row.pack(fill="x", pady=2)

                ctk.CTkLabel(item_row, text=f"Câu {q_i}:", width=65).pack(side="left", padx=5)
                ent_num = ctk.CTkEntry(item_row, width=100)
                ent_num.insert(0, val_num)
                ent_num.pack(side="left", padx=5)
                editor_widgets[f"p3_{q_i}"] = ent_num

                is_c = (val_num.replace(',', '.') == key_num.replace(',', '.') and bool(val_num))
                tag_text = "✓" if is_c else f"✗ (Key: {key_num})"
                tag_col = "#27AE60" if is_c else "#C0392B"
                ctk.CTkLabel(item_row, text=tag_text, text_color=tag_col, width=120).pack(side="left", padx=5)

        # Nút Lưu thay đổi & Chấm lại
        btn_action_box = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_action_box.pack(fill="x", pady=(20, 10))

        def save_and_regrade_submission():
            # 1. Cập nhật thông tin thí sinh
            new_name = ent_modal_name.get().strip()
            new_sbd = ent_modal_sbd.get().strip()
            new_code = ent_modal_code.get().strip()

            sub.student_name = new_name
            sub.student_id = new_sbd
            sub.exam_code = new_code

            # Kiểm tra mã đề: KHÔNG tự ý lấy key khác nếu mã đề không khớp!
            active_key = self.current_exam.answer_keys.get(sub.exam_code)
            if not active_key:
                valid_codes = ", ".join(self.current_exam.answer_keys.keys()) or "Chưa có"
                messagebox.showerror(
                    "Mã đề không hợp lệ",
                    f"Mã đề '{sub.exam_code}' không có trong bộ đáp án của kỳ thi!\n"
                    f"Các mã đề hợp lệ hiện có: {valid_codes}\n"
                    f"Vui lòng sửa lại đúng mã đề trước khi chấm lại."
                )
                return

            # 2. Cập nhật đáp án đã sửa
            if self.current_exam.mode == ExamMode.FULL_MCQ:
                new_answers = {}
                num_q = getattr(self.current_exam, "num_questions", 40) or 40
                for q_i in range(1, num_q + 1):
                    w = editor_widgets.get(f"mcq_{q_i}")
                    val = w.get() if w else None
                    new_answers[q_i] = val if val != "Trống" else None
                sub.extracted_data["answers"] = new_answers

                res = grade_full_mcq(new_answers, active_key, self.current_exam.max_score)
                sub.total_score = res["score"]
                sub.correct_count = res["correct_count"]
                sub.wrong_count = res["wrong_count"]
                sub.blank_count = res["blank_count"]
                sub.status = "Đã chấm"
                sub.needs_review = False
                sub.error_message = ""
            else:
                # Cập nhật P1, P2, P3
                new_p1 = {}
                for q_i in range(1, 13):
                    w = editor_widgets.get(f"p1_{q_i}")
                    val = w.get() if w else None
                    new_p1[q_i] = val if val != "Trống" else None

                new_p2 = {}
                for q_i in range(1, 5):
                    new_p2[q_i] = {}
                    for sub_k in ['a', 'b', 'c', 'd']:
                        w = editor_widgets.get(f"p2_{q_i}_{sub_k}")
                        val = w.get() if w else None
                        new_p2[q_i][sub_k] = val if val != "Trống" else None

                new_p3 = {}
                for q_i in range(1, 7):
                    w = editor_widgets.get(f"p3_{q_i}")
                    new_p3[q_i] = w.get().strip() if w else ""

                sub.extracted_data["part1"] = new_p1
                sub.extracted_data["part2"] = new_p2
                sub.extracted_data["part3"] = new_p3

                res = grade_thpt_2025(sub.extracted_data, active_key)
                sub.score_part1 = res["score_part1"]
                sub.score_part2 = res["score_part2"]
                sub.score_part3 = res["score_part3"]
                sub.total_score = res["total_score"]
                sub.correct_count = res["p1_correct"] + res["p3_correct"]
                sub.status = "Đã chấm"
                sub.needs_review = False
                sub.error_message = ""

            # Vẽ lại ảnh overlay từ ảnh đã căn chỉnh (align_paper) để tránh lệch tọa độ
            if sub.image_path and os.path.exists(sub.image_path):
                try:
                    succ_align, aligned_img, _ = align_paper(sub.image_path)
                    if not succ_align or aligned_img is None:
                        aligned_img = imread_utf8(sub.image_path)

                    if aligned_img is not None:
                        new_overlay = draw_grading_overlay(
                            aligned_img=aligned_img,
                            mode=self.current_exam.mode,
                            extracted_data=sub.extracted_data,
                            answer_key=active_key,
                            score_info=res
                        )
                        if not sub.annotated_image_path:
                            sub.annotated_image_path = os.path.join(
                                os.path.join(PROJECT_ROOT, "data", "annotated"),
                                f"result_{os.path.basename(sub.image_path)}"
                            )
                        imwrite_utf8(sub.annotated_image_path, new_overlay)

                        # Cập nhật ảnh hiển thị trực tiếp trên modal
                        try:
                            pil_img = Image.open(sub.annotated_image_path)
                            pil_img.thumbnail((620, 720))
                            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                            lbl_img.configure(image=ctk_img)
                            lbl_img.image = ctk_img
                        except Exception as reload_err:
                            print("Lỗi reload preview:", reload_err)
                except Exception as ex:
                    print("Lỗi cập nhật ảnh overlay:", ex)

            # Lưu vào storage
            save_submissions(self.current_exam.exam_id, self.current_submissions)
            self.render_submission_table()
            lbl_modal_score.configure(text=f"Tổng điểm: {sub.total_score:.2f} / 10.0")
            messagebox.showinfo("Thành công", f"Đã cập nhật bài làm! Điểm số mới: {sub.total_score:.2f}")


        btn_save_regrade = ctk.CTkButton(
            btn_action_box, text="💾 LƯU & CHẤM LẠI BÀI NÀY", height=40,
            fg_color="#27AE60", hover_color="#1E8449", font=ctk.CTkFont(weight="bold"),
            command=save_and_regrade_submission
        )
        btn_save_regrade.pack(fill="x", pady=5)

    # =================================================================
    # VIEW 5: THỐNG KÊ & XUẤT EXCEL (CHỌN KỲ THI TRỰC TIẾP)
    # =================================================================
    def show_stats_view(self):
        self.clear_content()

        exams = get_all_exams()
        if not exams:
            messagebox.showinfo("Thông báo", "Vui lòng chọn hoặc tạo một bài kiểm tra trước!")
            self.show_exam_list_view()
            return

        if not self.current_exam:
            self.current_exam = exams[0]
            self.current_submissions = get_submissions(self.current_exam.exam_id)

        container = ctk.CTkScrollableFrame(self.content_frame)
        container.pack(fill="both", expand=True, padx=25, pady=20)

        # Thanh chọn kỳ thi trên màn hình thống kê
        stats_top_bar = ctk.CTkFrame(container, fg_color="#1F4E78", corner_radius=8)
        stats_top_bar.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            stats_top_bar, text="📊 Chọn kỳ thi xem báo cáo:", 
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF"
        ).pack(side="left", padx=15, pady=10)

        exam_options = self.get_exam_display_options()
        current_opt = self.get_current_exam_display_label()
        if current_opt not in exam_options:
            current_opt = exam_options[0]

        cbo_stats_exam = ctk.CTkOptionMenu(
            stats_top_bar, values=exam_options, width=450,
            command=self.on_stats_exam_changed
        )
        cbo_stats_exam.set(current_opt)
        cbo_stats_exam.pack(side="left", padx=5, pady=10)

        title = ctk.CTkLabel(
            container, text=f"Báo Cáo Thống Kê: {self.current_exam.title}", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 15))

        # Phân loại bài nộp: Loại bỏ bài lỗi khỏi thống kê điểm số
        valid_subs = [s for s in self.current_submissions if s.status != "Lỗi"]
        error_subs = [s for s in self.current_submissions if s.status == "Lỗi"]
        review_subs = [s for s in self.current_submissions if s.status == "Cần kiểm tra"]
        scored_subs = [
            s for s in valid_subs 
            if s.status == "Đã chấm" or (s.status == "Cần kiểm tra" and (s.exam_code in (self.current_exam.answer_keys or {})))
        ]

        scores = [s.total_score for s in scored_subs]
        num_scored = len(scores)

        # 4 Thẻ KPI
        kpi_frame = ctk.CTkFrame(container, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=10)
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def make_kpi(col, label, value, color):
            box = ctk.CTkFrame(kpi_frame, fg_color=color, corner_radius=8)
            box.grid(row=0, column=col, padx=8, pady=5, sticky="ew")
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=12), text_color="#FFFFFF").pack(pady=(10, 2))
            ctk.CTkLabel(box, text=str(value), font=ctk.CTkFont(size=22, weight="bold"), text_color="#FFFFFF").pack(pady=(0, 10))

        avg = round(sum(scores) / max(num_scored, 1), 2) if num_scored else 0.0
        max_s = max(scores) if scores else 0.0
        min_s = min(scores) if scores else 0.0

        make_kpi(0, "Tổng bài tiếp nhận", f"{len(self.current_submissions)} (Lỗi: {len(error_subs)})", "#2980B9")
        make_kpi(1, "Điểm TB (bài hợp lệ)", avg, "#27AE60")
        make_kpi(2, "Điểm cao nhất", max_s, "#8E44AD")
        make_kpi(3, "Cần kiểm tra / Lỗi", f"{len(review_subs)} / {len(error_subs)}", "#E67E22")

        # Phân loại học sinh (chỉ tính trên bài thi hợp lệ)
        dist_frame = ctk.CTkFrame(container)
        dist_frame.pack(fill="x", pady=15, padx=5)

        ctk.CTkLabel(
            dist_frame, 
            text=f"Phân bố kết quả xếp loại ({num_scored} bài hợp lệ - đã loại {len(error_subs)} bài lỗi):", 
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        c_gioi = sum(1 for s in scores if s >= 8.0)
        c_kha = sum(1 for s in scores if 6.5 <= s < 8.0)
        c_tb = sum(1 for s in scores if 5.0 <= s < 6.5)
        c_yeu = sum(1 for s in scores if s < 5.0)

        dist_grid = ctk.CTkFrame(dist_frame, fg_color="transparent")
        dist_grid.pack(fill="x", padx=15, pady=5)
        dist_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def make_rank_badge(col, name, count, color):
            b = ctk.CTkFrame(dist_grid, fg_color=("gray85", "gray25"), corner_radius=6)
            b.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            ctk.CTkLabel(b, text=name, font=ctk.CTkFont(size=12, weight="bold"), text_color=color).pack(pady=(5, 0))
            ctk.CTkLabel(b, text=f"{count} bài ({round(count/max(num_scored,1)*100, 1)}%)").pack(pady=(0, 5))

        make_rank_badge(0, "Giỏi (>=8.0đ)", c_gioi, "#27AE60")
        make_rank_badge(1, "Khá (6.5-7.9đ)", c_kha, "#2980B9")
        make_rank_badge(2, "Trung bình (5.0-6.4đ)", c_tb, "#F39C12")
        make_rank_badge(3, "Chưa đạt (<5.0đ)", c_yeu, "#C0392B")

        # Nút xuất file Excel
        btn_export = ctk.CTkButton(
            container, text="📊 XUẤT BÁO CÁO EXCEL 3 SHEET HOÀN CHỈNH", 
            height=45, fg_color="#27AE60", hover_color="#1E8449",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.export_full_excel_report
        )
        btn_export.pack(fill="x", pady=25, padx=5)

    def on_stats_exam_changed(self, selected_label: str):
        exam = self.get_exam_from_display_label(selected_label)
        if exam:
            self.current_exam = exam
            self.current_submissions = get_submissions(exam.exam_id)
            self.show_stats_view()

    def export_full_excel_report(self):
        if not self.current_submissions:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu bài chấm để xuất báo cáo!")
            return

        out_path = filedialog.asksaveasfilename(
            title="Lưu Báo cáo Excel kết quả thi",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not out_path:
            return

        success = export_exam_results_to_excel(
            exam=self.current_exam,
            submissions=self.current_submissions,
            output_filepath=out_path
        )
        if success:
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo Excel thành công tại:\n{out_path}")
        else:
            messagebox.showerror(
                "Lỗi xuất báo cáo", 
                f"Không thể xuất file Excel báo cáo!\n"
                f"Vui lòng đóng file Excel nếu đang mở trong ứng dụng khác và kiểm tra quyền ghi thư mục."
            )


if __name__ == "__main__":
    app = OMRGradingApp()
    app.mainloop()
