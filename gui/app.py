"""
Module: app.py
Giao diện người dùng Desktop (CustomTkinter) cho Hệ thống nhận diện & chấm phiếu trắc nghiệm 50 câu:
  - Bước 1: Tải phiếu lên (Quản lý ảnh phiếu - Chức năng 1)
  - Bước 2: Đọc phiếu & Chấm điểm (Tiền xử lý, Nhận diện OMR 50 câu & Xử lý theo lô - Chức năng 2, 3, 4)
  - Bước 3: Xuất kết quả (Bảng điểm, Ảnh kết quả trực quan & Xuất file Excel - Chức năng 5)
"""

import os
import sys
import glob
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image

import customtkinter as ctk

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.models import Submission
from core.cv_utils import imread_utf8, imwrite_utf8
from core.grading_engine import grade_submission, parse_answer_string, generate_sample_answer_key
from core.exam_processor import process_single_submission, scan_answer_key_from_image
from core.excel_exporter import export_exam_results_to_excel
from core.sheet_generator import generate_all_samples, generate_50_mcq_template

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class OMRGradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Phần Mềm Nhận Diện & Chấm Phiếu Trắc Nghiệm THPT (50 Câu) - OpenCV")
        self.geometry("1300x820")
        self.minsize(1100, 700)

        # Trạng thái dữ liệu
        self.image_files = []
        self.image_validation_cache = {}
        self.answer_key = generate_sample_answer_key(50)
        self.submissions = []
        self.is_processing = False
        self.selected_sub = None

        self._setup_style()
        self._build_ui()
        self._refresh_answer_key_display()

    def _setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=26,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#202020"
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#2B5B84",
            foreground="#FFFFFF",
            relief="flat"
        )
        self.style.map("Treeview.Heading", background=[('active', '#1F4362')])
        self.style.map("Treeview", background=[('selected', '#CCE4F7')], foreground=[('selected', '#000000')])

    def _build_ui(self):
        # 1. Header Bar
        header_frame = ctk.CTkFrame(self, height=65, corner_radius=0)
        header_frame.pack(fill="x", side="top")

        title_lbl = ctk.CTkLabel(
            header_frame, 
            text="HỆ THỐNG NHẬN DIỆN VÀ CHẤM PHIẾU TRẮC NGHIỆM THPT (50 CÂU)", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        title_lbl.pack(side="left", padx=20, pady=(8, 0))

        sub_lbl = ctk.CTkLabel(
            header_frame, 
            text="Đồ án môn học: Thị giác máy tính (OpenCV) | Quy trình: 1. Tải phiếu lên ➔ 2. Đọc phiếu & Chấm điểm ➔ 3. Xuất kết quả", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray"
        )
        sub_lbl.place(x=20, y=36)

        self.theme_btn = ctk.CTkButton(
            header_frame, 
            text="Giao diện: Tối/Sáng", 
            width=130, 
            height=30,
            command=self._toggle_theme
        )
        self.theme_btn.pack(side="right", padx=20, pady=15)

        # 2. Main Tabview
        self.tabview = ctk.CTkTabview(self, corner_radius=8)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 12))

        self.tab_batch = self.tabview.add("  📋 Quản lý ảnh & Chấm bài theo lô  ")
        self.tab_detail = self.tabview.add("  🔍 Xem chi tiết bài làm & Ảnh kết quả  ")
        self.tab_template = self.tabview.add("  📄 Mẫu phiếu trắng 50 câu & Hướng dẫn  ")

        self._build_tab_batch()
        self._build_tab_detail()
        self._build_tab_template()

    # =========================================================================
    # TAB 1: QUẢN LÝ ẢNH & CHẤM BÀI THEO LÔ
    # =========================================================================
    def _build_tab_batch(self):
        # --- Khung trên: Thiết lập đáp án chuẩn 50 câu ---
        top_ctrl_box = ctk.CTkFrame(self.tab_batch)
        top_ctrl_box.pack(fill="x", padx=10, pady=(6, 8))

        row_ctrl = ctk.CTkFrame(top_ctrl_box, fg_color="transparent")
        row_ctrl.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            row_ctrl, 
            text="Đáp án chuẩn 50 câu:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="left", padx=(0, 10))

        self.entry_key = ctk.CTkEntry(
            row_ctrl, 
            placeholder_text="Nhập chuỗi đáp án 50 câu (VD: 'A B C D...' hoặc 'ABCD...' hoặc '1:A 2:B...')", 
            height=32
        )
        self.entry_key.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_apply_key = ctk.CTkButton(
            row_ctrl, 
            text="Lưu đáp án", 
            width=95, 
            height=32,
            command=self._apply_answer_key_from_entry
        )
        btn_apply_key.pack(side="left", padx=3)

        btn_sample_key = ctk.CTkButton(
            row_ctrl, 
            text="Mẫu mặc định", 
            width=100, 
            height=32,
            fg_color="#4F79A2",
            hover_color="#3B5D7D",
            command=self._set_sample_answer_key
        )
        btn_sample_key.pack(side="left", padx=3)

        btn_import_key = ctk.CTkButton(
            row_ctrl, 
            text="Nạp từ file...", 
            width=95, 
            height=32,
            fg_color="#5A6B7C",
            hover_color="#455260",
            command=self._import_key_from_file
        )
        btn_import_key.pack(side="left", padx=3)

        # Nhãn hiển thị tóm tắt đáp án chuẩn
        self.lbl_key_summary = ctk.CTkLabel(
            top_ctrl_box, 
            text="Đáp án hiện tại: 50 câu (Chưa thiết lập)", 
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#2E7D32"
        )
        self.lbl_key_summary.pack(anchor="w", padx=12, pady=(0, 8))

        # --- Khung giữa chia làm 2 cột: Trái (Quản lý ảnh) | Phải (Tiến trình & Kết quả) ---
        split_frame = ctk.CTkFrame(self.tab_batch, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Cột Trái: Quản lý ảnh phiếu (Chức năng 1)
        left_box = ctk.CTkFrame(split_frame, width=470)
        left_box.pack(side="left", fill="both", expand=False, padx=(10, 5), pady=5)
        left_box.pack_propagate(False)

        left_header = ctk.CTkLabel(
            left_box, 
            text="Bước 1: Tải phiếu trả lời lên (Quản lý ảnh)", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        left_header.pack(anchor="w", padx=12, pady=(10, 6))

        btn_row1 = ctk.CTkFrame(left_box, fg_color="transparent")
        btn_row1.pack(fill="x", padx=10, pady=3)

        ctk.CTkButton(
            btn_row1, text="➕ Tải ảnh phiếu...", width=105, height=30, command=self._action_add_images
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            btn_row1, text="📁 Tải folder...", width=105, height=30, command=self._action_add_directory
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row1, text="⚡ Nạp 7 bài mẫu", width=120, height=30,
            fg_color="#D97724", hover_color="#B55E15", command=self._action_load_sample_dataset
        ).pack(side="left", padx=4)

        btn_row2 = ctk.CTkFrame(left_box, fg_color="transparent")
        btn_row2.pack(fill="x", padx=10, pady=(2, 6))

        ctk.CTkButton(
            btn_row2, text="Xóa ảnh chọn", width=105, height=28,
            fg_color="#A24A4A", hover_color="#803535", command=self._action_remove_selected_image
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_row2, text="Xóa toàn bộ", width=100, height=28,
            fg_color="#6B7280", hover_color="#4B5563", command=self._action_clear_all_images
        ).pack(side="left", padx=5)

        # Bảng danh sách ảnh
        tree_frame_left = tk.Frame(left_box, bg="#FFFFFF")
        tree_frame_left.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_images = ttk.Treeview(
            tree_frame_left, 
            columns=("STT", "FileName", "Size", "Status"), 
            show="headings", 
            selectmode="extended"
        )
        self.tree_images.heading("STT", text="STT")
        self.tree_images.heading("FileName", text="Tên file ảnh")
        self.tree_images.heading("Size", text="Kích thước")
        self.tree_images.heading("Status", text="Kiểm tra")

        self.tree_images.column("STT", width=40, anchor="center")
        self.tree_images.column("FileName", width=180, anchor="w")
        self.tree_images.column("Size", width=95, anchor="center")
        self.tree_images.column("Status", width=95, anchor="center")

        scroll_img_y = ttk.Scrollbar(tree_frame_left, orient="vertical", command=self.tree_images.yview)
        self.tree_images.configure(yscrollcommand=scroll_img_y.set)
        self.tree_images.pack(side="left", fill="both", expand=True)
        scroll_img_y.pack(side="right", fill="y")

        self.lbl_img_status = ctk.CTkLabel(
            left_box, text="Tổng số: 0 ảnh đã nạp", 
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color="gray"
        )
        self.lbl_img_status.pack(anchor="w", padx=12, pady=(2, 8))

        # Cột Phải: Đọc phiếu & Xuất kết quả
        right_box = ctk.CTkFrame(split_frame)
        right_box.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=5)

        right_header = ctk.CTkLabel(
            right_box, 
            text="Bước 2: Đọc phiếu & Bước 3: Xuất kết quả", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        right_header.pack(anchor="w", padx=12, pady=(10, 2))

        stat_bar = ctk.CTkFrame(right_box, fg_color="transparent")
        stat_bar.pack(fill="x", padx=10, pady=(6, 6))

        self.card_total = self._create_stat_card(stat_bar, "Tổng số bài", "0", "#3B82F6")
        self.card_success = self._create_stat_card(stat_bar, "Đọc thành công", "0", "#10B981")
        self.card_warning = self._create_stat_card(stat_bar, "Cần kiểm tra", "0", "#F59E0B")
        self.card_error = self._create_stat_card(stat_bar, "Bị lỗi", "0", "#EF4444")

        ctl_bar = ctk.CTkFrame(right_box, fg_color="transparent")
        ctl_bar.pack(fill="x", padx=10, pady=4)

        self.btn_start_grading = ctk.CTkButton(
            ctl_bar, 
            text="▶ ĐỌC PHIẾU & CHẤM ĐIỂM", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=38,
            fg_color="#1E824C",
            hover_color="#16653A",
            command=self._start_batch_grading
        )
        self.btn_start_grading.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_export_excel = ctk.CTkButton(
            ctl_bar, 
            text="📊 Xuất kết quả (Excel)", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=165,
            height=38,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            command=self._action_export_excel
        )
        self.btn_export_excel.pack(side="right")

        prog_bar_frame = ctk.CTkFrame(right_box, fg_color="transparent")
        prog_bar_frame.pack(fill="x", padx=10, pady=(4, 6))

        self.progress_bar = ctk.CTkProgressBar(prog_bar_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.progress_bar.set(0.0)

        self.lbl_progress = ctk.CTkLabel(
            prog_bar_frame, text="Sẵn sàng", font=ctk.CTkFont(family="Segoe UI", size=11), width=180, anchor="e"
        )
        self.lbl_progress.pack(side="right")

        tree_frame_right = tk.Frame(right_box, bg="#FFFFFF")
        tree_frame_right.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_results = ttk.Treeview(
            tree_frame_right, 
            columns=("STT", "StudentID", "FileName", "Score", "Correct", "Wrong", "Blank", "Status"), 
            show="headings", 
            selectmode="browse"
        )
        self.tree_results.heading("STT", text="STT")
        self.tree_results.heading("StudentID", text="Mã học sinh")
        self.tree_results.heading("FileName", text="Tên file ảnh")
        self.tree_results.heading("Score", text="Điểm /10")
        self.tree_results.heading("Correct", text="Đúng /50")
        self.tree_results.heading("Wrong", text="Sai")
        self.tree_results.heading("Blank", text="Trống")
        self.tree_results.heading("Status", text="Trạng thái")

        self.tree_results.column("STT", width=40, anchor="center")
        self.tree_results.column("StudentID", width=105, anchor="w")
        self.tree_results.column("FileName", width=180, anchor="w")
        self.tree_results.column("Score", width=80, anchor="center")
        self.tree_results.column("Correct", width=85, anchor="center")
        self.tree_results.column("Wrong", width=60, anchor="center")
        self.tree_results.column("Blank", width=60, anchor="center")
        self.tree_results.column("Status", width=100, anchor="center")

        scroll_res_y = ttk.Scrollbar(tree_frame_right, orient="vertical", command=self.tree_results.yview)
        self.tree_results.configure(yscrollcommand=scroll_res_y.set)
        self.tree_results.pack(side="left", fill="both", expand=True)
        scroll_res_y.pack(side="right", fill="y")
        self.tree_results.bind("<Double-1>", self._on_result_double_click)

        bottom_bar = ctk.CTkFrame(right_box, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=10, pady=(2, 6))

        ctk.CTkButton(
            bottom_bar, text="🔍 Xem chi tiết bài đã chọn", width=160, height=28, command=self._view_selected_submission
        ).pack(side="left")

        ctk.CTkLabel(
            bottom_bar, text="(Mẹo: Click đúp vào một dòng học sinh để xem ảnh đã vẽ kết quả)", 
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color="gray"
        ).pack(side="right")

    def _create_stat_card(self, parent, title: str, val: str, color: str):
        card = ctk.CTkFrame(parent, fg_color=color, height=55, corner_radius=6)
        card.pack(side="left", fill="x", expand=True, padx=4)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#FFFFFF").pack(pady=(4, 0))
        lbl_v = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#FFFFFF")
        lbl_v.pack(pady=(0, 4))
        return lbl_v

    # =========================================================================
    # TAB 2: DETAIL & VISUALIZER
    # =========================================================================
    def _build_tab_detail(self):
        top_bar = ctk.CTkFrame(self.tab_detail)
        top_bar.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(top_bar, text="Chọn bài học sinh:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        self.combo_students = ctk.CTkComboBox(
            top_bar, values=["Chưa có kết quả nào"], width=260, command=self._on_combo_student_change
        )
        self.combo_students.pack(side="left", padx=5)

        self.lbl_detail_score = ctk.CTkLabel(
            top_bar, 
            text="Điểm: -- / 10.0  |  Xếp loại: --", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#1E824C"
        )
        self.lbl_detail_score.pack(side="left", padx=25)

        ctk.CTkButton(
            top_bar, text="Mở ảnh gốc", width=110, command=self._open_current_image_external
        ).pack(side="right", padx=10)

        content_box = ctk.CTkFrame(self.tab_detail, fg_color="transparent")
        content_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        table_box = ctk.CTkFrame(content_box, width=380)
        table_box.pack(side="left", fill="both", expand=False, padx=(0, 5))
        table_box.pack_propagate(False)

        ctk.CTkLabel(table_box, text="Chi tiết 50 câu hỏi", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8, 4))

        tree_det_frame = tk.Frame(table_box, bg="#FFFFFF")
        tree_det_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_details = ttk.Treeview(
            tree_det_frame, columns=("Q", "Student", "Key", "Result"), show="headings", selectmode="browse"
        )
        self.tree_details.heading("Q", text="Câu")
        self.tree_details.heading("Student", text="Học sinh")
        self.tree_details.heading("Key", text="Đáp án")
        self.tree_details.heading("Result", text="Kết quả")

        self.tree_details.column("Q", width=55, anchor="center")
        self.tree_details.column("Student", width=85, anchor="center")
        self.tree_details.column("Key", width=75, anchor="center")
        self.tree_details.column("Result", width=85, anchor="center")

        scroll_det = ttk.Scrollbar(tree_det_frame, orient="vertical", command=self.tree_details.yview)
        self.tree_details.configure(yscrollcommand=scroll_det.set)
        self.tree_details.pack(side="left", fill="both", expand=True)
        scroll_det.pack(side="right", fill="y")

        img_box = ctk.CTkFrame(content_box)
        img_box.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            img_box, 
            text="Ảnh bài làm (OpenCV: Xanh = Đúng, Đỏ = Sai, Vàng = Đáp án chuẩn)", 
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.lbl_image_view = ctk.CTkLabel(img_box, text="Chưa có ảnh được chọn", fg_color="#1E1E1E")
        self.lbl_image_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # =========================================================================
    # TAB 3: MẪU PHIẾU TRẮNG 50 CÂU & HƯỚNG DẪN
    # =========================================================================
    def _build_tab_template(self):
        box = ctk.CTkFrame(self.tab_template)
        box.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            box, 
            text="MẪU PHIẾU THI TRẮC NGHIỆM THPT (50 CÂU) & QUY TRÌNH SỬ DỤNG", 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        intro_text = (
            "Phần mềm được thiết kế chuyên biệt cho phiếu trắc nghiệm 50 câu chuẩn THPT:\n"
            "  • Thuật toán Thị giác máy tính (OpenCV) tự động nhận diện và nắn phẳng phối cảnh (Perspective Transform).\n"
            "  • Tự động phân tích mật độ pixel đen để bóc tách đáp án 50 câu, Số Báo Danh và Mã Đề Thi.\n"
            "  • Tự động phát hiện câu bỏ trống, câu tô trùng nhiều đáp án, cảnh báo tẩy lem nhem.\n"
            "  • Chấm điểm chuẩn xác theo thang 10.0 (mỗi câu đúng = 0.2 điểm) và xuất file Excel 3 Sheet đầy đủ."
        )
        ctk.CTkLabel(box, text=intro_text, font=ctk.CTkFont(family="Segoe UI", size=12), justify="left").pack(anchor="w", padx=20, pady=5)

        btn_frame = ctk.CTkFrame(box, fg_color="transparent")
        btn_frame.pack(anchor="w", padx=20, pady=15)

        ctk.CTkButton(
            btn_frame, text="🖨️ Xuất mẫu phiếu trắng 50 câu (PNG)", height=36, command=self._export_blank_template
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="⚡ Sinh lại 7 bài làm mẫu kiểm thử", height=36,
            fg_color="#D97724", hover_color="#B55E15", command=self._regenerate_samples
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            box, text="Quy trình sử dụng gồm 3 bước đơn giản:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 5))

        steps_text = (
            "1. BƯỚC 1 - TẢI PHIẾU LÊN:\n"
            "   Bấm '➕ Tải ảnh phiếu...' hoặc '📁 Tải folder...' để chọn các ảnh phiếu cần chấm (hỗ trợ JPG, PNG).\n"
            "   (Có thể bấm '⚡ Nạp 7 bài mẫu' để thử nghiệm ngay lập tức).\n\n"
            "2. BƯỚC 2 - ĐỌC PHIẾU & CHẤM ĐIỂM:\n"
            "   Bấm nút '▶ ĐỌC PHIẾU & CHẤM ĐIỂM'. Hệ thống sẽ tự động xử lý tuần tự từng ảnh, đọc các câu trả lời,\n"
            "   so sánh với đáp án chuẩn và tính điểm.\n\n"
            "3. BƯỚC 3 - XUẤT KẾT QUẢ:\n"
            "   • Bảng kết quả hiển thị điểm số, số câu đúng/sai/trống của từng học sinh.\n"
            "   • Click đúp vào một học sinh để xem ảnh phiếu đã được khoanh chấm trực quan (Xanh = Đúng, Đỏ = Sai).\n"
            "   • Bấm '📊 Xuất kết quả (Excel)' để lưu báo cáo tổng hợp 3 Sheet."
        )
        ctk.CTkLabel(box, text=steps_text, font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#1E824C", justify="left").pack(anchor="w", padx=20, pady=5)

    # =========================================================================
    # LOGIC QUẢN LÝ ẢNH
    # =========================================================================
    def _action_add_images(self):
        files = filedialog.askopenfilenames(
            title="Chọn các ảnh phiếu trả lời",
            filetypes=[("Ảnh phiếu thi", "*.jpg;*.jpeg;*.png"), ("Tất cả file", "*.*")]
        )
        if not files:
            return
        new_count = 0
        for f in files:
            norm_path = os.path.abspath(f)
            if norm_path not in self.image_files:
                self.image_files.append(norm_path)
                new_count += 1
        self._refresh_image_list()
        if new_count > 0:
            self._update_progress_status(f"Đã thêm {new_count} ảnh vào danh sách.")

    def _action_add_directory(self):
        dir_path = filedialog.askdirectory(title="Chọn thư mục chứa ảnh phiếu thi")
        if not dir_path:
            return
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]
        found = []
        for pat in patterns:
            found.extend(glob.glob(os.path.join(dir_path, pat)))
        new_count = 0
        for f in sorted(found):
            norm_path = os.path.abspath(f)
            if norm_path not in self.image_files:
                self.image_files.append(norm_path)
                new_count += 1
        self._refresh_image_list()
        messagebox.showinfo("Thêm thư mục", f"Đã quét và thêm {new_count} ảnh từ thư mục:\n{dir_path}")

    def _action_load_sample_dataset(self):
        sample_dir = os.path.join(PROJECT_ROOT, "dataset", "sample_submissions_50cau")
        if not os.path.exists(sample_dir):
            generate_all_samples()

        patterns = ["*.jpg", "*.jpeg", "*.png"]
        found = []
        for pat in patterns:
            found.extend(glob.glob(os.path.join(sample_dir, pat)))

        self.image_files = [os.path.abspath(f) for f in sorted(found)]
        self._refresh_image_list()
        self._update_progress_status(f"Đã nạp {len(self.image_files)} ảnh bài làm mẫu 50 câu.")

    def _action_remove_selected_image(self):
        selected_items = self.tree_images.selection()
        if not selected_items:
            messagebox.showwarning("Thông báo", "Vui lòng chọn ít nhất một ảnh để xóa.")
            return
        removed = 0
        for item_id in selected_items:
            vals = self.tree_images.item(item_id, "values")
            if vals:
                fname = vals[1]
                for path in list(self.image_files):
                    if os.path.basename(path) == fname:
                        self.image_files.remove(path)
                        removed += 1
                        break
        self._refresh_image_list()
        self._update_progress_status(f"Đã xóa {removed} ảnh.")

    def _action_clear_all_images(self):
        if not self.image_files:
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ ảnh khỏi danh sách?"):
            self.image_files.clear()
            self._refresh_image_list()
            self._update_progress_status("Đã làm trống danh sách ảnh.")

    def _refresh_image_list(self):
        for item in self.tree_images.get_children():
            self.tree_images.delete(item)

        valid_count = 0
        for idx, img_path in enumerate(self.image_files, start=1):
            fname = os.path.basename(img_path)
            if img_path not in self.image_validation_cache:
                is_valid, size_str, msg = self._validate_image_file(img_path)
                self.image_validation_cache[img_path] = (is_valid, size_str, msg)
            else:
                is_valid, size_str, msg = self.image_validation_cache[img_path]

            status_text = "Hợp lệ" if is_valid else f"Lỗi ({msg})"
            if is_valid:
                valid_count += 1
            self.tree_images.insert("", "end", values=(idx, fname, size_str, status_text))

        self.lbl_img_status.configure(
            text=f"Tổng số: {len(self.image_files)} ảnh ({valid_count} hợp lệ, {len(self.image_files) - valid_count} lỗi)"
        )
        self.card_total.configure(text=str(len(self.image_files)))

    def _validate_image_file(self, path: str):
        if not os.path.exists(path):
            return False, "--", "Không tồn tại"
        ext = os.path.splitext(path)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            return False, "--", "Định dạng lạ"
        try:
            img = imread_utf8(path)
            if img is None:
                return False, "--", "Không giải mã được"
            h, w = img.shape[:2]
            return True, f"{w}x{h}", "OK"
        except Exception:
            return False, "--", "Lỗi đọc"

    # =========================================================================
    # LOGIC CẤU HÌNH ĐÁP ÁN
    # =========================================================================
    def _apply_answer_key_from_entry(self):
        text = self.entry_key.get().strip()
        if not text:
            messagebox.showwarning("Thông báo", "Vui lòng nhập chuỗi đáp án chuẩn.")
            return

        parsed = parse_answer_string(text, max_q=50)
        if not parsed:
            messagebox.showerror("Lỗi", "Không tìm thấy đáp án hợp lệ (A, B, C, D) trong chuỗi vừa nhập.")
            return

        self.answer_key = parsed
        self._refresh_answer_key_display()
        messagebox.showinfo("Thành công", f"Đã lưu thành công đáp án chuẩn cho {len(parsed)}/50 câu hỏi!")

    def _set_sample_answer_key(self):
        self.answer_key = generate_sample_answer_key(50)
        sample_str = " ".join([self.answer_key[i] for i in range(1, 51)])
        self.entry_key.delete(0, "end")
        self.entry_key.insert(0, sample_str)
        self._refresh_answer_key_display()

    def _import_key_from_file(self):
        filepath = filedialog.askopenfilename(
            title="Chọn file đáp án",
            filetypes=[("File văn bản hoặc Excel", "*.txt;*.xlsx"), ("Tất cả", "*.*")]
        )
        if not filepath:
            return

        ext = os.path.splitext(filepath)[1].lower()
        try:
            if ext == ".txt":
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                parsed = parse_answer_string(content, max_q=50)
            elif ext == ".xlsx":
                import openpyxl
                wb = openpyxl.load_workbook(filepath, data_only=True)
                ws = wb.active
                parsed = {}
                for row in ws.iter_rows(values_only=True):
                    if not row or len(row) < 2:
                        continue
                    c1, c2 = str(row[0]).strip(), str(row[1]).strip().upper()
                    if c1.isdigit() and c2 in ['A', 'B', 'C', 'D']:
                        q = int(c1)
                        if 1 <= q <= 50:
                            parsed[q] = c2

            if parsed:
                self.answer_key = parsed
                sample_str = " ".join([self.answer_key.get(i, "") for i in range(1, len(parsed) + 1)])
                self.entry_key.delete(0, "end")
                self.entry_key.insert(0, sample_str)
                self._refresh_answer_key_display()
                messagebox.showinfo("Nạp đáp án", f"Đã nạp thành công {len(parsed)} đáp án từ file!")
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy cấu trúc đáp án hợp lệ trong file.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")

    def _refresh_answer_key_display(self):
        total = len(self.answer_key)
        first_10 = " ".join([f"{i}:{self.answer_key.get(i, '?')}" for i in range(1, min(11, total + 1))])
        self.lbl_key_summary.configure(
            text=f"Đáp án chuẩn hiện tại: Đã nạp {total}/50 câu | 10 câu đầu: [{first_10} ...]"
        )

    # =========================================================================
    # LOGIC CHẤM BÀI THEO LÔ (BATCH PROCESSING)
    # =========================================================================
    def _start_batch_grading(self):
        if self.is_processing:
            messagebox.showwarning("Thông báo", "Hệ thống đang trong quá trình chấm bài. Vui lòng đợi!")
            return
        if not self.image_files:
            messagebox.showwarning("Thông báo", "Chưa có ảnh nào trong danh sách. Vui lòng bấm 'Thêm ảnh' hoặc 'Nạp ảnh mẫu'!")
            return
        if len(self.answer_key) < 5:
            messagebox.showwarning("Thông báo", "Vui lòng thiết lập đáp án chuẩn trước khi chấm.")
            return

        self.is_processing = True
        self.btn_start_grading.configure(state="disabled", text="⏳ ĐANG XỬ LÝ HÀNG LOẠT...")
        self.submissions.clear()

        for item in self.tree_results.get_children():
            self.tree_results.delete(item)

        thread = threading.Thread(target=self._run_batch_worker, daemon=True)
        thread.start()

    def _run_batch_worker(self):
        total = len(self.image_files)
        success_count = 0
        warning_count = 0
        error_count = 0

        for idx, img_path in enumerate(self.image_files, start=1):
            fname = os.path.basename(img_path)
            pct = idx / total
            status_msg = f"Đang chấm ({idx}/{total}): {fname}..."
            self.after(0, self._update_batch_progress, pct, status_msg)

            try:
                sub = process_single_submission(
                    image_path=img_path,
                    answer_key=self.answer_key
                )
            except Exception as e:
                sub = Submission(
                    submission_id=f"sub_err_{idx}",
                    student_id=os.path.splitext(fname)[0],
                    image_path=img_path,
                    status="Lỗi",
                    error_message=f"Lỗi: {str(e)}"
                )

            self.submissions.append(sub)

            if sub.status == "Thành công":
                success_count += 1
            elif sub.status == "Cảnh báo":
                warning_count += 1
            else:
                error_count += 1

            self.after(0, self._add_result_row_to_table, idx, sub)

        self.after(0, self._finish_batch_grading, total, success_count, warning_count, error_count)

    def _update_batch_progress(self, progress_float: float, text: str):
        self.progress_bar.set(progress_float)
        self.lbl_progress.configure(text=text)

    def _add_result_row_to_table(self, stt: int, sub: Submission):
        st_id = sub.student_id or sub.submission_id
        fname = os.path.basename(sub.image_path)
        score_str = f"{sub.score:.2f}" if sub.status != "Lỗi" else "0.00"
        
        self.tree_results.insert("", "end", values=(
            stt, st_id, fname, score_str,
            f"{sub.correct_count}/50", sub.wrong_count, sub.blank_count,
            sub.status
        ))

    def _finish_batch_grading(self, total: int, success: int, warning: int, error: int):
        self.is_processing = False
        self.btn_start_grading.configure(state="normal", text="▶ BẮT ĐẦU CHẤM BÀI HÀNG LOẠT (50 CÂU)")
        self.progress_bar.set(1.0)
        self.lbl_progress.configure(text=f"Đã hoàn thành {total} bài!")

        self.card_total.configure(text=str(total))
        self.card_success.configure(text=str(success))
        self.card_warning.configure(text=str(warning))
        self.card_error.configure(text=str(error))

        combo_values = [f"{s.student_id or s.submission_id} - {os.path.basename(s.image_path)}" for s in self.submissions]
        if combo_values:
            self.combo_students.configure(values=combo_values)
            self.combo_students.set(combo_values[0])
            self._display_submission_detail(self.submissions[0])

        messagebox.showinfo(
            "Hoàn thành chấm bài",
            f"Đã hoàn tất chấm hàng loạt {total} bài thi 50 câu:\n"
            f"  • Thành công: {success} bài\n"
            f"  • Cần kiểm tra: {warning} bài\n"
            f"  • Bị lỗi: {error} bài"
        )

    def _action_export_excel(self):
        if not self.submissions:
            messagebox.showwarning("Thông báo", "Chưa có kết quả chấm bài nào để xuất Excel.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Lưu báo cáo kết quả thi",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")]
        )
        if not filepath:
            return

        ok = export_exam_results_to_excel(
            submissions=self.submissions,
            answer_key=self.answer_key,
            output_filepath=filepath,
            exam_title="BÁO CÁO KẾT QUẢ THI TRẮC NGHIỆM THPT (50 CÂU)"
        )
        if ok:
            messagebox.showinfo("Xuất Excel", f"Đã xuất báo cáo kết quả thi thành công:\n{filepath}")
        else:
            messagebox.showerror("Lỗi", "Không thể xuất file Excel. Vui lòng kiểm tra quyền ghi.")

    # =========================================================================
    # TAB 2: DETAIL & VISUALIZER
    # =========================================================================
    def _on_result_double_click(self, event):
        self._view_selected_submission()

    def _view_selected_submission(self):
        selected = self.tree_results.selection()
        if not selected:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một dòng học sinh trong bảng kết quả.")
            return

        item = self.tree_results.item(selected[0])
        stt = int(item["values"][0])
        sub = self.submissions[stt - 1]
        self.selected_sub = sub

        val_str = f"{sub.student_id or sub.submission_id} - {os.path.basename(sub.image_path)}"
        self.combo_students.set(val_str)
        self._display_submission_detail(sub)
        self.tabview.set("  🔍 Xem chi tiết bài làm & Ảnh kết quả  ")

    def _on_combo_student_change(self, choice: str):
        for sub in self.submissions:
            val_str = f"{sub.student_id or sub.submission_id} - {os.path.basename(sub.image_path)}"
            if val_str == choice:
                self.selected_sub = sub
                self._display_submission_detail(sub)
                break

    def _display_submission_detail(self, sub: Submission):
        if sub.status == "Lỗi":
            self.lbl_detail_score.configure(
                text=f"[{sub.student_id}]  TRẠNG THÁI: LỖI  |  {sub.error_message}", text_color="#DC2626"
            )
        else:
            rank = "Giỏi" if sub.score >= 8.0 else ("Khá" if sub.score >= 6.5 else ("Trung bình" if sub.score >= 5.0 else "Yếu"))
            text_stat = (
                f"[{sub.student_id}]  ĐIỂM: {sub.score:.2f} / 10.0  |  "
                f"Đúng: {sub.correct_count}/50  |  Sai: {sub.wrong_count}  |  Trống: {sub.blank_count}  |  Loại: {rank}"
            )
            color = "#1E824C" if sub.status == "Thành công" else "#D97724"
            self.lbl_detail_score.configure(text=text_stat, text_color=color)

        for item in self.tree_details.get_children():
            self.tree_details.delete(item)

        details = sub.details
        for q in range(1, 51):
            key = self.answer_key.get(q, "")
            det = details.get(q, {})
            st_ans = det.get("student", "-")
            is_c = det.get("is_correct", False)

            if not st_ans or st_ans == "Trống":
                res_text = "Bỏ trống"
            elif is_c:
                res_text = "Đúng ✓"
            else:
                res_text = "Sai ✗"

            self.tree_details.insert("", "end", values=(f"Câu {q:02d}", st_ans, key, res_text))

        target_path = sub.annotated_image_path if (sub.annotated_image_path and os.path.exists(sub.annotated_image_path)) else sub.image_path
        self._load_and_render_image(target_path)

    def _load_and_render_image(self, img_path: str):
        if not img_path or not os.path.exists(img_path):
            self.lbl_image_view.configure(image=None, text="Không tìm thấy file ảnh.")
            return
        try:
            cv_img = imread_utf8(img_path)
            if cv_img is None:
                self.lbl_image_view.configure(image=None, text="Không thể đọc ảnh.")
                return
            rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            disp_w = 520
            disp_h = int(disp_w * (pil_img.height / pil_img.width))
            if disp_h > 620:
                disp_h = 620
                disp_w = int(disp_h * (pil_img.width / pil_img.height))

            pil_resized = pil_img.resize((disp_w, disp_h), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_resized, dark_image=pil_resized, size=(disp_w, disp_h))
            self.lbl_image_view.configure(image=ctk_img, text="")
            self.lbl_image_view.image = ctk_img
        except Exception as e:
            self.lbl_image_view.configure(image=None, text=f"Lỗi hiển thị ảnh: {e}")

    def _open_current_image_external(self):
        if not self.selected_sub:
            messagebox.showinfo("Thông báo", "Chưa có bài thi nào được chọn.")
            return
        target = self.selected_sub.annotated_image_path or self.selected_sub.image_path
        if target and os.path.exists(target):
            try:
                os.startfile(target)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở ảnh: {e}")

    # =========================================================================
    # TAB 3: MẪU PHIẾU
    # =========================================================================
    def _export_blank_template(self):
        save_path = filedialog.asksaveasfilename(
            title="Lưu mẫu phiếu trắng 50 câu",
            defaultextension=".png",
            filetypes=[("Ảnh PNG", "*.png")]
        )
        if not save_path:
            return

        blank = generate_50_mcq_template()
        ok = imwrite_utf8(save_path, blank)
        if ok:
            messagebox.showinfo("Thành công", f"Đã xuất mẫu phiếu trắng 50 câu ra:\n{save_path}")
        else:
            messagebox.showerror("Lỗi", "Không thể ghi file ảnh.")

    def _regenerate_samples(self):
        generate_all_samples()
        messagebox.showinfo("Thành công", "Đã tạo mới bộ dữ liệu mẫu 50 câu!")
        self._action_load_sample_dataset()

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current == "Dark" else "Dark")

    def _update_progress_status(self, msg: str):
        self.lbl_progress.configure(text=msg)


if __name__ == "__main__":
    app = OMRGradingApp()
    app.mainloop()
