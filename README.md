# HỆ THỐNG QUÉT VÀ CHẤM BÀI TRẮC NGHIỆM ĐA NĂNG BẰNG PYTHON & THỊ GIÁC MÁY TÍNH (OMR)

> **Đồ án môn học:** Thị giác máy tính (Computer Vision)  
> **Ngôn ngữ & Thư viện:** Python 3.10+, OpenCV, NumPy, CustomTkinter, OpenPyXL, Pillow.

---

## 🌟 Điểm nổi bật của Hệ thống

1. **Hỗ trợ 2 Chế độ thi linh hoạt (Dual-Mode):**
   * **Chế độ 1 - Full Trắc nghiệm:** Phục vụ kiểm tra 15 phút, 1 tiết, học kỳ (40 câu, 4 lựa chọn A-B-C-D, tính điểm đều theo thang 10).
   * **Chế độ 2 - Chuẩn Tốt nghiệp THPT mới (từ 2025 của Bộ GD&ĐT):**
     * **Phần I:** 12 câu trắc nghiệm 4 lựa chọn (3.0 điểm).
     * **Phần II:** 4 câu Đúng / Sai (4.0 điểm, tính điểm lũy tiến: 0.1đ - 0.25đ - 0.5đ - 1.0đ).
     * **Phần III:** 6 câu Trả lời ngắn dạng bảng tô số gồm dấu `-`, `,` và các số 0-9 (3.0 điểm).
2. **Thị giác máy tính độ chính xác cao:**
   * Tự động phát hiện **4 Marker định vị ở 4 góc** để nắn phẳng ảnh bằng biến đổi phối cảnh (Perspective Transform).
   * Chống méo, xoay nghiêng góc $15^\circ - 30^\circ$, chống bóng đổ tay/điện thoại.
   * Tự động bóc tách **Số báo danh (6 số)** và **Mã đề thi (3 số)**.
   * Thuật toán so sánh tương đối (Relative Scoring) chống lỗi khi học sinh tẩy chì chưa sạch hoặc tô mờ.
3. **Giao diện Desktop hiện đại (CustomTkinter):**
   * Hỗ trợ Dark/Light mode sang trọng.
   * Chấm bài hàng loạt có thanh tiến trình (ProgressBar) theo thời gian thực.
   * Màn hình **Review & Sửa lỗi:** Xem ảnh bài làm đã được vẽ khoanh tròn Xanh lá (đúng), Đỏ (sai), Vàng (đáp án đúng) và cho phép sửa tay câu nghi vấn.
4. **Báo cáo Excel chuyên nghiệp 3 Sheet:**
   * **Sheet 1:** Bảng điểm tổng hợp (SBD, Họ tên, Mã đề, Điểm từng phần, Tổng điểm, Xếp loại).
   * **Sheet 2:** Bảng chi tiết từng câu của từng học sinh.
   * **Sheet 3:** Thống kê phổ điểm, tỷ lệ đúng/sai theo từng câu hỏi.

---

## 📂 Cấu trúc thư mục Dự án

