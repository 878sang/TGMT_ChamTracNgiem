# HỆ THỐNG QUÉT VÀ CHẤM BÀI TRẮC NGHIỆM ĐA NĂNG BẰNG PYTHON & THỊ GIÁC MÁY TÍNH (OMR)

> **Đồ án môn học:** Thị giác máy tính (Computer Vision)  
> **Ngôn ngữ & Thư viện:** Python 3.10+, OpenCV, NumPy, CustomTkinter, OpenPyXL, Pillow, Pytest.

---

## 🌟 Điểm nổi bật của Hệ thống

1. **Hỗ trợ 2 Chế độ thi linh hoạt (Dual-Mode):**
   * **Chế độ 1 - Trắc nghiệm 4 lựa chọn (Full MCQ):** Phục vụ kiểm tra 15 phút, 1 tiết, thi học kỳ (hỗ trợ linh hoạt **20 câu** hoặc **40 câu** trên mẫu phiếu in chuẩn, 4 lựa chọn A-B-C-D, tính điểm đều theo thang 10.0).
   * **Chế độ 2 - Chuẩn Tốt nghiệp THPT mới (từ 2025 của Bộ GD&ĐT):**
     * **Phần I:** 12 câu trắc nghiệm 4 lựa chọn A-B-C-D (mỗi câu 0.25đ, tối đa 3.0 điểm).
     * **Phần II:** 4 câu Đúng / Sai x 4 ý a,b,c,d (chấm lũy tiến: đúng 1 ý = 0.1đ | 2 ý = 0.25đ | 3 ý = 0.5đ | 4 ý = 1.0đ, tối đa 4.0 điểm).
     * **Phần III:** 6 câu Trả lời ngắn dạng bảng tô số 4 cột gồm dấu `-`, `,` và các số 0-9 (mỗi câu 0.5đ, tối đa 3.0 điểm).

2. **Thị giác máy tính & OMR độ chính xác cao:**
   * **Thuật toán kiểm soát 4 Marker định vị góc:** Chỉ tiến hành nắn phẳng phối cảnh (Perspective Transform) khi xác định đủ đúng 4 marker hình học hợp lệ ở 4 góc; nếu ảnh bị che khuất hoặc thiếu góc, hệ thống lập tức báo lỗi ảnh rõ ràng thay vì nắn lệch tọa độ.
   * **Chống méo, chụp nghiêng, bóng đổ, thiếu sáng và mờ:** Tự động thích ứng với ảnh chụp thực tế bằng điện thoại qua bộ tiền xử lý đa ngưỡng Gaussian & Otsu Threshold.
   * **Nhận diện SBD (6 số) & Mã đề thi (3 số) chuẩn xác:** Tuyệt đối không tự ý gán số mặc định ('000000' hay '100') khi không đọc được. Nếu học sinh bỏ trống hoặc tẩy chì chưa sạch, hệ thống đánh dấu cờ cảnh báo `?` và yêu cầu giáo viên xác nhận.
   * **Xử lý mã đề thông minh:** Nếu mã đề không tồn tại trong bộ đáp án, bài làm được đưa vào trạng thái **"Cần kiểm tra"**, điểm số giữ 0.0, tuyệt đối không tự ý lấy đáp án của mã đề đầu tiên.
   * **Bóc tách câu trả lời ngắn Phần III chuẩn quy chế:** Giữ đúng vị trí từng cột số, tự động phát hiện lỗi tô trùng ô trong 1 cột và lỗi bỏ trống cột ở giữa các chữ số.

3. **Giao diện Desktop hiện đại, Thread-Safe & Hỗ trợ Sửa bài:**
   * Xây dựng trên **CustomTkinter** với Dark/Light mode hiện đại.
   * **Luồng chấm nền an toàn (Thread-Safe):** Toàn bộ tiến trình quét, bảng kết quả và thông báo hoàn tất được đồng bộ về luồng chính của Tkinter thông qua cơ chế callback (`after`), đảm bảo giao diện luôn mượt mà, không bị treo đơ.
   * Màn hình **Review & Sửa lỗi:** Xem ảnh bài làm trực quan với các vòng tròn khoanh màu Xanh lá (đúng), Đỏ (sai), Vàng (đáp án đúng). Cho phép giáo viên sửa nhanh đáp án, mã đề, họ tên và bấm **"Lưu & Chấm lại"**. Khi chấm lại, hệ thống sử dụng ảnh đã căn chỉnh để các vòng tròn khoanh không bao giờ bị lệch vị trí.

