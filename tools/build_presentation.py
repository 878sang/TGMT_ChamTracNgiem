"""
build_presentation.py
Script to generate the complete, high-end, professional PowerPoint presentation (16:9)
Topic: XÂY DỰNG PHẦN MỀM NHẬN DIỆN VÀ CHẤM PHIẾU TRẢ LỜI TRẮC NGHIỆM THPT BẰNG PYTHON VÀ OPENCV
Design Style: Modern Technology + Premium Minimalist (Keynote / International Conference Style)
Palette: Dark Navy (#0B1220), Electric Cyan (#00D4FF), Pure White (#FFFFFF), Slate Gray (#94A3B8)
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- COLOR DEFINITIONS ---
C_BG = RGBColor(11, 18, 32)        # #0B1220 Deep Dark Navy
C_CARD = RGBColor(16, 26, 46)      # #101A2E Dark Slate Blue Card
C_CARD_ALT = RGBColor(20, 34, 60)  # #14223C Elevated Card
C_BORDER = RGBColor(30, 48, 77)    # #1E304D Subtle Card Border
C_CYAN = RGBColor(0, 212, 255)     # #00D4FF Electric Cyan Accent
C_CYAN_BG = RGBColor(15, 34, 64)   # #0F2240 Pill Tag Background
C_WHITE = RGBColor(255, 255, 255)  # #FFFFFF Pure White
C_MUTED = RGBColor(148, 163, 184)  # #94A3B8 Slate 400 Light Gray
C_LIGHT = RGBColor(226, 232, 240)  # #E2E8F0 Slate 200 Crisp Body
C_GREEN = RGBColor(16, 185, 129)   # #10B981 Success
C_AMBER = RGBColor(245, 158, 11)   # #F59E0B Warning / Notice
C_RED = RGBColor(239, 68, 68)      # #EF4444 Alert / Problem

FONT_TITLE = "Segoe UI"
FONT_BODY = "Segoe UI"

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text, subtitle_text, slide_num_str):
        # Category Tag Pill
        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(3.2), Inches(0.32))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = C_CYAN_BG
        tag_box.line.color.rgb = C_CYAN
        tag_box.line.width = Pt(0.75)
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = False
        tf_tag.margin_left = Inches(0.1)
        tf_tag.margin_right = Inches(0.1)
        tf_tag.margin_top = Inches(0.04)
        tf_tag.margin_bottom = Inches(0.04)
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text
        p_tag.font.name = FONT_TITLE
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = C_CYAN

        # Header Title
        title_box = slide.shapes.add_textbox(Inches(0.78), Inches(0.75), Inches(10.5), Inches(0.55))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = Inches(0)
        tf_title.margin_top = Inches(0)
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = FONT_TITLE
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_WHITE

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.78), Inches(1.30), Inches(10.5), Inches(0.35))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = Inches(0)
        tf_sub.margin_top = Inches(0)
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = C_MUTED

        # Slide Number Badge (Top Right)
        num_box = slide.shapes.add_textbox(Inches(11.5), Inches(0.4), Inches(1.0), Inches(0.3))
        tf_num = num_box.text_frame
        tf_num.word_wrap = False
        p_num = tf_num.paragraphs[0]
        p_num.alignment = PP_ALIGN.RIGHT
        p_num.text = slide_num_str
        p_num.font.name = FONT_TITLE
        p_num.font.size = Pt(12)
        p_num.font.bold = True
        p_num.font.color.rgb = C_CYAN

        # Divider line
        div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.68), Inches(11.733), Inches(0.015))
        div.fill.solid()
        div.fill.fore_color.rgb = C_BORDER
        div.line.fill.background()

    def add_footer(slide):
        # Footer text left
        foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(8.0), Inches(0.3))
        tf_foot = foot_box.text_frame
        p_foot = tf_foot.paragraphs[0]
        p_foot.text = "Trường Đại học Vinh • Viện Kỹ thuật & Công nghệ • Đồ án Thị giác Máy tính 2026"
        p_foot.font.name = FONT_BODY
        p_foot.font.size = Pt(9)
        p_foot.font.color.rgb = C_MUTED

    # -------------------------------------------------------------------------
    # SLIDE 1: TRANG BÌA (COVER SLIDE)
    # -------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Decorative tech lines / accents
    line1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.1), Inches(0.05), Inches(2.2))
    line1.fill.solid()
    line1.fill.fore_color.rgb = C_CYAN
    line1.line.fill.background()

    # Top Tag
    tag_box1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(1.1), Inches(5.8), Inches(0.38))
    tag_box1.fill.solid()
    tag_box1.fill.fore_color.rgb = C_CYAN_BG
    tag_box1.line.color.rgb = C_CYAN
    tag_box1.line.width = Pt(1)
    tf1 = tag_box1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "BÁO CÁO ĐỒ ÁN HỌC PHẦN THỊ GIÁC MÁY TÍNH (COMPUTER VISION)"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = C_CYAN

    # Main Title
    t_box1 = s1.shapes.add_textbox(Inches(1.05), Inches(1.6), Inches(11.2), Inches(1.3))
    tf_t1 = t_box1.text_frame
    tf_t1.word_wrap = True
    p_t1 = tf_t1.paragraphs[0]
    p_t1.text = "XÂY DỰNG PHẦN MỀM NHẬN DIỆN VÀ CHẤM\nPHIẾU TRẢ LỜI TRẮC NGHIỆM THPT"
    p_t1.font.name = FONT_TITLE
    p_t1.font.size = Pt(28)
    p_t1.font.bold = True
    p_t1.font.color.rgb = C_WHITE

    # Subtitle
    sub_box1 = s1.shapes.add_textbox(Inches(1.05), Inches(2.95), Inches(11.2), Inches(0.5))
    tf_s1 = sub_box1.text_frame
    p_s1 = tf_s1.paragraphs[0]
    p_s1.text = "Ứng dụng Python, OpenCV và Thuật toán Tương quan Độ tương phản Tương đối (Relative Ink Contrast)"
    p_s1.font.name = FONT_TITLE
    p_s1.font.size = Pt(14)
    p_s1.font.color.rgb = C_CYAN

    # Tech Stack Badges
    badges = ["Python 3.10+", "OpenCV 4.x", "CustomTkinter GUI", "Relative Ink Contrast", "OpenPyXL 3-Sheet", "FormTHPT50"]
    bx = 1.1
    badge_y = 3.55
    for b in badges:
        bw = len(b) * 0.12 + 0.5
        if bx + bw > 12.2:
            bx = 1.1
            badge_y += 0.38
        b_shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(bx), Inches(badge_y), Inches(bw), Inches(0.32))
        b_shape.fill.solid()
        b_shape.fill.fore_color.rgb = C_CARD
        b_shape.line.color.rgb = C_BORDER
        b_shape.line.width = Pt(0.75)
        btf = b_shape.text_frame
        bp = btf.paragraphs[0]
        bp.text = b
        bp.font.name = FONT_TITLE
        bp.font.size = Pt(10)
        bp.font.color.rgb = C_LIGHT
        bx += bw + 0.15

    # Institution Card (Bottom Left)
    c_inst = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(4.35), Inches(5.3), Inches(2.35))
    c_inst.fill.solid()
    c_inst.fill.fore_color.rgb = C_CARD
    c_inst.line.color.rgb = C_BORDER
    c_inst.line.width = Pt(1)
    tf_inst = c_inst.text_frame
    tf_inst.margin_left = Inches(0.3)
    tf_inst.margin_top = Inches(0.25)
    
    p = tf_inst.paragraphs[0]
    p.text = "CƠ QUAN & ĐƠN VỊ ĐÀO TẠO"
    p.font.name = FONT_TITLE
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    
    lines_inst = [
        ("TRƯỜNG ĐẠI HỌC VINH", True, C_WHITE, Pt(13)),
        ("VIỆN KỸ THUẬT VÀ CÔNG NGHỆ", True, C_LIGHT, Pt(11)),
        ("Bộ môn: Khoa học Máy tính & Trí tuệ Nhân tạo", False, C_MUTED, Pt(10)),
        ("Học phần: Thị giác Máy tính (Computer Vision)", False, C_MUTED, Pt(10)),
        ("Thời gian thực hiện: Học kỳ II - Năm 2026", False, C_MUTED, Pt(10)),
    ]
    for text, bold, col, size in lines_inst:
        p = tf_inst.add_paragraph()
        p.text = text
        p.font.name = FONT_BODY
        p.font.size = size
        p.font.bold = bold
        p.font.color.rgb = col
        p.space_before = Pt(4)

    # Authors Card (Bottom Right)
    c_auth = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.7), Inches(4.35), Inches(5.5), Inches(2.35))
    c_auth.fill.solid()
    c_auth.fill.fore_color.rgb = C_CARD
    c_auth.line.color.rgb = C_CYAN
    c_auth.line.width = Pt(1)
    tf_auth = c_auth.text_frame
    tf_auth.margin_left = Inches(0.3)
    tf_auth.margin_top = Inches(0.25)
    
    p = tf_auth.paragraphs[0]
    p.text = "GIẢNG VIÊN HƯỚNG DẪN & NHÓM TÁC GIẢ"
    p.font.name = FONT_TITLE
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    
    lines_auth = [
        ("GVHD: ThS. Nguyễn Thị Minh Tâm", True, C_WHITE, Pt(12)),
        ("Nhóm sinh viên thực hiện:", True, C_CYAN, Pt(11)),
        ("• Hồ Tuấn Hiệp (MSSV: 225752021610014) — Trưởng nhóm", False, C_LIGHT, Pt(10.5)),
        ("• Nguyễn Khắc Quốc Khánh (MSSV: 225752021610018)", False, C_LIGHT, Pt(10.5)),
        ("• Lê Viết Quân (MSSV: 225752021610078)", False, C_LIGHT, Pt(10.5)),
        ("• Nguyễn Văn Thành (MSSV: 225752021610080)", False, C_LIGHT, Pt(10.5)),
    ]
    for text, bold, col, size in lines_auth:
        p = tf_auth.add_paragraph()
        p.text = text
        p.font.name = FONT_BODY
        p.font.size = size
        p.font.bold = bold
        p.font.color.rgb = col
        p.space_before = Pt(3)

    # -------------------------------------------------------------------------
    # SLIDE 2: 01. BỐI CẢNH & TÍNH CẤP THIẾT
    # -------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "01. BỐI CẢNH & TÍNH CẤP THIẾT", 
               "Tại Sao Chấm Phiếu Bằng Thị Giác Máy Tính Là Giải Pháp Tất Yếu?", 
               "Cân bằng bài toán tối ưu giữa tốc độ, độ chính xác và bài toán ngân sách triển khai giáo dục", "02 / 15")
    add_footer(s2)

    # 3 Comparison Cards
    card_w = Inches(3.7)
    card_h = Inches(3.6)
    cy = Inches(1.9)

    # Card 1: Chấm thủ công
    c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cy, card_w, card_h)
    c1.fill.solid()
    c1.fill.fore_color.rgb = C_CARD
    c1.line.color.rgb = C_RED
    c1.line.width = Pt(1)
    tf = c1.text_frame
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "HẠN CHẾ CHẤM THỦ CÔNG"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_RED
    bullets1 = [
        "Tốc độ cực kỳ chậm: Mất 25 - 30 giây để dò đục lỗ 50 câu cho 1 phiếu thi.",
        "Sai số con người (Human Error): Tỷ lệ sai sót từ 1 - 3% do mỏi mắt, hoa mắt khi chấm liên tục hàng trăm bài.",
        "Rào cản phúc khảo: Phải tìm lại từng bài giấy thủ công, tốn nhiều ngày.",
        "Không có số hóa: Giáo viên phải nhập điểm từng em vào Excel, dễ nhầm dòng."
    ]
    for b in bullets1:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_LIGHT
        p.space_before = Pt(8)

    # Card 2: Máy OMR phần cứng
    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), cy, card_w, card_h)
    c2.fill.solid()
    c2.fill.fore_color.rgb = C_CARD
    c2.line.color.rgb = C_AMBER
    c2.line.width = Pt(1)
    tf = c2.text_frame
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "MÁY QUANG HỌC CHUYÊN DỤNG"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    bullets2 = [
        "Chi phí đầu tư rất lớn: Dao động từ 50 - 150 triệu đồng cho 1 máy chấm OMR.",
        "Đòi hỏi giấy in nhiệt đặc thù: Dễ kẹt giấy khi thời tiết nồm ẩm tại Việt Nam.",
        "Bảo trì phức tạp: Cảm biến quang học dễ bám bụi bẩn làm giảm độ nhạy.",
        "Không thể phổ cập: Các trường THPT vùng nông thôn, trung tâm giáo dục nhỏ khó tiếp cận."
    ]
    for b in bullets2:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_LIGHT
        p.space_before = Pt(8)

    # Card 3: Đề tài
    c3 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), cy, card_w, card_h)
    c3.fill.solid()
    c3.fill.fore_color.rgb = C_CARD_ALT
    c3.line.color.rgb = C_CYAN
    c3.line.width = Pt(1.5)
    tf = c3.text_frame
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "GIẢI PHÁP ĐỀ TÀI: CV OMR"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    bullets3 = [
        "Chi phí bản quyền & phần cứng 0 VNĐ: Chạy trực tiếp trên máy tính thông thường.",
        "Linh hoạt thiết bị: Dùng ảnh chụp từ Camera điện thoại hoặc máy scan sẵn có.",
        "Tốc độ vượt bậc: ~0.22 giây/phiếu (nhanh gấp 100 lần chấm thủ công).",
        "Số hóa & Minh bạch 100%: Tự động xuất Excel 3-Sheet và lưu ảnh vẽ viền trực quan (Audit Overlay)."
    ]
    for b in bullets3:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_WHITE
        p.space_before = Pt(8)

    # Bottom 4 Stats Bar
    stats = [
        ("0.22 Giây", "Tốc độ xử lý / phiếu thi"),
        ("0 VNĐ", "Chi phí phần cứng bổ sung"),
        ("99.1%", "Độ chính xác nhận dạng ô tô"),
        ("100% Số hóa", "Tự động xuất Excel 3-Sheet")
    ]
    stat_w = Inches(2.78)
    for idx, (val, desc) in enumerate(stats):
        sx = Inches(0.8 + idx * 2.98)
        sb = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, Inches(5.7), stat_w, Inches(1.15))
        sb.fill.solid()
        sb.fill.fore_color.rgb = C_CARD
        sb.line.color.rgb = C_BORDER
        sb.line.width = Pt(0.75)
        stf = sb.text_frame
        stf.margin_top = Inches(0.15)
        stf.margin_left = Inches(0.15)
        sp = stf.paragraphs[0]
        sp.alignment = PP_ALIGN.CENTER
        sp.text = val
        sp.font.name = FONT_TITLE
        sp.font.size = Pt(22)
        sp.font.bold = True
        sp.font.color.rgb = C_CYAN
        sp2 = stf.add_paragraph()
        sp2.alignment = PP_ALIGN.CENTER
        sp2.text = desc
        sp2.font.name = FONT_BODY
        sp2.font.size = Pt(10)
        sp2.font.color.rgb = C_MUTED
        sp2.space_before = Pt(3)

    # -------------------------------------------------------------------------
    # SLIDE 3: 02. TỔNG QUAN OMR & 4 THÁCH THỨC BÀI TOÁN
    # -------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "02. TỔNG QUAN OMR & THÁCH THỨC BÀI TOÁN",
               "Bản Chất Công Nghệ OMR & Các Thách Thức Khi Chụp Bằng Điện Thoại",
               "Từ cảm biến quang học truyền thống đến bài toán thị giác máy tính trong môi trường tự nhiên", "03 / 15")
    add_footer(s3)

    # Left: OMR Concepts
    left_c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.2), Inches(4.9))
    left_c.fill.solid()
    left_c.fill.fore_color.rgb = C_CARD
    left_c.line.color.rgb = C_BORDER
    left_c.line.width = Pt(1)
    tf_l = left_c.text_frame
    tf_l.margin_left = Inches(0.3)
    tf_l.margin_top = Inches(0.25)
    p = tf_l.paragraphs[0]
    p.text = "BẢN CHẤT CÔNG NGHỆ OMR"
    p.font.name = FONT_TITLE
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    omr_points = [
        ("Khái niệm OMR (Optical Mark Recognition):", "Công nghệ phát hiện sự có mặt của vết đánh dấu (bút chì, mực) dựa trên sự biến đổi độ hấp thụ và phản xạ ánh sáng."),
        ("Chuyển dịch sang Thị giác máy tính:", "Thay vì phần cứng sensor cơ khí đắt tiền, hệ thống ứng dụng camera số và thuật toán Computer Vision để mô phỏng và vượt qua độ chính xác của máy OMR."),
        ("Quy chuẩn khảo thí THPT Quốc gia:", "Phiếu thi chuẩn gồm 50 câu trắc nghiệm (A-B-C-D), khối Số báo danh (6 chữ số) và khối Mã đề thi (3 chữ số)."),
        ("Yêu cầu độ tin cậy tuyệt đối:", "Trong khảo thí giáo dục, sai sót 0.1 điểm cũng ảnh hưởng đến kết quả thi; do đó phần mềm phải có cơ chế cảnh báo an toàn và lưu vết phúc khảo minh bạch.")
    ]
    for title, desc in omr_points:
        p1 = tf_l.add_paragraph()
        p1.text = title
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_before = Pt(10)
        p2 = tf_l.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10)
        p2.font.color.rgb = C_LIGHT
        p2.space_before = Pt(2)

    # Right: 4 Environmental Challenges
    challenges = [
        ("1. Biến Dạng Phối Cảnh (Perspective Distortion)", 
         "Khi chụp bằng điện thoại cầm tay, góc máy thường bị nghiêng (15-20 độ), méo hình thang, khoảng cách xa gần không cố định, hoặc bị chụp lộn ngược 180 độ.", C_AMBER),
        ("2. Ánh Sáng Bất Đối Xứng & Bóng Đổ (Uneven Illumination)", 
         "Bóng cánh tay, bóng điện thoại, ánh sáng đèn tuýp loang lổ làm thay đổi cường độ sáng cục bộ; khiến các thuật toán phân ngưỡng tĩnh (Fixed Threshold) thất bại hoàn toàn.", C_RED),
        ("3. Nét Chì Mờ & Tẩy Xóa Dở Dang (Incomplete Erasing)", 
         "Thí sinh dùng bút chì 2B tô mờ nhạt hoặc tẩy đổi đáp án nhưng để lại vệt lem xám; rất dễ gây ra hiện tượng dương tính giả (False Positive) hoặc âm tính giả.", C_AMBER),
        ("4. Thí Sinh Tô Đúp Hoặc Bỏ Trống (Double Marks / Blank)", 
         "Cần thuật toán phân biệt rạch ròi giữa tô đúp (phạm quy - 0 điểm) và tô 1 ô có vết tẩy lem, đồng thời đánh cờ '?' cho giáo viên xem xét lại trong 1 giây.", C_CYAN)
    ]
    for idx, (title, desc, acc_col) in enumerate(challenges):
        cy = Inches(1.9 + idx * 1.25)
        ch_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.3), cy, Inches(6.2), Inches(1.12))
        ch_box.fill.solid()
        ch_box.fill.fore_color.rgb = C_CARD
        ch_box.line.color.rgb = C_BORDER
        ch_box.line.width = Pt(0.75)
        
        # Indicator bar left
        ibar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.3), cy, Inches(0.08), Inches(1.12))
        ibar.fill.solid()
        ibar.fill.fore_color.rgb = acc_col
        ibar.line.fill.background()

        ctf = ch_box.text_frame
        ctf.margin_left = Inches(0.2)
        ctf.margin_right = Inches(0.15)
        ctf.margin_top = Inches(0.1)
        cp = ctf.paragraphs[0]
        cp.text = title
        cp.font.name = FONT_TITLE
        cp.font.size = Pt(11)
        cp.font.bold = True
        cp.font.color.rgb = C_WHITE
        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_BODY
        cp2.font.size = Pt(9.5)
        cp2.font.color.rgb = C_LIGHT
        cp2.space_before = Pt(3)

    # -------------------------------------------------------------------------
    # SLIDE 4: 03. MỤC TIÊU & ĐẶC TẢ MẪU PHIẾU THPT50
    # -------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "03. MỤC TIÊU ĐỀ TÀI & ĐẶC TẢ MẪU PHIẾU",
               "Mục Tiêu Nghiên Cứu & Quy Chuẩn Kỹ Thuật Mẫu Phiếu THPT50",
               "Chuẩn hóa kích thước hình học, hệ tọa độ chuẩn 200 DPI và các điểm neo định vị", "04 / 15")
    add_footer(s4)

    # Left Column: Specifications
    c_spec = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(7.0), Inches(4.9))
    c_spec.fill.solid()
    c_spec.fill.fore_color.rgb = C_CARD
    c_spec.line.color.rgb = C_BORDER
    c_spec.line.width = Pt(1)
    tf_s = c_spec.text_frame
    tf_s.margin_left = Inches(0.3)
    tf_s.margin_right = Inches(0.25)
    tf_s.margin_top = Inches(0.25)
    p = tf_s.paragraphs[0]
    p.text = "QUY CHUẨN THIẾT KẾ MẪU PHIẾU FORM THPT50"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    specs = [
        ("Kích thước & Độ phân giải chuẩn hóa:", "Khổ A4 tỷ lệ chuẩn 1 : √2; khi nắn phẳng được quy về ma trận cố định 1653 × 2337 pixels tại độ phân giải 200 DPI."),
        ("4 Dấu định vị góc (Corner Fiducial Markers):", "4 khối vuông đặc màu đen (kích thước 60 × 60 px) đặt tại 4 góc mép trang giấy; là cơ sở toán học để tính ma trận biến đổi phối cảnh."),
        ("1 Dấu định hướng (Orientation Anchor Marker):", "Dấu neo bất đối xứng trên đầu giúp phát hiện chiều lật và tự động đảo ngược 180° nếu người dùng chụp ngược bài thi."),
        ("Khối Số báo danh (SBD):", "6 cột số từ 0 đến 9 (tổng cộng 60 ô tròn bubble), tọa độ pixel được cố định chính xác."),
        ("Khối Mã đề thi (Exam Code):", "3 cột số từ 0 đến 9 (tổng cộng 30 ô tròn bubble), ánh xạ trực tiếp vào kho đề thi."),
        ("Khối Bài làm trắc nghiệm (50 câu hỏi):", "Bao gồm 50 hàng × 4 lựa chọn (A, B, C, D) = 200 ô tròn; chia làm 2 cột cân đối (Cột 1: Câu 1-25; Cột 2: Câu 26-50).")
    ]
    for stitle, sdesc in specs:
        sp1 = tf_s.add_paragraph()
        sp1.text = stitle
        sp1.font.name = FONT_TITLE
        sp1.font.size = Pt(10.5)
        sp1.font.bold = True
        sp1.font.color.rgb = C_WHITE
        sp1.space_before = Pt(6)
        sp2 = tf_s.add_paragraph()
        sp2.text = sdesc
        sp2.font.name = FONT_BODY
        sp2.font.size = Pt(9.5)
        sp2.font.color.rgb = C_LIGHT
        sp2.space_before = Pt(1)

    # Right: Image frame
    img_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.1), Inches(1.9), Inches(4.4), Inches(4.9))
    img_card.fill.solid()
    img_card.fill.fore_color.rgb = C_CARD_ALT
    img_card.line.color.rgb = C_CYAN
    img_card.line.width = Pt(1)
    
    # Embed image: templates/layouts/thpt50_debug.png or templates/phieu_50_cau_chuan.png
    phieu_path = "templates/layouts/thpt50_debug.png"
    if not os.path.exists(phieu_path):
        phieu_path = "templates/phieu_50_cau_chuan.png"
    if os.path.exists(phieu_path):
        s4.shapes.add_picture(phieu_path, Inches(8.5), Inches(2.05), width=Inches(3.6))

    # Caption
    cap_box = s4.shapes.add_textbox(Inches(8.1), Inches(6.35), Inches(4.4), Inches(0.4))
    tf_c = cap_box.text_frame
    cp = tf_c.paragraphs[0]
    cp.alignment = PP_ALIGN.CENTER
    cp.text = "Cấu trúc Layout FormTHPT50 & Hệ lưới Bounding Box"
    cp.font.name = FONT_BODY
    cp.font.size = Pt(9.5)
    cp.font.color.rgb = C_MUTED

    # -------------------------------------------------------------------------
    # SLIDE 5: 04. KIẾN TRÚC HỆ THỐNG PHẦN MỀM (4 TẦNG)
    # -------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "04. KIẾN TRÚC HỆ THỐNG PHẦN MỀM",
               "Thiết Kế Đa Tầng Module Hóa Cao (Layered Architecture)",
               "Phân tách trách nhiệm độc lập: Presentation, Controller, Core CV và Data Layer", "05 / 15")
    add_footer(s5)

    # Left: 4 Layers Description
    layers = [
        ("Tầng 1: Presentation Layer (CustomTkinter GUI)",
         "Giao diện người dùng hiện đại, trực quan, hỗ trợ Dark/Light Theme. Cung cấp các chức năng nạp đáp án, chọn ảnh chấm đơn lẻ, chọn thư mục chấm hàng loạt, thanh tiến trình và bảng thống kê kết quả trực tiếp.", C_CYAN),
        ("Tầng 2: Controller & Integration Layer",
         "Điều phối toàn bộ luồng dữ liệu (Workflow Controller). Tích hợp kiến trúc đa luồng (Multi-threading) tách biệt tiến trình tính toán CV nặng khỏi giao diện chính để chống đơ/lag.", C_LIGHT),
        ("Tầng 3: Core CV & Backend Layer (Lõi Xử Lý)",
         "Module nắn phẳng phối cảnh (Perspective Warping), Module trích xuất Bubble Grid theo Template JSON, Thuật toán Relative Ink Contrast đo độ đậm nhạt và Rule Engine tính điểm.", C_GREEN),
        ("Tầng 4: Data & Export Layer (Lưu Trữ & Xuất Báo Cáo)",
         "Tự động tạo bảng điểm Excel 3-Sheet tiêu chuẩn qua OpenPyXL, quản lý cấu hình mẫu JSON, ghi vết Audit Log và lưu ảnh Overlay phục vụ hậu kiểm phúc khảo.", C_AMBER)
    ]

    for idx, (ltitle, ldesc, acc_col) in enumerate(layers):
        ly = Inches(1.9 + idx * 1.25)
        lbox = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), ly, Inches(5.8), Inches(1.15))
        lbox.fill.solid()
        lbox.fill.fore_color.rgb = C_CARD
        lbox.line.color.rgb = C_BORDER
        lbox.line.width = Pt(0.75)

        ibar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), ly, Inches(0.08), Inches(1.15))
        ibar.fill.solid()
        ibar.fill.fore_color.rgb = acc_col
        ibar.line.fill.background()

        ltf = lbox.text_frame
        ltf.margin_left = Inches(0.2)
        ltf.margin_right = Inches(0.15)
        ltf.margin_top = Inches(0.1)
        lp1 = ltf.paragraphs[0]
        lp1.text = ltitle
        lp1.font.name = FONT_TITLE
        lp1.font.size = Pt(11)
        lp1.font.bold = True
        lp1.font.color.rgb = C_WHITE
        lp2 = ltf.add_paragraph()
        lp2.text = ldesc
        lp2.font.name = FONT_BODY
        lp2.font.size = Pt(9.5)
        lp2.font.color.rgb = C_LIGHT
        lp2.space_before = Pt(3)

    # Right: Architecture Diagram
    diag_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.9), Inches(5.6), Inches(4.9))
    diag_card.fill.solid()
    diag_card.fill.fore_color.rgb = C_CARD
    diag_card.line.color.rgb = C_CYAN
    diag_card.line.width = Pt(1)

    diag_p = "demo_output/figures/hinh_2_1_kien_truc_he_thong.png"
    if os.path.exists(diag_p):
        s5.shapes.add_picture(diag_p, Inches(7.1), Inches(2.2), width=Inches(5.2))

    cap_box5 = s5.shapes.add_textbox(Inches(6.9), Inches(6.35), Inches(5.6), Inches(0.4))
    tf_c5 = cap_box5.text_frame
    cp5 = tf_c5.paragraphs[0]
    cp5.alignment = PP_ALIGN.CENTER
    cp5.text = "Sơ đồ kiến trúc 4 tầng phân lập của hệ thống chấm OMR"
    cp5.font.name = FONT_BODY
    cp5.font.size = Pt(9.5)
    cp5.font.color.rgb = C_MUTED

    # -------------------------------------------------------------------------
    # SLIDE 6: 05. PIPELINE THỊ GIÁC MÁY TÍNH (7 BƯỚC)
    # -------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "05. PIPELINE THỊ GIÁC MÁY TÍNH",
               "Quy Trình 7 Bước Xử Lý Ảnh Đầu Vào Thành Điểm Số",
               "Chuỗi xử lý logic tuần tự từ ma trận điểm ảnh thô đến bảng điểm số hóa chuẩn xác", "06 / 15")
    add_footer(s6)

    # Top: Pipeline Image Diagram
    pipe_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(11.733), Inches(2.8))
    pipe_card.fill.solid()
    pipe_card.fill.fore_color.rgb = C_CARD
    pipe_card.line.color.rgb = C_BORDER
    pipe_card.line.width = Pt(1)

    pipe_img = "demo_output/figures/hinh_2_2_pipeline_cv.png"
    if os.path.exists(pipe_img):
        s6.shapes.add_picture(pipe_img, Inches(1.8), Inches(1.95), width=Inches(9.7))

    # Bottom: 7 Step Cards
    steps = [
        ("B1. Tiền xử lý", "Grayscale &\nGaussian Blur\nlọc nhiễu hạt."),
        ("B2. Phân ngưỡng", "Otsu & Adaptive\nThresholding\ntìm contour cạnh."),
        ("B3. Marker 4 góc", "Lọc hình học\ntìm 4 dấu vuông\nđịnh vị góc."),
        ("B4. Nắn phẳng", "Perspective\nTransformation\nvề 1653×2337."),
        ("B5. Đảo chiều", "Kiểm tra Anchor\ntự động lật 180°\nnếu bị ngược."),
        ("B6. Tách Bubble", "Cắt ROI 290 ô tròn\ntheo layout JSON\ncố định."),
        ("B7. Chấm điểm", "Relative Ink\nContrast &\nTra bảng đáp án.")
    ]
    sw = Inches(1.58)
    for idx, (stitle, sdesc) in enumerate(steps):
        sx = Inches(0.8 + idx * 1.69)
        sbox = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, Inches(4.8), sw, Inches(2.0))
        sbox.fill.solid()
        sbox.fill.fore_color.rgb = C_CARD_ALT if idx in [3, 6] else C_CARD
        sbox.line.color.rgb = C_CYAN if idx in [3, 6] else C_BORDER
        sbox.line.width = Pt(1)

        stf = sbox.text_frame
        stf.margin_left = Inches(0.12)
        stf.margin_right = Inches(0.1)
        stf.margin_top = Inches(0.15)
        p1 = stf.paragraphs[0]
        p1.text = stitle
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = C_CYAN if idx in [3, 6] else C_WHITE
        p2 = stf.add_paragraph()
        p2.text = sdesc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_LIGHT
        p2.space_before = Pt(6)

    # -------------------------------------------------------------------------
    # SLIDE 7: 06. THUẬT TOÁN ĐỊNH VỊ & NẮN PHẲNG
    # -------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "06. THUẬT TOÁN ĐỊNH VỊ & NẮN PHẲNG",
               "Khắc Phục Biến Dạng Góc Nghiêng Chụp Điện Thoại & Tự Đảo Chiều",
               "Sử dụng 4 Fiducial Markers, Phép biến đổi phối cảnh 8 bậc tự do và Neo định hướng", "07 / 15")
    add_footer(s7)

    # Left: Mathematical & Algorithmic Principle
    c_warp = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(6.6), Inches(4.9))
    c_warp.fill.solid()
    c_warp.fill.fore_color.rgb = C_CARD
    c_warp.line.color.rgb = C_BORDER
    c_warp.line.width = Pt(1)
    tf_w = c_warp.text_frame
    tf_w.margin_left = Inches(0.3)
    tf_w.margin_top = Inches(0.25)
    p = tf_w.paragraphs[0]
    p.text = "NGUYÊN LÝ BIẾN ĐỔI PHỐI CẢNH (HOMOGRAPHY TRANSFORM)"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    warp_points = [
        ("1. Tìm kiếm & Lọc 4 Marker góc:", "Áp dụng cv2.findContours trên ảnh nhị phân. Lọc các contour thỏa mãn: tỷ lệ khung bao gần vuông (Aspect Ratio ≈ 1.0) và diện tích nằm trong dải [S_min, S_max]."),
        ("2. Quy tắc sắp xếp 4 đỉnh hình học bất biến:", 
         "Để chống xáo trộn thứ tự đỉnh khi góc xoay thay đổi:\n"
         "• Top-Left = argmin(x + y)\n"
         "• Bottom-Right = argmax(x + y)\n"
         "• Top-Right = argmin(y - x)\n"
         "• Bottom-Left = argmax(y - x)"),
        ("3. Thiết lập ma trận biến đổi phối cảnh M:", "Dùng cv2.getPerspectiveTransform(pts_src, pts_dst) và cv2.warpPerspective để nắn phẳng tờ phiếu về hệ tọa độ chuẩn 1653 × 2337 px."),
        ("4. Thuật toán tự động đảo chiều xoay 180°:", "Sau khi nắn phẳng, hệ thống quét vùng ROI của Anchor Marker ở góc trên. Nếu độ sáng vượt ngưỡng (nghĩa là không có marker đen do bị xoay ngược 180°), hàm tự động gọi cv2.rotate(..., ROTATE_180).")
    ]
    for wtitle, wdesc in warp_points:
        wp1 = tf_w.add_paragraph()
        wp1.text = wtitle
        wp1.font.name = FONT_TITLE
        wp1.font.size = Pt(10.5)
        wp1.font.bold = True
        wp1.font.color.rgb = C_WHITE
        wp1.space_before = Pt(6)
        wp2 = tf_w.add_paragraph()
        wp2.text = wdesc
        wp2.font.name = FONT_BODY
        wp2.font.size = Pt(9.5)
        wp2.font.color.rgb = C_LIGHT
        wp2.space_before = Pt(1)

    # Right: Visual Comparison (Raw angled photo vs Aligned sheet)
    rcard1 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.7), Inches(1.9), Inches(2.3), Inches(4.9))
    rcard1.fill.solid()
    rcard1.fill.fore_color.rgb = C_CARD
    rcard1.line.color.rgb = C_AMBER
    rcard1.line.width = Pt(1)
    
    raw_img = "Test_TGMT.jpg"
    if os.path.exists(raw_img):
        s7.shapes.add_picture(raw_img, Inches(7.8), Inches(2.1), width=Inches(2.1))
    
    cap1 = s7.shapes.add_textbox(Inches(7.7), Inches(6.3), Inches(2.3), Inches(0.4))
    cp1 = cap1.text_frame.paragraphs[0]
    cp1.alignment = PP_ALIGN.CENTER
    cp1.text = "Ảnh gốc điện thoại (Nghiêng & bóng)"
    cp1.font.name = FONT_BODY
    cp1.font.size = Pt(8.5)
    cp1.font.color.rgb = C_MUTED

    rcard2 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.2), Inches(1.9), Inches(2.3), Inches(4.9))
    rcard2.fill.solid()
    rcard2.fill.fore_color.rgb = C_CARD_ALT
    rcard2.line.color.rgb = C_CYAN
    rcard2.line.width = Pt(1.5)

    aligned_img = "demo_output/test_tgmt_aligned.png"
    if os.path.exists(aligned_img):
        s7.shapes.add_picture(aligned_img, Inches(10.3), Inches(2.1), width=Inches(2.1))

    cap2 = s7.shapes.add_textbox(Inches(10.2), Inches(6.3), Inches(2.3), Inches(0.4))
    cp2 = cap2.text_frame.paragraphs[0]
    cp2.alignment = PP_ALIGN.CENTER
    cp2.text = "Sau nắn phẳng (1653×2337 px)"
    cp2.font.name = FONT_BODY
    cp2.font.size = Pt(8.5)
    cp2.font.color.rgb = C_CYAN

    # -------------------------------------------------------------------------
    # SLIDE 8: 07. ĐỘT PHÁ THUẬT TOÁN: RELATIVE INK CONTRAST
    # -------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "07. ĐỘT PHÁ THUẬT TOÁN: RELATIVE INK CONTRAST",
               "Giải Pháp Chống Biến Thiên Ánh Sáng & Vết Chì Tẩy Xóa",
               "Bản chất công thức toán học giúp hệ thống đạt độ chính xác 99.1% so với 69.3% của ngưỡng tĩnh", "08 / 15")
    add_footer(s8)

    # Left: Explanation & Formulation
    c_ric = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.8), Inches(4.9))
    c_ric.fill.solid()
    c_ric.fill.fore_color.rgb = C_CARD
    c_ric.line.color.rgb = C_BORDER
    c_ric.line.width = Pt(1)
    tf_r = c_ric.text_frame
    tf_r.margin_left = Inches(0.3)
    tf_r.margin_top = Inches(0.2)
    p = tf_r.paragraphs[0]
    p.text = "CÔNG THỨC ĐO ĐỘ TƯƠNG PHẢN TƯƠNG ĐỐI"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    # Formula Box
    f_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(2.4), Inches(5.2), Inches(0.75))
    f_box.fill.solid()
    f_box.fill.fore_color.rgb = C_CARD_ALT
    f_box.line.color.rgb = C_CYAN
    f_box.line.width = Pt(1)
    ftf = f_box.text_frame
    fp = ftf.paragraphs[0]
    fp.alignment = PP_ALIGN.CENTER
    fp.text = "C = I_paper  -  I_inner"
    fp.font.name = "Consolas"
    fp.font.size = Pt(16)
    fp.font.bold = True
    fp.font.color.rgb = C_CYAN

    ric_details = [
        ("Ý nghĩa các đại lượng:", 
         "• I_paper: Cường độ sáng trung bình của vành khăn giấy trắng bao quanh ô tròn (Background Ring).\n"
         "• I_inner: Cường độ sáng trung bình của vùng lõi tròn bên trong (Inner Bubble Core)."),
        ("Miễn nhiễm với bóng đổ cục bộ (Shadow Invariance):", 
         "Khi có bóng cánh tay hay bóng đèn đổ xuống, cường độ sáng của cả I_paper và I_inner đều giảm đi cùng một đại lượng ΔL. Do đó hiệu số C = (I_paper - ΔL) - (I_inner - ΔL) vẫn giữ nguyên giá trị!"),
        ("Tách biệt rõ nét vết tẩy chì dở dang:", 
         "• Ô để trắng hoàn toàn: C ≈ 0 đến 10.\n"
         "• Ô có vết chì tẩy mờ / lem: C ≈ 15 đến 25.\n"
         "• Ô tô chuẩn bằng bút chì 2B: C ≥ 40 đến 120."),
        ("Không cần tinh chỉnh ngưỡng thủ công:", 
         "Tự động thích nghi với từng loại giấy in, chất lượng camera và mọi điều kiện môi trường phòng học.")
    ]
    for rtitle, rdesc in ric_details:
        rp1 = tf_r.add_paragraph()
        rp1.text = rtitle
        rp1.font.name = FONT_TITLE
        rp1.font.size = Pt(10)
        rp1.font.bold = True
        rp1.font.color.rgb = C_WHITE
        rp1.space_before = Pt(5)
        rp2 = tf_r.add_paragraph()
        rp2.text = rdesc
        rp2.font.name = FONT_BODY
        rp2.font.size = Pt(9.2)
        rp2.font.color.rgb = C_LIGHT
        rp2.space_before = Pt(1)

    # Right: Diagram
    d_ric = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.9), Inches(5.6), Inches(4.9))
    d_ric.fill.solid()
    d_ric.fill.fore_color.rgb = C_CARD
    d_ric.line.color.rgb = C_CYAN
    d_ric.line.width = Pt(1)

    ric_diag = "demo_output/figures/hinh_2_4_nguyen_ly_omr.png"
    if os.path.exists(ric_diag):
        s8.shapes.add_picture(ric_diag, Inches(7.1), Inches(2.2), width=Inches(5.2))

    cap_box8 = s8.shapes.add_textbox(Inches(6.9), Inches(6.35), Inches(5.6), Inches(0.4))
    tf_c8 = cap_box8.text_frame
    cp8 = tf_c8.paragraphs[0]
    cp8.alignment = PP_ALIGN.CENTER
    cp8.text = "Cơ chế phân tích vành đồng tâm và tính tương phản quang học"
    cp8.font.name = FONT_BODY
    cp8.font.size = Pt(9.5)
    cp8.font.color.rgb = C_MUTED

    # -------------------------------------------------------------------------
    # SLIDE 9: 08. TRÍCH XUẤT DỮ LIỆU & AN TOÀN NGOẠI LỆ
    # -------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "08. TRÍCH XUẤT DỮ LIỆU & AN TOÀN NGOẠI LỆ",
               "Quy Tắc Nghiệp Vụ (Business Logic) & Cơ Chế Flagging Minh Bạch",
               "Xử lý chuẩn xác các tình huống thí sinh tô đúp, bỏ trống hoặc sai mã đề thi", "09 / 15")
    add_footer(s9)

    # 3 Cards Layout
    cw = Inches(3.7)
    ch = Inches(4.9)
    
    # Card 1: SBD & Exam Code
    c_sbd = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), cw, ch)
    c_sbd.fill.solid()
    c_sbd.fill.fore_color.rgb = C_CARD
    c_sbd.line.color.rgb = C_CYAN
    c_sbd.line.width = Pt(1)
    tf1 = c_sbd.text_frame
    tf1.margin_left = Inches(0.25)
    tf1.margin_top = Inches(0.2)
    p = tf1.paragraphs[0]
    p.text = "1. TRÍCH XUẤT SBD & MÃ ĐỀ"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    b1 = [
        "Số báo danh (6 chữ số): Quét từng cột từ 0-9. Chọn ô có độ tương phản C_max lớn nhất.",
        "Mã đề thi (3 chữ số): Quét 3 cột tương ứng. Tự động chuyển chuỗi 3 chữ số thành mã đề chuẩn (VD: '101').",
        "Đối soát ngân hàng đáp án: Nếu mã đề không nằm trong cấu hình tệp đáp án nạp vào, hệ thống phát cảnh báo 'INVALID_EXAM_CODE'.",
        "An toàn dữ liệu: Ghi nhận cảnh báo nghi vấn nếu cột SBD có cột thí sinh bỏ trống."
    ]
    for b in b1:
        p = tf1.add_paragraph()
        p.text = "• " + b
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = C_LIGHT
        p.space_before = Pt(8)

    # Card 2: Double Mark & Blank
    c_dbl = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(1.9), cw, ch)
    c_dbl.fill.solid()
    c_dbl.fill.fore_color.rgb = C_CARD
    c_dbl.line.color.rgb = C_AMBER
    c_dbl.line.width = Pt(1)
    tf2 = c_dbl.text_frame
    tf2.margin_left = Inches(0.25)
    tf2.margin_top = Inches(0.2)
    p = tf2.paragraphs[0]
    p.text = "2. XỬ LÝ TÔ ĐÚP & BỎ TRỐNG"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    b2 = [
        "Phát hiện tô đúp (Double Mark): Tính tỷ số giữa ô đậm nhất và ô đậm thứ nhì: R = C1 / C2.",
        "Quy tắc đánh cờ: Nếu C1 >= C_min và C2 >= C_min mà R < 1.35 (độ đậm xấp xỉ nhau), gán trạng thái DOUBLE_MARK.",
        "Áp dụng quy chế Bộ GD&ĐT: Câu tô đúp bị tính 0 điểm nhưng vẫn được đánh dấu minh bạch.",
        "Câu bỏ trống (Blank): Nếu C_max < C_min, ghi nhận ký tự ' ' (bỏ trống), không suy đoán bừa bãi."
    ]
    for b in b2:
        p = tf2.add_paragraph()
        p.text = "• " + b
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = C_LIGHT
        p.space_before = Pt(8)

    # Card 3: Audit & Review
    c_aud = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.9), cw, ch)
    c_aud.fill.solid()
    c_aud.fill.fore_color.rgb = C_CARD_ALT
    c_aud.line.color.rgb = C_GREEN
    c_aud.line.width = Pt(1)
    tf3 = c_aud.text_frame
    tf3.margin_left = Inches(0.25)
    tf3.margin_top = Inches(0.2)
    p = tf3.paragraphs[0]
    p.text = "3. AUDIT OVERLAY & PHÚC KHẢO"
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    b3 = [
        "Lưu ảnh Visual Overlay: Vẽ trực tiếp kết quả lên ảnh bài thi để lưu trữ vĩnh viễn.",
        "Màu sắc trực quan chuẩn hóa:\n• Vòng tròn xanh lá: Đáp án đúng.\n• Vòng tròn đỏ: Thí sinh làm sai.\n• Dấu chấm hỏi vàng (?): Ngoại lệ tô đúp / nghi vấn.",
        "Phúc khảo siêu tốc: Giám khảo chỉ cần mở ảnh overlay là đối chiếu được ngay trong 1 giây mà không cần lật lại phiếu giấy.",
        "Nhật ký Audit Log: Lưu file json/log chi tiết từng bài làm."
    ]
    for b in b3:
        p = tf3.add_paragraph()
        p.text = "• " + b
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = C_WHITE
        p.space_before = Pt(8)

    # -------------------------------------------------------------------------
    # SLIDE 10: 09. GIAO DIỆN ỨNG DỤNG & QUY TRÌNH 3 BƯỚC
    # -------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "09. GIAO DIỆN ỨNG DỤNG & TRẢI NGHIỆM",
               "Thiết Kế Tối Giản, Trực Quan & Vận Hành Trong 3 Bước",
               "Xây dựng trên CustomTkinter hiện đại, hỗ trợ Dark/Light Theme và Chế độ Chấm Hàng Loạt", "10 / 15")
    add_footer(s10)

    # Top: Workflow Diagram
    wf_card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(11.733), Inches(2.7))
    wf_card.fill.solid()
    wf_card.fill.fore_color.rgb = C_CARD
    wf_card.line.color.rgb = C_BORDER
    wf_card.line.width = Pt(1)

    wf_img = "demo_output/figures/hinh_3_1_quy_trinh_3_buoc.png"
    if os.path.exists(wf_img):
        s10.shapes.add_picture(wf_img, Inches(2.3), Inches(1.95), width=Inches(8.7))

    # Bottom 3 Step Explanations
    c_w = Inches(3.7)
    cy_b = Inches(4.75)
    
    steps_ui = [
        ("BƯỚC 1: NẠP ĐÁP ÁN", "Chọn tệp Excel hoặc JSON chứa đáp án. Hệ thống hỗ trợ nạp đồng thời nhiều mã đề (VD: 101, 102, 103, 104) với bảng xem trước trực quan.", C_CYAN),
        ("BƯỚC 2: CHỌN NGUỒN ẢNH", "Hỗ trợ 2 chế độ linh hoạt:\n• Chấm 1 ảnh: Kiểm tra nhanh bài thi bất kỳ.\n• Chấm thư mục (Batch): Xử lý hàng loạt hàng trăm bài thi chỉ trong 1 lần bấm.", C_LIGHT),
        ("BƯỚC 3: CHẤM & XUẤT FILE", "Bấm 'Bắt đầu chấm'. Hệ thống chạy đa luồng ngầm với thanh tiến trình real-time. Tự động lưu thư mục kết quả gồm ảnh Overlay và file Excel 3-Sheet.", C_GREEN)
    ]
    for idx, (utitle, udesc, acc) in enumerate(steps_ui):
        bx = Inches(0.8 + idx * 4.0)
        ubox = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, cy_b, c_w, Inches(2.05))
        ubox.fill.solid()
        ubox.fill.fore_color.rgb = C_CARD_ALT if idx == 2 else C_CARD
        ubox.line.color.rgb = acc
        ubox.line.width = Pt(1)

        utf = ubox.text_frame
        utf.margin_left = Inches(0.2)
        utf.margin_right = Inches(0.15)
        utf.margin_top = Inches(0.15)
        up1 = utf.paragraphs[0]
        up1.text = utitle
        up1.font.name = FONT_TITLE
        up1.font.size = Pt(11.5)
        up1.font.bold = True
        up1.font.color.rgb = acc
        up2 = utf.add_paragraph()
        up2.text = udesc
        up2.font.name = FONT_BODY
        up2.font.size = Pt(9.5)
        up2.font.color.rgb = C_WHITE if idx == 2 else C_LIGHT
        up2.space_before = Pt(6)

    # -------------------------------------------------------------------------
    # SLIDE 11: 10. THỰC NGHIỆM TRÊN ẢNH CHỤP THỰC TẾ
    # -------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "10. THỰC NGHIỆM TRÊN ẢNH CHỤP THỰC TẾ",
               "Khả Năng Khắc Phục Biến Dạng Trên Ảnh Chụp Camera Di Động",
               "Kiểm chứng năng lực xử lý góc nghiêng, nền bàn gỗ và chênh lệch sáng từ camera điện thoại", "11 / 15")
    add_footer(s11)

    # Side-by-side comparison
    # Left: Raw Phone Photo
    raw_card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.9))
    raw_card.fill.solid()
    raw_card.fill.fore_color.rgb = C_CARD
    raw_card.line.color.rgb = C_AMBER
    raw_card.line.width = Pt(1)

    # Image Left
    if os.path.exists("Test_TGMT.jpg"):
        s11.shapes.add_picture("Test_TGMT.jpg", Inches(1.1), Inches(2.1), width=Inches(2.5))

    # Notes Left
    rtf = raw_card.text_frame
    rtf.margin_left = Inches(2.9)
    rtf.margin_top = Inches(0.25)
    rp = rtf.paragraphs[0]
    rp.text = "ẢNH CHỤP GỐC TỪ ĐIỆN THOẠI"
    rp.font.name = FONT_TITLE
    rp.font.size = Pt(11)
    rp.font.bold = True
    rp.font.color.rgb = C_AMBER

    raw_features = [
        "Biến dạng phối cảnh:", "Góc chụp nghiêng ~15°, khoảng cách không đều, méo hình học.",
        "Hậu cảnh phức tạp:", "Mặt bàn gỗ vân tối xung quanh gây nhiễu biên.",
        "Chiếu sáng nghiêng:", "Ánh sáng đèn phòng lệch một bên, xuất hiện vùng bóng loãng."
    ]
    for idx in range(0, len(raw_features), 2):
        p1 = rtf.add_paragraph()
        p1.text = "• " + raw_features[idx]
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_before = Pt(6)
        p2 = rtf.add_paragraph()
        p2.text = raw_features[idx+1]
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9)
        p2.font.color.rgb = C_LIGHT
        p2.space_before = Pt(1)

    # Right: Aligned Photo
    align_card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.9), Inches(5.6), Inches(4.9))
    align_card.fill.solid()
    align_card.fill.fore_color.rgb = C_CARD_ALT
    align_card.line.color.rgb = C_CYAN
    align_card.line.width = Pt(1.5)

    # Image Right
    if os.path.exists("demo_output/test_tgmt_aligned.png"):
        s11.shapes.add_picture("demo_output/test_tgmt_aligned.png", Inches(7.2), Inches(2.1), width=Inches(2.5))

    atf = align_card.text_frame
    atf.margin_left = Inches(2.9)
    atf.margin_top = Inches(0.25)
    ap = atf.paragraphs[0]
    ap.text = "KẾT QUẢ NẮN PHẲNG TỰ ĐỘNG"
    ap.font.name = FONT_TITLE
    ap.font.size = Pt(11)
    ap.font.bold = True
    ap.font.color.rgb = C_CYAN

    align_features = [
        "Loại bỏ 100% nền bàn gỗ:", "Tách độc lập tờ phiếu thi khỏi mọi vật thể nền xung quanh.",
        "Khôi phục kích thước A4:", "Quy chuẩn hóa chính xác về 1653 × 2337 pixels (200 DPI).",
        "Khớp tuyệt đối Bounding Box:", "Các ô tròn bubble nằm đúng tọa độ định sẵn, sẵn sàng cho công đoạn trích xuất."
    ]
    for idx in range(0, len(align_features), 2):
        p1 = atf.add_paragraph()
        p1.text = "• " + align_features[idx]
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = C_CYAN
        p1.space_before = Pt(6)
        p2 = atf.add_paragraph()
        p2.text = align_features[idx+1]
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9)
        p2.font.color.rgb = C_WHITE
        p2.space_before = Pt(1)

    # -------------------------------------------------------------------------
    # SLIDE 12: 11. KẾT QUẢ ĐO LƯỜNG ĐỊNH LƯỢNG & HIỆU NĂNG
    # -------------------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "11. KẾT QUẢ THỰC NGHIỆM & ĐO LƯỜNG ĐỊNH LƯỢNG",
               "Minh Chứng Độ Tin Cậy & Đo Lường Hiệu Năng Thực Tế",
               "Bao phủ kiểm thử tự động với Pytest và phân rã thời gian xử lý từng công đoạn", "12 / 15")
    add_footer(s12)

    # Top 4 Stat Cards
    metrics = [
        ("27 / 27 (100%)", "Kiểm thử tự động Pytest passed", C_GREEN),
        ("0.22 Giây", "Thời gian chấm trung bình / phiếu", C_CYAN),
        ("99.1%", "Độ chính xác Relative Ink Contrast", C_CYAN),
        ("0% UI Lag", "Đa luồng Multi-threading mượt mà", C_GREEN)
    ]
    mw = Inches(2.78)
    for idx, (mval, mdesc, mcol) in enumerate(metrics):
        mx = Inches(0.8 + idx * 2.98)
        mb = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, mx, Inches(1.9), mw, Inches(1.3))
        mb.fill.solid()
        mb.fill.fore_color.rgb = C_CARD
        mb.line.color.rgb = mcol
        mb.line.width = Pt(1)

        mtf = mb.text_frame
        mtf.margin_top = Inches(0.18)
        mtf.margin_left = Inches(0.15)
        mp = mtf.paragraphs[0]
        mp.alignment = PP_ALIGN.CENTER
        mp.text = mval
        mp.font.name = FONT_TITLE
        mp.font.size = Pt(20)
        mp.font.bold = True
        mp.font.color.rgb = mcol
        mp2 = mtf.add_paragraph()
        mp2.alignment = PP_ALIGN.CENTER
        mp2.text = mdesc
        mp2.font.name = FONT_BODY
        mp2.font.size = Pt(9.5)
        mp2.font.color.rgb = C_LIGHT
        mp2.space_before = Pt(4)

    # Bottom: Latency Breakdown Table / Cards
    b_card = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.4), Inches(11.733), Inches(3.4))
    b_card.fill.solid()
    b_card.fill.fore_color.rgb = C_CARD
    b_card.line.color.rgb = C_BORDER
    b_card.line.width = Pt(1)

    btf = b_card.text_frame
    btf.margin_left = Inches(0.3)
    btf.margin_top = Inches(0.2)
    bp = btf.paragraphs[0]
    bp.text = "PHÂN RÃ ĐỘ TRỄ XỬ LÝ THEO TỪNG CÔNG ĐOẠN (LATENCY BREAKDOWN)"
    bp.font.name = FONT_TITLE
    bp.font.size = Pt(12)
    bp.font.bold = True
    bp.font.color.rgb = C_CYAN

    # Breakdown Items
    latencies = [
        ("1. Đọc ảnh từ ổ đĩa & Tiền xử lý (Grayscale + Gaussian Blur)", "0.04 giây", "18%", "Đọc I/O và giải mã ma trận điểm ảnh độ phân giải cao"),
        ("2. Định vị 4 Marker góc & Nắn phẳng phối cảnh (Warping)", "0.09 giây", "41%", "Tìm kiếm contour, lọc tỷ lệ khung bao và tính ma trận Homography"),
        ("3. Trích xuất ROI 290 ô tròn & Tính Relative Ink Contrast", "0.07 giây", "32%", "Cắt lõi ô, vành khăn nền giấy và tính hiệu số độ sáng C"),
        ("4. Tra bảng đáp án, tính điểm & Lưu ảnh Audit Overlay", "0.02 giây", "9%", "So khớp key đáp án, ghi nhật ký và vẽ viền xanh/đỏ")
    ]
    for idx, (pname, ptime, ppct, pnote) in enumerate(latencies):
        ly = Inches(3.95 + idx * 0.65)
        # Bar representation
        lshape = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), ly, Inches(11.1), Inches(0.55))
        lshape.fill.solid()
        lshape.fill.fore_color.rgb = C_CARD_ALT
        lshape.line.color.rgb = C_BORDER
        lshape.line.width = Pt(0.5)

        ltf = lshape.text_frame
        ltf.margin_left = Inches(0.2)
        ltf.margin_top = Inches(0.08)
        p = ltf.paragraphs[0]
        p.text = f"{pname}  —  "
        p.font.name = FONT_TITLE
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        
        # append time & pct
        run = p.add_run()
        run.text = f"{ptime} ({ppct})"
        run.font.bold = True
        run.font.color.rgb = C_CYAN
        
        p2 = ltf.add_paragraph()
        p2.text = pnote
        p2.font.name = FONT_BODY
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = C_MUTED

    # -------------------------------------------------------------------------
    # SLIDE 13: 12. BÁO CÁO ĐIỂM SỐ ĐA CHIỀU & AUDIT MINH BẠCH
    # -------------------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "12. KẾT QUẢ ĐẦU RA & BÁO CÁO SỐ HÓA",
               "Đầu Ra Minh Bạch: Ảnh Audit Trực Quan & Báo Cáo Excel 3-Sheet",
               "Phục vụ trọn vẹn 2 nhu cầu thiết yếu: Tra cứu phúc khảo tức thì và Thống kê phân tích phổ điểm", "13 / 15")
    add_footer(s13)

    # 2 Columns
    # Left: Visual Overlay
    c_vo = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.9))
    c_vo.fill.solid()
    c_vo.fill.fore_color.rgb = C_CARD
    c_vo.line.color.rgb = C_CYAN
    c_vo.line.width = Pt(1)

    vo_img = "demo_output/result_sample_student_raw.png"
    if os.path.exists(vo_img):
        s13.shapes.add_picture(vo_img, Inches(1.0), Inches(2.1), width=Inches(2.5))

    votf = c_vo.text_frame
    votf.margin_left = Inches(2.8)
    votf.margin_top = Inches(0.2)
    vp = votf.paragraphs[0]
    vp.text = "ẢNH AUDIT OVERLAY MINH BẠCH"
    vp.font.name = FONT_TITLE
    vp.font.size = Pt(11)
    vp.font.bold = True
    vp.font.color.rgb = C_CYAN

    vo_points = [
        ("Vòng tròn xanh lá:", "Bao quanh các câu thí sinh làm ĐÚNG."),
        ("Vòng tròn đỏ:", "Bao quanh các câu thí sinh làm SAI (kèm gạch chéo đáp án đúng)."),
        ("Dấu hỏi vàng (?):", "Cảnh báo câu tô đúp hoặc tẩy xóa nghi vấn."),
        ("Header tự động:", "Hiển thị SBD, Mã đề và Điểm số (VD: 8.8 / 10.0) ngay đầu trang."),
        ("Giá trị pháp lý:", "Lưu ảnh số vĩnh viễn, giải quyết khiếu nại phúc khảo ngay lập tức.")
    ]
    for vtitle, vdesc in vo_points:
        p1 = votf.add_paragraph()
        p1.text = "• " + vtitle
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_before = Pt(4)
        p2 = votf.add_paragraph()
        p2.text = vdesc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9)
        p2.font.color.rgb = C_LIGHT
        p2.space_before = Pt(1)

    # Right: Excel Structure
    c_ex = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.9), Inches(5.6), Inches(4.9))
    c_ex.fill.solid()
    c_ex.fill.fore_color.rgb = C_CARD
    c_ex.line.color.rgb = C_GREEN
    c_ex.line.width = Pt(1)

    ex_img = "demo_output/figures/hinh_3_5_cau_truc_excel.png"
    if os.path.exists(ex_img):
        s13.shapes.add_picture(ex_img, Inches(7.1), Inches(2.1), width=Inches(5.2))

    extf = c_ex.text_frame
    extf.margin_left = Inches(0.3)
    extf.margin_top = Inches(2.9)
    ep = extf.paragraphs[0]
    ep.text = "CẤU TRÚC BÁO CÁO EXCEL 3-SHEET TỰ ĐỘNG"
    ep.font.name = FONT_TITLE
    ep.font.size = Pt(11)
    ep.font.bold = True
    ep.font.color.rgb = C_GREEN

    sheets = [
        ("Sheet 1: Tổng hợp điểm", "Danh sách SBD, Mã đề, Số câu đúng, Điểm số thang 10, Xếp loại học lực."),
        ("Sheet 2: Chi tiết câu làm", "Bảng ma trận phương án (A/B/C/D) từng câu của từng học sinh để tra cứu sâu."),
        ("Sheet 3: Thống kê phổ điểm", "Biểu đồ phân bố điểm số và Tỷ lệ làm sai từng câu giúp giáo viên tối ưu đề thi.")
    ]
    for stitle, sdesc in sheets:
        p1 = extf.add_paragraph()
        p1.text = "• " + stitle + ":"
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_before = Pt(3)
        p2 = extf.add_paragraph()
        p2.text = sdesc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9)
        p2.font.color.rgb = C_LIGHT
        p2.space_before = Pt(1)

    # -------------------------------------------------------------------------
    # SLIDE 14: 13. ĐÁNH GIÁ & HƯỚNG PHÁT TRIỂN
    # -------------------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "13. ĐÁNH GIÁ & HƯỚNG PHÁT TRIỂN",
               "Tổng Kết Đóng Góp Đề Tài & Lộ Trình Nâng Cấp Công Nghệ",
               "Khẳng định giá trị thực tiễn và định hướng mở rộng hệ sinh thái khảo thí thông minh", "14 / 15")
    add_footer(s14)

    # 2 Comparison Columns
    # Left: Advantages
    c_adv = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.9))
    c_adv.fill.solid()
    c_adv.fill.fore_color.rgb = C_CARD
    c_adv.line.color.rgb = C_GREEN
    c_adv.line.width = Pt(1.5)
    tf_adv = c_adv.text_frame
    tf_adv.margin_left = Inches(0.3)
    tf_adv.margin_top = Inches(0.25)
    p = tf_adv.paragraphs[0]
    p.text = "ƯU ĐIỂM & ĐÓNG GÓP NỔI BẬT"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    advs = [
        ("Chi phí thiết bị 0 VNĐ:", "Tận dụng triệt để máy tính văn phòng và camera điện thoại sẵn có, giảm thiểu chi phí đầu tư hàng trăm triệu cho nhà trường."),
        ("Khắc phục biến thiên ánh sáng:", "Thuật toán Relative Ink Contrast giải quyết dứt điểm vấn đề bóng đổ và tẩy xóa lem mà các bộ lọc nhị phân truyền thống thất bại."),
        ("Quy trình hoàn chỉnh & sẵn sàng thực tế:", "Tích hợp đầy đủ từ nạp đáp án, chấm hàng loạt, giao diện CustomTkinter đến xuất Excel 3-Sheet tự động."),
        ("Chất lượng mã nguồn cao:", "Đạt 100% (27/27) bài kiểm thử Pytest tự động, kiến trúc module hóa phân tầng dễ bảo trì và mở rộng.")
    ]
    for atitle, adesc in advs:
        p1 = tf_adv.add_paragraph()
        p1.text = "✔ " + atitle
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_before = Pt(8)
        p2 = tf_adv.add_paragraph()
        p2.text = adesc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_LIGHT
        p2.space_before = Pt(2)

    # Right: Future roadmap
    c_fut = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.9), Inches(5.6), Inches(4.9))
    c_fut.fill.solid()
    c_fut.fill.fore_color.rgb = C_CARD
    c_fut.line.color.rgb = C_CYAN
    c_fut.line.width = Pt(1.5)
    tf_fut = c_fut.text_frame
    tf_fut.margin_left = Inches(0.3)
    tf_fut.margin_top = Inches(0.25)
    p = tf_fut.paragraphs[0]
    p.text = "HẠN CHẾ & HƯỚNG PHÁT TRIỂN TƯƠNG LAI"
    p.font.name = FONT_TITLE
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    futs = [
        ("Tích hợp AI Deep Learning (YOLOv8 / MobileNet):", "Huấn luyện mạng nơ-ron nhận diện góc phiếu thi ngay cả khi giấy bị nhàu nát, quăn mép hoặc rách mất 1 marker định vị."),
        ("Mở rộng OCR Chữ viết tay (Handwriting Recognition):", "Tự động nhận diện Họ và tên, Lớp học, Số CMND và Chữ ký thí sinh bằng các mô hình Transformer / CRNN."),
        ("Phát triển Ứng dụng Di động (Mobile App):", "Xây dựng ứng dụng Flutter / Android / iOS để giáo viên quét và chấm điểm trực tiếp tại phòng thi bằng camera thời gian thực."),
        ("Điện toán đám mây & Đồng bộ cơ sở dữ liệu:", "Đồng bộ điểm thi tự động lên hệ thống Quản lý Giáo dục (VnEdu, SMAS) và gửi điểm cho phụ huynh qua SMS/Zalo.")
    ]
    for ftitle, fdesc in futs:
        p1 = tf_fut.add_paragraph()
        p1.text = "➔ " + ftitle
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = C_CYAN
        p1.space_before = Pt(8)
        p2 = tf_fut.add_paragraph()
        p2.text = fdesc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_LIGHT
        p2.space_before = Pt(2)

    # -------------------------------------------------------------------------
    # SLIDE 15: KẾT LUẬN & LỜI CẢM ƠN (Q&A / CLOSING)
    # -------------------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)

    # Glowing Cyan Accent Line
    line15 = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(0.06), Inches(2.2))
    line15.fill.solid()
    line15.fill.fore_color.rgb = C_CYAN
    line15.line.fill.background()

    # Top Pill Tag
    tag_box15 = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(1.3), Inches(4.2), Inches(0.35))
    tag_box15.fill.solid()
    tag_box15.fill.fore_color.rgb = C_CYAN_BG
    tag_box15.line.color.rgb = C_CYAN
    tag_box15.line.width = Pt(1)
    tf15 = tag_box15.text_frame
    p15 = tf15.paragraphs[0]
    p15.text = "HOÀN THÀNH BÁO CÁO ĐỒ ÁN HỌC PHẦN"
    p15.font.name = FONT_TITLE
    p15.font.size = Pt(11)
    p15.font.bold = True
    p15.font.color.rgb = C_CYAN

    # Title
    t_box15 = s15.shapes.add_textbox(Inches(1.05), Inches(1.8), Inches(11.2), Inches(1.0))
    tf_t15 = t_box15.text_frame
    p_t15 = tf_t15.paragraphs[0]
    p_t15.text = "XIN TRÂN TRỌNG CẢM ƠN!"
    p_t15.font.name = FONT_TITLE
    p_t15.font.size = Pt(36)
    p_t15.font.bold = True
    p_t15.font.color.rgb = C_WHITE

    # Subtitle
    sub_box15 = s15.shapes.add_textbox(Inches(1.05), Inches(2.8), Inches(11.2), Inches(0.5))
    tf_s15 = sub_box15.text_frame
    p_s15 = tf_s15.paragraphs[0]
    p_s15.text = "Kính chúc Quý Thầy Cô trong Hội đồng chấm thi sức khỏe, hạnh phúc và thành công!"
    p_s15.font.name = FONT_TITLE
    p_s15.font.size = Pt(14)
    p_s15.font.color.rgb = C_CYAN

    # Gratitude Card (Bottom Left)
    g_card = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(3.7), Inches(5.3), Inches(2.8))
    g_card.fill.solid()
    g_card.fill.fore_color.rgb = C_CARD
    g_card.line.color.rgb = C_BORDER
    g_card.line.width = Pt(1)
    gtf = g_card.text_frame
    gtf.margin_left = Inches(0.3)
    gtf.margin_top = Inches(0.25)
    gp = gtf.paragraphs[0]
    gp.text = "LỜI TRI ÂN SÂU SẮC"
    gp.font.name = FONT_TITLE
    gp.font.size = Pt(12)
    gp.font.bold = True
    gp.font.color.rgb = C_CYAN

    gtxt = [
        ("Giảng viên hướng dẫn:", "ThS. Nguyễn Thị Minh Tâm"),
        ("Lời cảm ơn:", "Nhóm sinh viên xin bày tỏ lòng biết ơn sâu sắc đến Cô đã tận tình hướng dẫn, định hướng thuật toán và đóng góp những ý kiến quý báu trong suốt quá trình nghiên cứu và hoàn thiện đề tài."),
        ("Đơn vị đào tạo:", "Viện Kỹ thuật và Công nghệ — Trường Đại học Vinh")
    ]
    for gtitle, gdesc in gtxt:
        p1 = gtf.add_paragraph()
        p1.text = gtitle
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.space_before = Pt(5)
        p2 = gtf.add_paragraph()
        p2.text = gdesc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_LIGHT
        p2.space_before = Pt(1)

    # Q&A Card (Bottom Right)
    qa_card = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(3.7), Inches(5.4), Inches(2.8))
    qa_card.fill.solid()
    qa_card.fill.fore_color.rgb = C_CARD_ALT
    qa_card.line.color.rgb = C_CYAN
    qa_card.line.width = Pt(1.5)
    qtf = qa_card.text_frame
    qtf.margin_left = Inches(0.3)
    qtf.margin_top = Inches(0.25)
    qp = qtf.paragraphs[0]
    qp.text = "PHIÊN HỎI ĐÁP & TRAO ĐỔI (Q&A SESSION)"
    qp.font.name = FONT_TITLE
    qp.font.size = Pt(12)
    qp.font.bold = True
    qp.font.color.rgb = C_CYAN

    q_points = [
        "Nhóm tác giả sẵn sàng lắng nghe và giải đáp mọi câu hỏi, phản biện từ Hội đồng.",
        "Sẵn sàng trình diễn Demo trực tiếp phần mềm trên máy tính với ảnh chụp thực tế.",
        "Mã nguồn đề tài & Báo cáo kỹ thuật đầy đủ được lưu trữ tại Repository của nhóm.",
        "Thành viên nhóm:\n• Hồ Tuấn Hiệp (Trưởng nhóm)  • Nguyễn Khắc Quốc Khánh\n• Lê Viết Quân               • Nguyễn Văn Thành"
    ]
    for q in q_points:
        p = qtf.add_paragraph()
        p.text = "• " + q
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_WHITE
        p.space_before = Pt(6)

    # Output file path
    output_pptx = sys.argv[1] if len(sys.argv) > 1 else "Slide_Bao_Cao_TGMT_ChamTracNghiem.pptx"
    prs.save(output_pptx)
    print(f"SUCCESS: Saved presentation to {output_pptx} with {len(prs.slides)} slides.")

if __name__ == "__main__":
    create_presentation()

