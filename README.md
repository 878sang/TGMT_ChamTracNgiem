# PHẦN MỀM NHẬN DIỆN VÀ CHẤM PHIẾU FORMTHPT50

> **Môn học:** Thị giác máy tính (Computer Vision)  
> **Công nghệ:** Python 3.10+, OpenCV, NumPy, CustomTkinter, OpenPyXL, Pillow.

---

## 1. Giới thiệu
Phần mềm chỉ hỗ trợ mẫu phiếu **FormTHPT50** với số câu chấm tùy chọn từ **1 đến 50**:
1. **Bước 1 - Tải phiếu lên:** Tải một hoặc nhiều ảnh phiếu trả lời (JPG, JPEG, JPE, PNG) của học sinh.
2. **Bước 2 - Đọc phiếu & Chấm điểm:** Nhập số câu (1–50), nạp đáp án tương ứng; OpenCV căn chỉnh FormTHPT50, đọc câu trả lời, SBD và mã đề rồi chấm điểm. Các mẫu cũ không được nhận diện hay chấm.
3. **Bước 3 - Xuất kết quả:** Hiển thị danh sách điểm số, số câu đúng/sai/trống, xem ảnh phiếu đã khoanh màu trực quan và xuất báo cáo Excel 3 Sheet đầy đủ.

---

## 2. Đáp ứng đầy đủ 5 chức năng của đề bài

### Chức năng 1: Quản lý ảnh phiếu trả lời
- Cho phép tải lên một hoặc nhiều ảnh cùng lúc (`.jpg`, `.jpeg`, `.jpe`, `.png`).
- Nút nạp nhanh 7 bài làm mẫu thử nghiệm (`HS001` đến `HS007`).
- Bảng danh sách ảnh hiển thị tên file, độ phân giải ($W \times H$) và trạng thái kiểm tra hợp lệ.
- Cho phép xóa từng ảnh hoặc xóa toàn bộ danh sách.

### Chức năng 2: Tiền xử lý ảnh (OpenCV Pipeline)
- **Đọc ảnh UTF-8 an toàn:** Hỗ trợ đầy đủ đường dẫn tiếng Việt có dấu qua `imread_utf8`.
- **Khử nhiễu & Nhị phân hóa:** Kết hợp Gaussian Blur và Adaptive/Otsu Thresholding.
- **Nhận diện marker và căn chỉnh phối cảnh:** Tìm marker vuông của FormTHPT50, tự xử lý ảnh xoay ngang hoặc ngược và warp về canvas $1653 \times 2337$ px.
- Bố cục được đọc từ `templates/layouts/thpt50.json`, trích trực tiếp từ PDF đính kèm; không dùng tọa độ của mẫu cũ làm dự phòng.

### Chức năng 3: Nhận diện đáp án (OMR 1-50 câu)
- Kiểm tra độ khớp lưới bọt theo layout FormTHPT50 trước khi đọc; ảnh không đúng mẫu bị báo lỗi thay vì chấm bằng tọa độ đoán.
- FormTHPT50 có hai khối 25 hàng × 4 lựa chọn (câu 1–25 bên trái, 26–50 bên phải), khối SBD 6 cột và mã đề 3 cột.
- Đo độ tối tương đối ở tâm từng ô, không tính viền tròn in sẵn là nét tô; cảnh báo các nét tô mờ hoặc không rõ. Nếu quét lại ảnh kết quả đã khoanh màu, lớp màu đỏ/vàng/xanh cũ được loại bỏ trước khi đọc đáp án; nếu lần dò ban đầu chưa tìm thấy lưới, hệ thống sẽ dò lại từ đầu sau khi làm sạch ảnh.
- Chỉ dùng tọa độ cố định khi xác nhận đúng lưới mẫu; nếu không nhận diện được bố cục, đánh dấu cần kiểm tra thay vì chấm theo tọa độ đoán.
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
  - Thang điểm 10.0: mỗi câu đúng được $+10/N$ điểm (N là số câu đã chọn).
  - Phân loại học lực: Xuất sắc ($\ge 9.0$), Giỏi ($\ge 8.0$), Khá ($\ge 6.5$), Trung bình ($\ge 5.0$), Yếu ($< 5.0$).