4. **Báo cáo Excel chuyên nghiệp 3 Sheet hoàn chỉnh:**
   * **Sheet 1 (Bang_Diem_Tong_Hop):** SBD, Họ tên (tự động map từ Excel hoặc OCR), Mã đề, Điểm từng phần, Điểm tổng, Xếp loại và Trạng thái bài thi. Các bài lỗi được phân loại riêng, không tính điểm ảo vào lớp.
   * **Sheet 2 (Chi_Tiet_Bai_Lam):** Ma trận chi tiết lựa chọn của từng thí sinh ở từng câu hỏi.
   * **Sheet 3 (Thong_Ke_Pho_Diem):**
     * **I. Chỉ số KPI:** Điểm trung bình, Điểm cao nhất, Điểm thấp nhất, tỷ lệ Giỏi/Khá/TB/Chưa đạt (được tính toán chọn lọc trên các bài thi hợp lệ, không bị kéo tụt bởi bài thi lỗi).
     * **II. Bảng phổ điểm chi tiết:** Phân bố học sinh theo 10 khoảng điểm từ [0.0 - 1.0) đến [9.0 - 10.0].
     * **III. Ma trận tỷ lệ đúng / sai theo từng câu hỏi:** Thống kê chi tiết tỷ lệ Đúng, Sai, Bỏ trống của từng câu hỏi và từng phần thi (Phần I, II, III).

---

## 📂 Cấu trúc thư mục Dự án

```text
TGMT_ChamTracNgiem/
│
├── core/                              # Các module xử lý lõi (Core algorithms)
│   ├── cv_utils.py                    # Tiện ích đọc/ghi ảnh tiếng Việt UTF-8 trên Windows
│   ├── models.py                      # Data models (Exam, Submission, ExamMode)
│   ├── sheet_generator.py             # Sinh mẫu phiếu PDF/PNG và bộ ảnh test đa dạng
│   ├── image_alignment.py             # Căn chỉnh phối cảnh 4 marker góc & tách ROI
│   ├── omr_extractor.py               # Nhận diện OMR SBD, Mã đề, Full MCQ, THPT 3 phần
│   ├── visualizer.py                  # Vẽ khoanh màu chấm điểm và banner kết quả lên ảnh
│   ├── grading_engine.py              # Logic chấm điểm chuẩn Bộ GD&ĐT (Full MCQ & THPT 2025)
│   ├── excel_answer_handler.py        # Import/Export file đáp án Excel/TXT
│   ├── excel_exporter.py              # Xuất báo cáo kết quả thi 3 Sheet hoàn chỉnh
│   ├── student_roster_handler.py      # Import danh sách học sinh và tra cứu SBD
│   ├── ocr_engine.py                  # Nhận diện OCR chữ in/viết tay khung tiêu đề
│   ├── storage_manager.py             # Quản lý lưu trữ JSON độc lập đường dẫn
│   └── exam_processor.py              # Cầu nối tích hợp toàn bộ pipeline chấm thi
│
├── gui/                               # Giao diện người dùng Desktop (CustomTkinter)
│   └── app.py                         # Ứng dụng Desktop GUI hoàn chỉnh, Thread-Safe
│
├── templates/                         # File mẫu in ấn & file Excel mẫu
│   ├── phieu_full_40_cau.png          # Mẫu phiếu Full trắc nghiệm 40 câu
│   ├── phieu_thpt_2025.png            # Mẫu phiếu thi chuẩn THPT 2025
│   ├── mau_dap_an.xlsx                # Mẫu Excel đáp án Full trắc nghiệm
│   ├── mau_dap_an_thpt_2025.xlsx      # Mẫu Excel đáp án chuẩn THPT 3 phần
│   └── mau_danh_sach_hoc_sinh.xlsx    # Mẫu danh sách học sinh lớp
│
├── dataset/                           # Dữ liệu thử nghiệm phong phú
│   └── sample_submissions/            # Ảnh bài làm phẳng, chụp nghiêng, thiếu sáng, bóng đổ, mờ, lỗi thực tế
│
├── tests/                             # Bộ kiểm thử tự động (Pytest)
│   ├── test_grading.py                # Test logic chấm điểm, điểm biên, xử lý mã đề sai, xuất Excel
│   └── test_omr_and_alignment.py      # Test kiểm tra 4 marker, OMR SBD/Mã đề, phát hiện gap Phần III
│
├── data/                              # Dữ liệu lưu trữ bài thi và kết quả chấm
│   ├── exams.json                     # Cấu hình bài kiểm tra đã tạo
│   └── annotated/                     # Ảnh bài thi sau khi chấm (đã vẽ overlay)
│
├── main.py                            # Điểm khởi chạy chính của phần mềm
├── requirements.txt                   # Danh sách thư viện Python cần thiết
├── ytuong.txt                         # Bản thuyết minh đề tài
└── phan_cong_nhiem_vu.txt             # Báo cáo phân công nhiệm vụ chi tiết 4 thành viên
```