```text
Đồ Án/
│
├── core/                              # Các module xử lý lõi
│   ├── cv_utils.py                    # Tiện ích đọc/ghi ảnh tiếng Việt trên Windows
│   ├── models.py                      # Data models (Exam, Submission, ExamMode)
│   ├── sheet_generator.py             # Sinh mẫu phiếu và ảnh test thực tế
│   ├── image_alignment.py             # Căn chỉnh phối cảnh & tách ROI (TV1)
│   ├── omr_extractor.py               # Nhận diện OMR cả 2 chế độ thi (TV2)
│   ├── visualizer.py                  # Vẽ khoanh màu chấm điểm lên ảnh (TV2)
│   ├── grading_engine.py              # Logic chấm điểm chuẩn BGD&ĐT (TV3)
│   ├── excel_answer_handler.py        # Import/Export file đáp án Excel/TXT (TV3)
│   ├── excel_exporter.py              # Xuất báo cáo kết quả thi 3 Sheet (TV3)
│   ├── storage_manager.py             # Quản lý lưu trữ JSON (TV3)
│   └── exam_processor.py              # Cầu nối tích hợp toàn bộ pipeline
│
├── gui/                               # Giao diện người dùng Desktop (TV4)
│   └── app.py                         # Ứng dụng CustomTkinter hoàn chỉnh
│
├── templates/                         # File mẫu in ấn & file Excel mẫu
│   ├── phieu_full_40_cau.png          # Mẫu phiếu Full trắc nghiệm 40 câu
│   ├── phieu_thpt_2025.png            # Mẫu phiếu thi chuẩn THPT 2025
│   ├── mau_dap_an.xlsx                # Mẫu Excel đáp án Full trắc nghiệm
│   └── mau_dap_an_thpt_2025.xlsx      # Mẫu Excel đáp án chuẩn THPT 3 phần
│
├── dataset/                           # Dữ liệu thử nghiệm
│   └── sample_submissions/            # Ảnh bài làm mẫu (ảnh phẳng & ảnh chụp nghiêng)
│
├── data/                              # Dữ liệu lưu trữ của hệ thống
│   ├── exams.json                     # Danh sách các bài kiểm tra đã tạo
│   └── annotated/                     # Ảnh bài làm sau khi chấm (đã vẽ overlay)
│
├── main.py                            # File khởi chạy chính của phần mềm
├── requirements.txt                   # Danh sách thư viện cần thiết
├── ytuong.txt                         # Bản thuyết minh ý tưởng đề tài
└── phan_cong_nhiem_vu.txt             # Bảng phân công chi tiết cho 4 thành viên
```

---

## 🚀 Hướng dẫn Cài đặt & Chạy Phần mềm

### 1. Cài đặt các thư viện cần thiết
Mở Terminal hoặc Command Prompt tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng
Chạy lệnh:
```bash
python main.py
```

---

## 📖 Hướng dẫn sử dụng chi tiết

### Bước 1: Chọn hoặc Tạo bài kiểm tra
* Chọn một bài kiểm tra có sẵn trong danh sách (hệ thống đã tạo sẵn 2 bài mẫu: 1 bài **Full Trắc Nghiệm** và 1 bài **Chuẩn THPT 2025**).
* Hoặc bấm **"+ Tạo bài thi mới"**:
  * Nhập Tên bài thi, Môn, Lớp.
  * Chọn **Chế độ 1 (Full trắc nghiệm)** hoặc **Chế độ 2 (Chuẩn THPT)**.
  * Nhập đáp án nhanh hoặc bấm **"📥 Import từ Excel"** để nạp file đáp án.

### Bước 2: Quét & Chấm bài thi
* Chuyển sang màn hình **"📸 Quét & Chấm bài"**.
* Bấm **"🖼️ Chọn ảnh bài làm"** hoặc **"📁 Chọn cả thư mục"** (có thể chọn ngay thư mục `dataset/sample_submissions` có sẵn).
* Bấm **"🚀 BẮT ĐẦU CHẤM TẤT CẢ"**. Hệ thống sẽ tự động:
  * Nắn thẳng từng ảnh chụp.
  * Nhận diện SBD, Mã đề và đáp án.
  * Tính điểm và vẽ kết quả lên ảnh.

### Bước 3: Xem chi tiết & Sửa bài nghi vấn
* Trên bảng kết quả, bấm nút **"Xem chi tiết"** ở bất kỳ học sinh nào.
* Xem ảnh bài làm đã được vẽ khoanh **Xanh lá** (đúng), **Đỏ** (sai), **Vàng** (đáp án đúng).
* Kiểm tra các câu bị cờ cảnh báo *"Cần kiểm tra"*.

### Bước 4: Thống kê & Xuất Excel
* Bấm sang màn hình **"📊 Thống kê & Xuất Excel"**.
* Xem các chỉ số KPI: Điểm trung bình, Điểm cao nhất, Điểm thấp nhất, Tỷ lệ giỏi/khá/trung bình/chưa đạt.
* Bấm **"📊 XUẤT BÁO CÁO EXCEL 3 SHEET HOÀN CHỈNH"** để tải file Excel báo cáo về máy.
