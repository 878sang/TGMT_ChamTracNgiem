# PHẦN MỀM NHẬN DIỆN VÀ CHẤM PHIẾU TRẢ LỜI TRẮC NGHIỆM THPT (50 CÂU)

> **Môn học:** Thị giác máy tính (Computer Vision)  
> **Công nghệ:** Python 3.10+, OpenCV, NumPy, CustomTkinter, OpenPyXL, Pillow.

---

## 1. Giới thiệu
Phần mềm tập trung chuyên sâu vào bài toán **Chấm phiếu trả lời trắc nghiệm THPT 50 câu** với quy trình thao tác chuẩn xác, trực quan gồm 3 bước:
1. **Bước 1 - Tải phiếu lên:** Tải một hoặc nhiều ảnh phiếu trả lời (JPG, PNG) của học sinh.
2. **Bước 2 - Đọc phiếu & Chấm điểm:** Thuật toán Thị giác máy tính (OpenCV) tự động nắn phẳng phối cảnh, tự động bóc tách các ô trả lời của 50 câu hỏi, SBD, mã đề và chấm điểm so với đáp án chuẩn. **Không cần nút bấm chức năng tự dò phiếu riêng biệt** vì toàn bộ thuật toán tự dò ma trận ô tròn diễn ra tự động ngầm bên trong.
3. **Bước 3 - Xuất kết quả:** Hiển thị danh sách điểm số, số câu đúng/sai/trống, xem ảnh phiếu đã khoanh màu trực quan và xuất báo cáo Excel 3 Sheet đầy đủ.

---

## 2. Đáp ứng đầy đủ 5 chức năng của đề bài

### Chức năng 1: Quản lý ảnh phiếu trả lời
- Cho phép tải lên một hoặc nhiều ảnh cùng lúc (`.jpg`, `.jpeg`, `.png`).
- Nút nạp nhanh 7 bài làm mẫu thử nghiệm (`HS001` đến `HS007`).
- Bảng danh sách ảnh hiển thị tên file, độ phân giải ($W \times H$) và trạng thái kiểm tra hợp lệ.
- Cho phép xóa từng ảnh hoặc xóa toàn bộ danh sách.

### Chức năng 2: Tiền xử lý ảnh (OpenCV Pipeline)
- **Đọc ảnh UTF-8 an toàn:** Hỗ trợ đầy đủ đường dẫn tiếng Việt có dấu qua `imread_utf8`.
- **Khử nhiễu & Nhị phân hóa:** Kết hợp Gaussian Blur và Adaptive/Otsu Thresholding.
- **Phát hiện 4 Marker định vị góc:** Sử dụng Contour Detection và xấp xỉ đa giác (`cv2.approxPolyDP`) để tìm 4 ô vuông đen ở 4 góc phiếu.
- **Căn chỉnh nắn phẳng (Perspective Transform):** Nắn phẳng ảnh bị nghiêng, xoay hoặc chụp lệch góc từ camera điện thoại về kích thước chuẩn hóa $1200 \times 1700$ px.

### Chức năng 3: Nhận diện đáp án (OMR 50 câu)
- Thuật toán tự động dò tìm vị trí 200 ô tròn tương ứng với 50 câu hỏi $\times$ 4 lựa chọn (A, B, C, D).
- Tính mật độ pixel đen (`cv2.countNonZero`) trong circular mask của từng ô tròn.
- Nhận diện chính xác:
  - Đáp án được tô hợp lệ.
  - Câu bỏ trống (`None`).
  - Câu tô nhiều đáp án / tô trùng (`['A', 'B']`).
  - Cảnh báo nghi vấn tẩy lem nhem hoặc tô chì quá mờ.
- Quét Số Báo Danh (6 chữ số) và Mã Đề Thi (3 chữ số).

### Chức năng 4: Xử lý nhiều học sinh theo lô (Batch Processing)
- Xử lý mượt mà hàng chục/hàng trăm ảnh cùng lúc trên luồng nền (`threading.Thread`) không làm đơ giao diện.
- Tự động trích xuất mã học sinh từ tên file ảnh (ví dụ: `HS001.jpg` $\rightarrow$ `HS001`).
- Thanh tiến trình trực quan (`ProgressBar`) hiển thị tỷ lệ % hoàn thành.
- **Cơ chế chống dừng đột ngột (Fault Tolerance):** Khi gặp 1 ảnh bị lỗi (khuyết góc, mất nét), hệ thống ghi nhận lỗi vào cột trạng thái và tự động tiếp tục xử lý các phiếu còn lại.
- Bảng thống kê chi tiết: Tổng số, Thành công, Cảnh báo/Cần kiểm tra, Thất bại.

### Chức năng 5: Chấm điểm tự động & Xuất Excel 3 Sheet
- Tự động so sánh đáp án nhận diện với đáp án chuẩn:
  - Thang điểm 10.0: Mỗi câu đúng được $+0.2$ điểm.
  - Phân loại học lực: Xuất sắc ($\ge 9.0$), Giỏi ($\ge 8.0$), Khá ($\ge 6.5$), Trung bình ($\ge 5.0$), Yếu ($< 5.0$).