---

## 🚀 Hướng dẫn Cài đặt & Chạy Phần mềm

### 1. Cài đặt các thư viện cần thiết
Mở Terminal hoặc Command Prompt tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

### 2. Chạy kiểm thử tự động (Unit Tests)
Kiểm tra tính toàn vẹn của toàn bộ thuật toán chấm điểm và OMR:
```bash
python -m pytest tests/
```

### 3. Khởi chạy ứng dụng Desktop
Chạy lệnh:
```bash
python main.py
```

---

## 📖 Hướng dẫn sử dụng chi tiết

### Bước 1: Chọn hoặc Tạo bài kiểm tra
* Chọn một bài kiểm tra có sẵn trong danh sách (hệ thống có sẵn bài mẫu **Full Trắc Nghiệm** và **Chuẩn THPT 2025**).
* Hoặc bấm **"➕ Tạo bài thi mới"**:
  * Nhập Tên bài thi, Môn, Lớp.
  * Chọn **Chế độ 1 (Trắc nghiệm 4 lựa chọn)** (chọn 20 hoặc 40 câu) hoặc **Chế độ 2 (Chuẩn THPT 2025)**.
  * Nhập chuỗi đáp án nhanh hoặc bấm **"📥 Import từ Excel"**.
  * (Tùy chọn) Bấm **"📥 Nạp Danh sách học sinh"** để phần mềm tự động gán tên học sinh theo SBD.

### Bước 2: Quét & Chấm bài thi
* Chuyển sang màn hình **"📸 Quét & Chấm bài"**.
* Bấm **"🖼️ Chọn ảnh bài làm"** hoặc **"📁 Chọn thư mục ảnh"** (có thể chọn thư mục `dataset/sample_submissions` có sẵn).
* Bấm **"🚀 BẮT ĐẦU CHẤM TẤT CẢ"**. Hệ thống sẽ tự động:
  * Nắn thẳng từng ảnh chụp qua 4 marker định vị góc.
  * Nhận diện SBD, Mã đề và đáp án.
  * Đối chiếu đáp án, tính điểm từng phần và vẽ kết quả lên ảnh.

### Bước 3: Xem chi tiết & Sửa bài nghi vấn
* Trên bảng kết quả, bấm nút **"🔍 Xem & Sửa"** ở bất kỳ bài làm nào.
* Quan sát ảnh bài làm đã được vẽ khoanh **Xanh lá** (đúng), **Đỏ** (sai), **Vàng** (đáp án đúng của đề).
* Nếu có câu bị cờ cảnh báo *"Cần kiểm tra"* (học sinh tẩy chì chưa sạch hoặc mã đề sai), giáo viên có thể sửa lại và bấm **"💾 LƯU & CHẤM LẠI BÀI NÀY"**. Ảnh overlay sẽ được vẽ lại chính xác trên tọa độ ảnh đã căn chỉnh.

### Bước 4: Thống kê & Xuất Excel
* Bấm sang màn hình **"📊 Thống kê & Xuất Excel"**.
* Xem các chỉ số KPI: Điểm trung bình, Điểm cao nhất, Điểm thấp nhất, Tỷ lệ giỏi/khá/trung bình/chưa đạt (đã tự động loại trừ bài lỗi).
* Bấm **"📊 XUẤT BÁO CÁO EXCEL 3 SHEET HOÀN CHỈNH"** để lưu file Excel báo cáo về máy.

---

## ⚠️ Giới hạn hiện tại & Lưu ý sử dụng
* **Mẫu phiếu:** Sử dụng 2 mẫu phiếu chuẩn A4 trong thư mục `templates/` (có 4 ô vuông đen to ở 4 góc để định vị).
* **Chất lượng ảnh:** Khi chụp ảnh bằng điện thoại, đảm bảo nhìn thấy rõ toàn bộ 4 marker ở 4 góc tờ giấy. Không để ngón tay che khuất các marker góc.
* **Bút chì:** Khuyến khích học sinh dùng bút chì 2B hoặc đậm hơn để tô ô tròn kín và rõ ràng.