- Cung cấp tính năng **Tự dò đáp án chuẩn từ ảnh phiếu mẫu giáo viên** hoặc nhập chuỗi đáp án nhanh.
- **Xuất file Excel gồm 3 Sheet chuyên nghiệp:**
  1. `Bang_Diem_Tong_Hop`: Bảng điểm tổng kết, xếp loại, số câu đúng/sai/trống của từng học sinh.
  2. `Chi_Tiet_Bai_Lam`: Ma trận chi tiết N câu trả lời của từng học sinh (Tô xanh câu đúng, tô đỏ câu sai).
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
│   ├── models.py                      # Data model Submission
│   ├── image_alignment.py             # Tiền xử lý, phát hiện marker & nắn phẳng phối cảnh
│   ├── layouts.py                     # Nạp layout OMR FormTHPT50
│   ├── omr_extractor.py               # Bóc tách OMR theo layout FormTHPT50
│   ├── visualizer.py                  # Vẽ overlay kết quả chấm trực quan lên ảnh bài làm
│   ├── grading_engine.py              # Logic chấm điểm thang 10.0 (0.2đ/câu) & xếp loại
│   ├── excel_exporter.py              # Xuất báo cáo kết quả thi ra Excel gồm 3 Sheet
│   ├── sheet_generator.py             # Tạo và sinh phiếu FormTHPT50
│   └── exam_processor.py              # Căn chỉnh, nhận diện, chấm và vẽ kết quả
│
├── gui/                               # Giao diện người dùng
│   └── app.py                         # Ứng dụng Desktop chấm phiếu FormTHPT50
│
├── templates/
│   ├── phieu_50_cau_chuan.png         # Mẫu phiếu thi trắng 50 câu chuẩn
│   ├── layouts/thpt50.json            # Layout pixel lấy từ PDF FormTHPT50
│   └── layouts/thpt50_base.png        # Nền phiếu chuẩn dùng để tạo phiếu trắng
│
├── tests/
│   └── test_omr_50_cau.py             # Unit test cho FormTHPT50
├── tools/
│   ├── build_layout_from_pdf.py       # Trích xuất layout từ PDF nguồn
│   ├── build_concise_report.py        # Tạo báo cáo phiên bản ngắn
│   ├── build_complete_report.py      # Tạo báo cáo đầy đủ, dùng tiện ích từ bản ngắn
│   ├── build_presentation.py          # Tạo bộ slide cơ sở
│   └── redesign_presentation.py       # Sắp lại slide cơ sở thành bản 17 slide
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
   - Bấm `➕ Tải ảnh phiếu...` để chọn một hoặc nhiều ảnh phiếu của học sinh.
2. **Bước 2: Đọc phiếu & Chấm điểm**
   - Chọn `40` hoặc `50` câu, nhập đủ đáp án chuẩn rồi bấm `▶ BẮT ĐẦU CHẤM BÀI`.
   - Phần mềm tự động căn chỉnh ảnh, đọc các câu trả lời theo mẫu đã chọn và chấm điểm.
3. **Bước 3: Xuất kết quả**
   - Xem kết quả trực tiếp trên bảng (Điểm, Số câu đúng/sai/trống).
   - Click đúp vào một học sinh để xem ảnh bài làm đã được vẽ khoanh chấm màu (Xanh = Đúng, Đỏ = Sai/Tô trùng).
   - Bấm `📊 Xuất kết quả (Excel)` để lưu file báo cáo 3 Sheet.

### 4. Chạy kiểm thử tự động (Unit Tests)
```bash
python tests/test_omr_50_cau.py
```
Toàn bộ 12 test case tương ứng với 5 chức năng đều đạt trạng thái `OK (100% Passed)`.