- Cung cấp tính năng **Tự dò đáp án chuẩn từ ảnh phiếu mẫu giáo viên** hoặc nhập chuỗi đáp án nhanh.
- **Xuất file Excel gồm 3 Sheet chuyên nghiệp:**
  1. `Bang_Diem_Tong_Hop`: Bảng điểm tổng kết, xếp loại, số câu đúng/sai/trống của từng học sinh.
  2. `Chi_Tiet_Bai_Lam`: Ma trận chi tiết 50 câu trả lời của từng học sinh (Tô xanh câu đúng, tô đỏ câu sai).
  3. `Thong_Ke_Pho_Diem`: Điểm trung bình, cao nhất, thấp nhất, phổ điểm và tỷ lệ học sinh làm đúng từng câu.

### Giao diện người dùng trực quan & Visualizer
- Giao diện CustomTkinter hiện đại, dễ thao tác.
- Xem chi tiết từng bài thi với lớp phủ trực quan OpenCV:
  - Vòng tròn **XANH LÁ**: Câu làm đúng.
  - Vòng tròn **ĐỎ** kèm dấu gạch chéo: Câu làm sai hoặc tô trùng.
  - Vòng tròn **VÀNG**: Đáp án chuẩn của đề thi để đối chiếu.
  - Banner điểm số nổi bật ở đầu trang phiếu.

---

## 3. Cấu trúc thư mục

```text
Do An/
│
├── core/                              # Các thuật toán xử lý cốt lõi (OpenCV & Backend)
│   ├── cv_utils.py                    # Đọc/ghi ảnh UTF-8 an toàn trên Windows
│   ├── models.py                      # Data models (Submission, Exam)
│   ├── image_alignment.py             # Tiền xử lý, phát hiện marker & nắn phẳng phối cảnh
│   ├── omr_extractor.py               # Thuật toán tự dò ma trận 50 câu & bóc tách OMR
│   ├── visualizer.py                  # Vẽ overlay kết quả chấm trực quan lên ảnh bài làm
│   ├── grading_engine.py              # Logic chấm điểm thang 10.0 (0.2đ/câu) & xếp loại
│   ├── excel_exporter.py              # Xuất báo cáo kết quả thi ra Excel gồm 3 Sheet
│   ├── sheet_generator.py             # Sinh phiếu trắng, phiếu đáp án mẫu GV & tập ảnh mẫu
│   └── exam_processor.py              # Pipeline xử lý trọn gói & tự dò đáp án từ ảnh GV
│
├── gui/                               # Giao diện người dùng
│   └── app.py                         # Ứng dụng Desktop CustomTkinter chuyên biệt cho phiếu 50 câu
│
├── dataset/
│   └── sample_submissions_50cau/      # 7 bài làm mẫu (10đ, 8đ, bỏ trống, tô trùng, chụp nghiêng...)
│
├── templates/
│   ├── phieu_50_cau_chuan.png         # Mẫu phiếu thi trắng 50 câu chuẩn
│   └── phieu_dap_an_mau_giao_vien.png # Phiếu đáp án chuẩn của giáo viên
│
├── tests/
│   └── test_omr_50_cau.py             # 12 bài unit test bao quát đầy đủ cả 5 chức năng
│
├── main.py                            # Điểm khởi chạy chương trình
└── requirements.txt                   # Thư viện yêu cầu
```

---

## 4. Hướng dẫn sử dụng chuẩn 3 bước

### Khởi chạy phần mềm
```bash
python main.py
```

### Quy trình 3 bước:
1. **Bước 1: Tải phiếu lên**
   - Bấm `➕ Tải ảnh phiếu...` để chọn 1 hoặc nhiều ảnh phiếu của học sinh (hoặc bấm `⚡ Nạp 7 bài mẫu` để thử nghiệm nhanh).
2. **Bước 2: Đọc phiếu & Chấm điểm**
   - Bấm `▶ ĐỌC PHIẾU & CHẤM ĐIỂM`.
   - Phần mềm tự động xử lý toàn bộ: nắn phẳng ảnh, tự dò tìm 50 câu hỏi, đọc câu trả lời và chấm điểm so với đáp án chuẩn.
3. **Bước 3: Xuất kết quả**
   - Xem kết quả trực tiếp trên bảng (Điểm, Số câu đúng/sai/trống).
   - Click đúp vào một học sinh để xem ảnh bài làm đã được vẽ khoanh chấm màu (Xanh = Đúng, Đỏ = Sai/Tô trùng).
   - Bấm `📊 Xuất kết quả (Excel)` để lưu file báo cáo 3 Sheet.

### 4. Chạy kiểm thử tự động (Unit Tests)
```bash
python tests/test_omr_50_cau.py
```
Toàn bộ 12 test case tương ứng với 5 chức năng đều đạt trạng thái `OK (100% Passed)`.
