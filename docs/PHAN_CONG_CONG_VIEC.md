# Phân công dự án FormTHPT50

## Các nhóm chức năng của đề tài

1. **Thiết kế phiếu và quản lý đáp án:** tạo mẫu phiếu 50 câu, nhập đáp án chuẩn và quản lý số lượng câu hỏi.
2. **Thu nhận và xử lý ảnh:** tiếp nhận ảnh từ máy tính hoặc camera, làm sạch ảnh và chuẩn hóa kích thước.
3. **Nhận diện và đọc phiếu:** tìm khung phiếu, căn chỉnh ảnh, đọc đáp án, số báo danh và mã đề.
4. **Chấm điểm và quản lý kết quả:** so sánh đáp án, tính điểm, hiển thị bảng điểm và xuất báo cáo Excel.

## Phân công công việc

| Thành viên | Tỷ lệ | Nhóm chức năng | Công việc lập trình |
|---|---:|---|---|
| **Sáng – nhóm trưởng** | **30%** | **Điều phối quy trình chấm thi** | Xây dựng phần kết nối toàn bộ quy trình từ nhận ảnh đến trả kết quả; lập trình chức năng chụp ảnh bằng camera, chấm điểm, phân loại kết quả, xử lý trạng thái thành công/cảnh báo/lỗi và tích hợp các chức năng của nhóm. |
| **Hoàn** | **24%** | **Giao diện và báo cáo kết quả** | Lập trình giao diện quản lý ảnh, nhập đáp án, theo dõi tiến trình và xem bảng điểm; xây dựng chức năng xuất Excel, hiển thị ảnh kết quả và hoàn thiện cách trình bày thông tin. |
| **Mạnh** | **24%** | **Thiết kế phiếu và quản lý dữ liệu bài thi** | Lập trình tạo mẫu phiếu 50 câu; xây dựng phần quản lý cấu hình số câu, đáp án chuẩn, thông tin thí sinh và dữ liệu bài làm; hỗ trợ các chức năng đọc/ghi dữ liệu của hệ thống. |
| **Nam** | **22%** | **Xử lý ảnh và nhận diện OMR** | Lập trình thu nhận ảnh, chuyển ảnh về dạng phù hợp để xử lý, phát hiện khung phiếu, căn chỉnh và xoay ảnh; nhận diện ô trả lời, số báo danh, mã đề và các trường hợp tô nhiều đáp án. |

## File code phụ trách

- **Sáng:** `core/grading_engine.py`, `core/exam_processor.py`, `gui/app.py` — chụp ảnh bằng camera, chấm điểm và tích hợp quy trình.
- **Hoàn:** `gui/app.py`, `core/excel_exporter.py`, `core/visualizer.py` — giao diện, báo cáo Excel và ảnh kết quả.
- **Mạnh:** `core/sheet_generator.py`, `core/models.py`, `core/layouts.py` — tạo phiếu, cấu trúc dữ liệu và cấu hình bố cục.
- **Nam:** `core/cv_utils.py`, `core/image_alignment.py`, `core/omr_extractor.py` — xử lý ảnh, căn chỉnh và nhận diện OMR.

## Kết quả cần bàn giao

- **Sáng:** quy trình chấm thi được tích hợp thống nhất, kèm chức năng mở camera, xem khung hình và lưu ảnh chụp vào danh sách bài thi.
- **Hoàn:** giao diện hoàn chỉnh, bảng điểm, ảnh kết quả và file Excel.
- **Mạnh:** mẫu phiếu, cấu trúc dữ liệu và chức năng quản lý đáp án hoạt động đúng.
- **Nam:** chức năng xử lý ảnh, căn chỉnh phiếu và đọc thông tin trên phiếu.

## Quy trình phối hợp

1. Mạnh chuẩn bị mẫu phiếu và cấu trúc dữ liệu.
2. Sáng hoàn thiện chức năng chụp ảnh bằng camera và tiếp nhận ảnh vào hệ thống.
3. Nam xử lý ảnh và nhận diện thông tin trên phiếu.
4. Sáng tích hợp phần nhận diện với chức năng chấm điểm.
5. Hoàn kết nối giao diện, bảng điểm và chức năng xuất báo cáo.
