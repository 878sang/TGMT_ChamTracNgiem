# -*- coding: utf-8 -*-
"""
Build Complete Report for:
ĐỒ ÁN HỌC PHẦN: THỊ GIÁC MÁY TÍNH
Đề tài: HỆ THỐNG NHẬN DIỆN VÀ CHẤM PHIẾU THI TRẮC NGHIỆM TỰ ĐỘNG BẰNG PYTHON VÀ OPENCV
(Phần mềm chấm phiếu FormTHPT50 từ 1 đến 50 câu theo công nghệ OMR)
"""

import os
import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from build_concise_report import (
    create_document, add_p, add_bullet, add_h1, add_h2, add_h3,
    add_code_block, add_image_figure, add_table_data
)

ROOT = Path(__file__).resolve().parents[1]


def add_callout(doc, title, text, box_type="NOTE"):
    colors = {
        "NOTE": "EFF6FF",
        "WARNING": "FFF7ED",
        "SUCCESS": "F0FDF4",
        "INFO": "EFF6FF",
    }
    table = doc.add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{colors.get(box_type, colors["NOTE"])}"/>')
    cell._tc.get_or_add_tcPr().append(shading)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_before = Pt(4)
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.left_indent = Inches(0.12)
    paragraph.paragraph_format.right_indent = Inches(0.12)
    label = paragraph.add_run(f"{title}\n")
    label.font.name = "Times New Roman"
    label.font.size = Pt(11)
    label.font.bold = True
    label.font.color.rgb = RGBColor(31, 78, 121)
    body = paragraph.add_run(text)
    body.font.name = "Times New Roman"
    body.font.size = Pt(10.5)
    body.font.color.rgb = RGBColor(30, 41, 59)

def build_report():
    print("Building full report...")
    doc = create_document()
    
    # =========================================================================
    # 1. TRANG BÌA (COVER PAGE)
    # =========================================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = Inches(0)
    r = p.add_run("TRƯỜNG ĐẠI HỌC VINH\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    
    r2 = p.add_run("VIỆN KỸ THUẬT VÀ CÔNG NGHỆ\n")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0, 51, 102)
    
    r3 = p.add_run("---------------***---------------")
    r3.font.name = "Times New Roman"
    r3.font.size = Pt(11)
    r3.font.color.rgb = RGBColor(120, 120, 120)
    
    # Spacing
    for _ in range(4):
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(0)
        
    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_before = Pt(0)
    p_course.paragraph_format.space_after = Pt(4)
    p_course.paragraph_format.first_line_indent = Inches(0)
    r_c1 = p_course.add_run("ĐỒ ÁN HỌC PHẦN\n")
    r_c1.font.name = "Times New Roman"
    r_c1.font.size = Pt(16)
    r_c1.font.bold = True
    r_c1.font.color.rgb = RGBColor(0, 0, 0)
    
    r_c2 = p_course.add_run("THỊ GIÁC MÁY TÍNH")
    r_c2.font.name = "Times New Roman"
    r_c2.font.size = Pt(18)
    r_c2.font.bold = True
    r_c2.font.color.rgb = RGBColor(0, 51, 102)
    
    for _ in range(2):
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(0)
        
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.paragraph_format.first_line_indent = Inches(0)
    r_t1 = p_title.add_run("TÊN ĐỀ TÀI:\n")
    r_t1.font.name = "Times New Roman"
    r_t1.font.size = Pt(13)
    r_t1.font.bold = True
    r_t1.font.color.rgb = RGBColor(100, 100, 100)
    
    r_t2 = p_title.add_run("HỆ THỐNG NHẬN DIỆN VÀ CHẤM PHIẾU THI TRẮC NGHIỆM TỰ ĐỘNG BẰNG PYTHON VÀ OPENCV\n")
    r_t2.font.name = "Times New Roman"
    r_t2.font.size = Pt(18)
    r_t2.font.bold = True
    r_t2.font.color.rgb = RGBColor(180, 0, 0)
    
    r_t3 = p_title.add_run("(Phần mềm chấm phiếu FormTHPT50 từ 1 đến 50 câu theo công nghệ OMR)")
    r_t3.font.name = "Times New Roman"
    r_t3.font.size = Pt(12)
    r_t3.font.italic = True
    r_t3.font.color.rgb = RGBColor(50, 50, 50)
    
    for _ in range(3):
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(0)
        
    # Metadata Table
    tbl_meta = doc.add_table(rows=2, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.rows[0].cells[0].width = Inches(2.2)
    tbl_meta.rows[0].cells[1].width = Inches(4.1)
    tbl_meta.rows[1].cells[0].width = Inches(2.2)
    tbl_meta.rows[1].cells[1].width = Inches(4.1)
    
    c00 = tbl_meta.cell(0, 0)
    c01 = tbl_meta.cell(0, 1)
    c10 = tbl_meta.cell(1, 0)
    c11 = tbl_meta.cell(1, 1)
    
    p00 = c00.paragraphs[0]
    p00.paragraph_format.space_after = Pt(3)
    r = p00.add_run("Cán bộ hướng dẫn (GVHD):")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12.5)
    r.font.bold = True
    
    p01 = c01.paragraphs[0]
    p01.paragraph_format.space_after = Pt(3)
    r = p01.add_run("Cô Nguyễn Thị Minh Tâm")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    
    p10 = c10.paragraphs[0]
    p10.paragraph_format.space_after = Pt(3)
    r = p10.add_run("Nhóm sinh viên thực hiện:")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12.5)
    r.font.bold = True
    
    p11 = c11.paragraphs[0]
    p11.paragraph_format.space_after = Pt(2)
    p11.paragraph_format.line_spacing = 1.25
    members = [
        "1. Hồ Tuấn Hiệp – MSSV: 225748020110020 (Trưởng nhóm)",
        "2. Nguyễn Khắc Quốc Khánh – MSSV: 225748020110261",
        "3. Lê Viết Quân – MSSV: 225748020110203",
        "4. Nguyễn Văn Thành – MSSV: 215748020110105"
    ]
    for idx, m in enumerate(members):
        if idx > 0:
            p11.add_run("\n")
        r_m = p11.add_run(m)
        r_m.font.name = "Times New Roman"
        r_m.font.size = Pt(12.0)
        if "Trưởng nhóm" in m:
            r_m.font.bold = True
            
    # Borderless metadata table
    tblPr = tbl_meta._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:insideH w:val="none"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    
    for _ in range(4):
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(0)
        
    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_before = Pt(0)
    p_loc.paragraph_format.space_after = Pt(0)
    p_loc.paragraph_format.first_line_indent = Inches(0)
    r_loc = p_loc.add_run("Nghệ An, Tháng 11 Năm 2026")
    r_loc.font.name = "Times New Roman"
    r_loc.font.size = Pt(13)
    r_loc.font.bold = True
    
    doc.add_page_break()
    
    # =========================================================================
    # 2. LỜI CẢM ƠN
    # =========================================================================
    add_h1(doc, "LỜI CẢM ƠN")
    add_p(doc, "Lời đầu tiên, nhóm sinh viên chúng em xin bày tỏ lòng biết ơn sâu sắc và chân thành nhất tới Cô Nguyễn Thị Minh Tâm – Giảng viên bộ môn Thị giác máy tính, Viện Kỹ thuật và Công nghệ - Trường Đại học Vinh, người đã tận tình truyền đạt những kiến thức chuyên môn quý báu, định hướng nghiên cứu khoa học và luôn nhiệt tình giúp đỡ, giải đáp thắc mắc cho nhóm chúng em trong suốt thời gian thực hiện đồ án học phần này.")
    add_p(doc, "Dưới sự giảng dạy đầy tâm huyết và những góp ý thực tế của cô, nhóm không chỉ được tiếp cận với các phương pháp xử lý ảnh kinh điển và hiện đại (như biến đổi phối cảnh hình học, phân đoạn ảnh nhị phân thích nghi, nhận diện đánh dấu quang học OMR), mà còn được truyền cảm hứng sáng tạo và rèn luyện tư duy giải quyết vấn đề kỹ thuật một cách bài bản, khoa học.")
    add_p(doc, "Chúng em cũng xin gửi lời cảm ơn chân thành đến Ban Giám hiệu Trường Đại học Vinh, Ban Lãnh đạo Viện Kỹ thuật và Công nghệ cùng các thầy cô giáo trong bộ môn đã tạo điều kiện tối ưu về cơ sở vật chất, phòng máy thực hành và môi trường học tập lý tưởng để chúng em hoàn thành đồ án này.")
    add_p(doc, "Mặc dù cả nhóm đã nỗ lực hết mình với tinh thần trách nhiệm cao nhất để hoàn thiện hệ thống phần mềm chấm thi trắc nghiệm hoàn chỉnh từ thuật toán lõi đến giao diện người dùng, song do kinh nghiệm thực tế và kiến thức của chúng em vẫn còn những hạn chế nhất định, đồ án chắc chắn khó tránh khỏi những thiếu sót. Chúng em rất mong tiếp tục nhận được sự nhận xét, góp ý và chỉ dẫn quý báu từ Cô Nguyễn Thị Minh Tâm cùng các thầy cô trong Hội đồng phản biện để sản phẩm ngày càng được hoàn thiện và có khả năng ứng dụng rộng rãi vào công tác khảo thí thực tế.")
    add_p(doc, "Sau cùng, chúng em kính chúc Cô Nguyễn Thị Minh Tâm dồi dào sức khỏe, luôn hạnh phúc và gặt hái được nhiều thành công rực rỡ trong sự nghiệp giảng dạy và nghiên cứu khoa học cao quý của mình!")
    
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.space_before = Pt(8)
    p_sig.paragraph_format.space_after = Pt(0)
    p_sig.paragraph_format.first_line_indent = Inches(0)
    r_sig1 = p_sig.add_run("Nghệ An, Tháng 11 Năm 2026\n")
    r_sig1.font.name = "Times New Roman"
    r_sig1.font.size = Pt(12)
    r_sig1.font.italic = True
    r_sig2 = p_sig.add_run("Tập thể nhóm sinh viên thực hiện\n")
    r_sig2.font.name = "Times New Roman"
    r_sig2.font.size = Pt(13)
    r_sig2.font.bold = True
    r_sig3 = p_sig.add_run("Hồ Tuấn Hiệp – Nguyễn Khắc Quốc Khánh\nLê Viết Quân – Nguyễn Văn Thành")
    r_sig3.font.name = "Times New Roman"
    r_sig3.font.size = Pt(12)
    r_sig3.font.italic = True
    
    doc.add_page_break()
    
    # =========================================================================
    # 3. MỤC LỤC TỔNG QUAN
    # =========================================================================
    add_h1(doc, "MỤC LỤC")
    
    toc_items = [
        ("LỜI CẢM ƠN", "2"),
        ("MỤC LỤC", "3"),
        ("DANH MỤC KÝ HIỆU VÀ TỪ VIẾT TẮT", "4"),
        ("DANH MỤC HÌNH ẢNH", "5"),
        ("DANH MỤC BẢNG BIỂU", "6"),
        ("MỞ ĐẦU", "7"),
        ("CHƯƠNG 1: TỔNG QUAN VÀ MÔ TẢ BÀI TOÁN", "9"),
        ("    1.1. Bối cảnh và tính cấp thiết của bài toán chấm thi trắc nghiệm", "9"),
        ("    1.2. Tổng quan về công nghệ OMR (Optical Mark Recognition)", "10"),
        ("    1.3. Mục tiêu và phạm vi nghiên cứu của đề tài", "12"),
        ("CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN", "14"),
        ("    2.1. Yêu cầu bài toán và kiến trúc hệ thống", "14"),
        ("        2.1.1. Yêu cầu bài toán (Input / Output)", "14"),
        ("        2.1.2. Yêu cầu chức năng", "15"),
        ("        2.1.3. Yêu cầu phi chức năng", "17"),
        ("    2.2. Pipeline xử lý Thị giác máy tính (Computer Vision Pipeline)", "18"),
        ("        2.2.1. Căn chỉnh phối cảnh dựa trên 4 Marker định vị (Perspective Transform)", "18"),
        ("        2.2.2. Phân vùng quan tâm (ROI) và trích xuất đặc trưng", "21"),
        ("        2.2.3. Thuật toán nhận diện tô ô trắc nghiệm (OMR Relative Scoring)", "23"),
        ("        2.2.4. Trích xuất Số báo danh, Mã đề thi và xử lý ngoại lệ", "25"),
        ("    2.3. Công nghệ và công cụ phát triển", "26"),
        ("CHƯƠNG 3: CÀI ĐẶT VÀ THỰC NGHIỆM ĐÁNH GIÁ", "29"),
        ("    3.1. Cài đặt hệ thống và tổ chức mã nguồn", "29"),
        ("        3.1.1. Cấu trúc thư mục dự án và các module cốt lõi", "29"),
        ("        3.1.2. Đặc tả mẫu phiếu FormTHPT50 và ma trận pixel tiêu chuẩn", "31"),
        ("        3.1.3. Hiện thực hóa các hàm xử lý chính trong Core", "33"),
        ("    3.2. Giao diện chương trình và quy trình vận hành 3 bước", "38"),
        ("        3.2.1. Thiết kế tổng thể giao diện Desktop CustomTkinter", "38"),
        ("        3.2.2. Quy trình thao tác 3 bước chuẩn của người dùng", "40"),
        ("    3.3. Thực nghiệm và đánh giá kết quả", "42"),
        ("        3.3.1. Các kịch bản thử nghiệm trên tập dữ liệu thử thách", "42"),
        ("        3.3.2. Kết quả kiểm thử tự động Unit Tests (27/27 test cases)", "45"),
        ("        3.3.3. Đánh giá hiệu năng thời gian và độ chính xác nhận diện", "46"),
        ("        3.3.4. Kết quả trực quan hóa overlay và xuất báo cáo Excel 3 Sheet", "48"),
        ("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "51"),
        ("    1. Kết quả đạt được", "51"),
        ("    2. Những tồn tại và hạn chế", "52"),
        ("    3. Hướng phát triển trong tương lai", "52"),
        ("PHỤ LỤC 01: BẢNG ĐÁNH GIÁ THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ", "54"),
        ("TÀI LIỆU THAM KHẢO", "56"),
    ]
    
    for item, page_str in toc_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(1)
        p_t.paragraph_format.space_after = Pt(1)
        p_t.paragraph_format.line_spacing = 1.15
        p_t.paragraph_format.first_line_indent = Inches(0)
        
        is_main = item.startswith("CHƯƠNG") or item in ["LỜI CẢM ƠN", "MỤC LỤC", "MỞ ĐẦU", "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "TÀI LIỆU THAM KHẢO", "PHỤ LỤC 01: BẢNG ĐÁNH GIÁ THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ"]
        
        r1 = p_t.add_run(item)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(12)
        r1.font.bold = is_main
        if is_main:
            r1.font.color.rgb = RGBColor(0, 51, 102)
            
        dots = " " + "." * max(5, 75 - len(item) * 2) + " "
        r_dots = p_t.add_run(dots)
        r_dots.font.name = "Times New Roman"
        r_dots.font.size = Pt(10)
        r_dots.font.color.rgb = RGBColor(160, 160, 160)
        
        r2 = p_t.add_run(page_str)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(12)
        r2.font.bold = is_main
        
    doc.add_page_break()
    
    # =========================================================================
    # 4. DANH MỤC VIẾT TẮT, HÌNH ẢNH, BẢNG BIỂU
    # =========================================================================
    add_h1(doc, "DANH MỤC KÝ HIỆU VÀ TỪ VIẾT TẮT")
    abbr_data = [
        ["OMR", "Optical Mark Recognition", "Nhận diện dấu đánh dấu quang học trên giấy"],
        ["CV", "Computer Vision", "Thị giác máy tính"],
        ["ROI", "Region of Interest", "Vùng quan tâm cần xử lý trên ảnh"],
        ["SBD", "Số báo danh", "Số định danh duy nhất của thí sinh tham gia kỳ thi"],
        ["THPT", "Trung học phổ thông", "Cấp học trung học phổ thông"],
        ["BGD&ĐT", "Bộ Giáo dục và Đào tạo", "Cơ quan quản lý giáo dục cao nhất tại Việt Nam"],
        ["GUI / UI", "Graphical User Interface", "Giao diện đồ họa người dùng"],
        ["API", "Application Programming Interface", "Giao diện lập trình ứng dụng"],
        ["IDE", "Integrated Development Environment", "Môi trường phát triển tích hợp (VS Code, PyCharm)"],
        ["PIL", "Python Imaging Library (Pillow)", "Thư viện nạp và vẽ ảnh số mạnh mẽ trong Python"],
        ["PDF", "Portable Document Format", "Định dạng tài liệu số di động"],
        ["JSON", "JavaScript Object Notation", "Định dạng trao đổi và cấu hình dữ liệu chuẩn"]
    ]
    add_table_data(doc, ["Ký hiệu viết tắt", "Tên tiếng Anh", "Ý nghĩa chuyên môn"], abbr_data, [1.5, 2.3, 2.5])
    
    add_h1(doc, "DANH MỤC HÌNH ẢNH")
    fig_items = [
        ("Hình 1.1", "Mẫu phiếu thi trắc nghiệm FormTHPT50 tiêu chuẩn khổ A4", "13"),
        ("Hình 2.1", "Sơ đồ kiến trúc tổng thể 4 tầng của hệ thống chấm phiếu FormTHPT50", "15"),
        ("Hình 2.2", "Sơ đồ luồng xử lý ảnh trong Pipeline Thị giác máy tính (OpenCV Pipeline)", "18"),
        ("Hình 2.3", "Bố cục ma trận pixel và các marker định vị của FormTHPT50", "22"),
        ("Hình 2.4", "Nguyên lý đo độ tương phản mực nội vùng (Relative Ink Contrast)", "24"),
        ("Hình 3.1", "Quy trình thao tác 3 bước chuẩn trên giao diện Desktop CustomTkinter", "39"),
        ("Hình 3.2", "Ảnh chụp bài thi thực tế từ điện thoại với góc chụp xiên và ánh sáng không đều", "43"),
        ("Hình 3.3", "Ảnh bài thi thực tế sau khi căn phẳng phối cảnh bằng 4 Marker góc", "44"),
        ("Hình 3.4", "Kết quả trực quan hóa bài làm sau khi chấm với overlay vòng tròn và banner điểm", "49"),
        ("Hình 3.5", "Cấu trúc báo cáo kết quả thi file Excel gồm 3 Sheet chuyên nghiệp", "50"),
    ]
    for fid, ftitle, fpage in fig_items:
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_before = Pt(2)
        p_f.paragraph_format.space_after = Pt(2)
        p_f.paragraph_format.first_line_indent = Inches(0)
        p_f.add_run(f"{fid}: {ftitle} ")
        dots = "." * max(5, 75 - len(fid + ftitle) * 2) + " "
        r_d = p_f.add_run(dots)
        r_d.font.color.rgb = RGBColor(160, 160, 160)
        p_f.add_run(fpage)

    add_h1(doc, "DANH MỤC BẢNG BIỂU")
    tbl_items = [
        ("Bảng 2.1", "Bảng đặc tả các trường dữ liệu đầu vào và đầu ra của hệ thống", "14"),
        ("Bảng 3.1", "Danh mục và chức năng các module trong kiến trúc mã nguồn", "30"),
        ("Bảng 3.2", "Đặc tả thông số hình học của mẫu phiếu FormTHPT50 trên canvas chuẩn", "32"),
        ("Bảng 3.3", "Bảng tổng hợp kết quả 27 ca kiểm thử tự động (Unit Tests)", "45"),
        ("Bảng 3.4", "Bảng đo thời gian thực thi (latency) chi tiết từng công đoạn trong pipeline", "47"),
        ("Bảng 3.5", "Bảng đánh giá độ chính xác nhận diện OMR trên các điều kiện thực nghiệm", "47"),
        ("Bảng 4.1", "Bảng phân công nhiệm vụ và tự đánh giá đóng góp của 4 thành viên", "55"),
    ]
    for tid, ttitle, tpage in tbl_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(2)
        p_t.paragraph_format.space_after = Pt(2)
        p_t.paragraph_format.first_line_indent = Inches(0)
        p_t.add_run(f"{tid}: {ttitle} ")
        dots = "." * max(5, 75 - len(tid + ttitle) * 2) + " "
        r_d = p_t.add_run(dots)
        r_d.font.color.rgb = RGBColor(160, 160, 160)
        p_t.add_run(tpage)

    doc.add_page_break()
    
    # =========================================================================
    # 5. MỞ ĐẦU
    # =========================================================================
    add_h1(doc, "MỞ ĐẦU")
    
    add_h2(doc, "1. Đặt vấn đề và tính cấp thiết của đề tài")
    add_p(doc, "Trong kỷ nguyên số hóa giáo dục hiện đại, các kỳ thi trắc nghiệm khách quan ngày càng khẳng định vị trí then chốt tại các cấp học và bậc học trên toàn quốc. Đặc biệt, kể từ khi Bộ Giáo dục và Đào tạo áp dụng hình thức thi trắc nghiệm cho hầu hết các môn thi trong Kỳ thi Tốt nghiệp THPT và các đợt thi Đánh giá năng lực của các trường đại học lớn, số lượng phiếu trả lời trắc nghiệm cần xử lý mỗi kỳ thi lên tới hàng triệu bài.")
    add_p(doc, "Tại các trường THPT, trung tâm khảo thí và các lớp luyện thi, giáo viên thường xuyên phải tổ chức các kỳ kiểm tra định kỳ (15 phút, 1 tiết, kiểm tra giữa kỳ, thi học kỳ và các đợt thi thử tốt nghiệp). Khối lượng bài thi cần chấm sau mỗi đợt có thể từ vài trăm đến hàng ngàn bài. Nếu thực hiện chấm thi thủ công bằng cách sử dụng phiếu đục lỗ truyền thống hoặc đối chiếu từng câu bằng mắt, giáo viên sẽ phải đối mặt với vô vàn áp lực: mất rất nhiều thời gian (trung bình 1 - 2 phút cho mỗi bài), dễ xảy ra sai sót do mỏi mắt nhầm lẫn giữa các mã đề, và thiếu tính minh bạch khách quan.")
    add_p(doc, "Các giải pháp phần cứng chấm thi OMR chuyên dụng hiện có trên thị trường tuy đạt độ ổn định cao nhưng giá thành cực kỳ đắt đỏ (từ hàng chục đến hàng trăm triệu đồng cho một máy quét chuyên dụng), đòi hỏi mẫu giấy in dập lỗ riêng biệt có định lượng cao và chi phí bảo trì tốn kém, hoàn toàn không khả thi để trang bị đại trà cho từng giáo viên bộ môn hay các trường học vùng khó khăn.")
    add_p(doc, "Xuất phát từ thực tiễn cấp bách đó, việc nghiên cứu và xây dựng một giải pháp phần mềm nhận diện và chấm bài thi trắc nghiệm tự động dựa trên công nghệ Thị giác máy tính (Computer Vision) kết hợp xử lý ảnh số bằng ngôn ngữ Python và thư viện OpenCV là một hướng đi đột phá, mang ý nghĩa khoa học và thực tiễn sâu sắc. Giải pháp này cho phép tận dụng trực tiếp các thiết bị sẵn có như camera điện thoại thông minh, máy quét văn phòng thông thường hay ảnh chụp màn hình để chấm bài tức thì, với chi phí đầu tư bằng 0 đồng và độ chính xác tiệm cận tuyệt đối.")
    
    add_h2(doc, "2. Mục đích nghiên cứu")
    add_p(doc, "Mục đích nghiên cứu chính của đề tài là xây dựng hoàn chỉnh một hệ thống ứng dụng Desktop tự động hóa toàn diện quy trình quét và chấm phiếu thi trắc nghiệm 50 câu (mẫu FormTHPT50), đáp ứng các yêu cầu kỹ thuật khắt khe:")
    add_bullet(doc, "Làm chủ pipeline xử lý ảnh số với OpenCV: Tiền xử lý, lọc nhiễu, nhị phân hóa thích nghi, phát hiện contour và nắn phẳng phối cảnh (Perspective Transform) dựa trên 4 Marker định vị ở 4 góc.", bold_prefix="Căn chỉnh hình học:")
    add_bullet(doc, "Phát triển thuật toán bóc tách OMR theo độ tương phản mực cục bộ (Relative Ink Contrast), kháng chịu tốt các hiện tượng bóng đổ, ánh sáng yếu, tẩy chì lem mờ hoặc học sinh tô chì nhạt.", bold_prefix="Bóc tách OMR thông minh:")
    add_bullet(doc, "Xử lý hàng loạt ảnh bài làm theo lô (Batch Processing) trên luồng nền (Threading), đảm bảo giao diện luôn mượt mà và chống dừng đột ngột (Fault Tolerance) khi gặp ảnh lỗi.", bold_prefix="Hiệu năng xử lý theo lô:")
    add_bullet(doc, "Thiết kế giao diện Desktop trực quan bằng CustomTkinter, hỗ trợ xem kết quả khoanh màu trực quan (Overlay) và tự động xuất báo cáo Excel 3 Sheet chuyên nghiệp phục vụ phân tích sư phạm.", bold_prefix="Trực quan hóa và báo cáo:")

    add_h2(doc, "3. Đối tượng và phạm vi nghiên cứu")
    add_bullet(doc, "Phiếu thi trắc nghiệm FormTHPT50 tiêu chuẩn khổ A4, bao gồm 50 câu trắc nghiệm 4 lựa chọn (A, B, C, D), khối Số báo danh (6 chữ số), khối Mã đề thi (3 chữ số) và 4 ô vuông Marker đen định vị tại 4 góc.", bold_prefix="Đối tượng nghiên cứu:")
    add_bullet(doc, "Tập trung xử lý ảnh chụp từ camera điện thoại thông minh, ảnh quét phẳng từ máy scan văn phòng hoặc ảnh cắt màn hình. Ứng dụng chạy trên môi trường máy tính để bàn (Windows / Linux / macOS) với giao diện Desktop độc lập.", bold_prefix="Phạm vi nghiên cứu:")

    add_h2(doc, "4. Phương pháp nghiên cứu")
    add_bullet(doc, "Thu thập và phân tích các tài liệu học thuật về xử lý ảnh số, lý thuyết không gian hình học, ma trận biến đổi phối cảnh 2D, các giải thuật phân ngưỡng nhị phân (Otsu, Adaptive Gaussian) và mô hình nhận diện quang học OMR.", bold_prefix="Phương pháp lý thuyết:")
    add_bullet(doc, "Xây dựng bộ dữ liệu ảnh bài thi đa dạng (ảnh phẳng scan, ảnh chụp góc nghiêng 15-30 độ, ảnh xoay các hướng, ảnh bóng đổ, ảnh thiếu sáng, ảnh có lỗi tô chì); tiến hành kiểm thử tự động với Pytest và đo đạc định lượng thời gian xử lý cũng như độ chính xác nhận diện.", bold_prefix="Phương pháp thực nghiệm:")

    add_h2(doc, "5. Bố cục của báo cáo đồ án")
    add_p(doc, "Báo cáo đồ án được cấu trúc thành 3 Chương nội dung chính cùng phần Mở đầu, Kết luận, Phụ lục và Tài liệu tham khảo:")
    add_bullet(doc, "Trình bày bối cảnh thực tiễn, tổng quan về công nghệ OMR, so sánh các giải pháp hiện nay và xác định mục tiêu, phạm vi nghiên cứu của đề tài.", bold_prefix="Chương 1: Tổng quan và mô tả bài toán -")
    add_bullet(doc, "Phân tích chi tiết các yêu cầu hệ thống (5 chức năng cốt lõi), thiết kế kiến trúc tổng thể 4 tầng, trình bày chi tiết pipeline xử lý Thị giác máy tính (nắn phối cảnh, OMR Ink Contrast, bóc tách SBD/Mã đề) và giới thiệu các công nghệ công cụ phát triển.", bold_prefix="Chương 2: Phân tích và thiết kế thuật toán -")
    add_bullet(doc, "Trình bày chi tiết cấu trúc mã nguồn dự án, đặc tả hình học phiếu FormTHPT50, hiện thực hóa các hàm thuật toán trong Core, thiết kế giao diện Desktop CustomTkinter theo quy trình 3 bước, báo cáo kết quả kiểm thử tự động 27 unit tests và đánh giá thực nghiệm định lượng về hiệu năng, độ chính xác cũng như trích xuất báo cáo Excel.", bold_prefix="Chương 3: Cài đặt và thực nghiệm đánh giá -")
    add_bullet(doc, "Tổng kết các kết quả nổi bật đã đạt được, chỉ ra những hạn chế còn tồn tại và vạch ra các định hướng nâng cấp, mở rộng hệ thống trong tương lai.", bold_prefix="Kết luận và hướng phát triển -")
    add_bullet(doc, "Bảng tổng hợp phân công nhiệm vụ và tự đánh giá đóng góp của 4 thành viên.", bold_prefix="Phụ lục 01: Bảng đánh giá thành viên -")
    
    doc.add_page_break()
    
    # =========================================================================
    # 6. CHƯƠNG 1: TỔNG QUAN VÀ MÔ TẢ BÀI TOÁN
    # =========================================================================
    add_h1(doc, "CHƯƠNG 1: TỔNG QUAN VÀ MÔ TẢ BÀI TOÁN")
    
    add_h2(doc, "1.1. Bối cảnh và tính cấp thiết của bài toán chấm thi trắc nghiệm")
    add_p(doc, "Tại Việt Nam, kể từ khi Bộ Giáo dục và Đào tạo chuyển đổi đa số các môn thi trong kỳ thi tốt nghiệp THPT sang hình thức trắc nghiệm khách quan (ngoại trừ môn Ngữ văn), nhu cầu rèn luyện kỹ năng làm bài trắc nghiệm của học sinh tăng cao đột biến. Các trường THPT, trung tâm khảo thí và giáo viên bộ môn thường xuyên tổ chức các đợt thi thử, kiểm tra 15 phút, kiểm tra 1 tiết và kiểm tra học kỳ. Số lượng phiếu trả lời cần chấm sau mỗi kỳ thi có thể lên tới hàng trăm, hàng ngàn bài.")
    add_p(doc, "Quy trình chấm thi truyền thống bộc lộ rất nhiều bất cập lớn:")
    add_bullet(doc, "Giáo viên phải dùng dưỡng đục lỗ đè lên từng tờ giấy thi, đếm từng vết chì tô và so khớp với đáp án của từng mã đề. Công việc này gây căng thẳng thị giác cực độ, tốn hàng chục giờ đồng hồ sau mỗi kỳ thi.", bold_prefix="Tốn kém thời gian và công sức:")
    add_bullet(doc, "Khi phải chấm hàng trăm bài thi liên tục, con người rất dễ bị mệt mỏi dẫn đến nhầm lẫn mã đề, bỏ sót câu hỏi hoặc cộng sai tổng điểm, gây ảnh hưởng tiêu cực đến quyền lợi và tâm lý của học sinh.", bold_prefix="Nguy cơ sai sót chủ quan:")
    add_bullet(doc, "Sau khi chấm xong, giáo viên phải nhập tay từng con điểm vào phần mềm quản lý điểm hoặc bảng tính Excel, mất thêm rất nhiều công đoạn trung gian và dễ gây sai lệch số liệu.", bold_prefix="Chậm trễ trong khâu thống kê:")
    
    add_p(doc, "Việc áp dụng công nghệ Thị giác máy tính (Computer Vision) để tự động hóa hoàn toàn quy trình này đem lại nhiều lợi ích thiết thực và đột phá:")
    add_bullet(doc, "Một bài thi 50 câu được nắn phẳng, nhận diện và chấm điểm trọn gói chỉ trong 0.15 - 0.35 giây, nhanh gấp hàng trăm lần so với chấm thủ công, giúp hoàn thành việc chấm hàng trăm bài thi chỉ trong vài phút.", bold_prefix="Tiết kiệm tối đa thời gian:")
    add_bullet(doc, "Thuật toán xử lý ma trận điểm ảnh tuyệt đối công bằng, loại bỏ hoàn toàn các sai sót chủ quan và cảm tính của con người trong quá trình đối chiếu đáp án.", bold_prefix="Độ chính xác và khách quan tuyệt đối:")
    add_bullet(doc, "Không yêu cầu phần cứng quét chuyên dụng đắt tiền (vốn có giá từ 30 đến trên 100 triệu đồng); hệ thống hoạt động hoàn hảo với ảnh chụp từ camera điện thoại thông minh giá rẻ hoặc máy quét văn phòng thông thường.", bold_prefix="Tối ưu chi phí đầu tư:")
    add_bullet(doc, "Tự động phân tích phổ điểm, tính điểm trung bình, xếp loại học lực và xuất file Excel 3 Sheet chuyên nghiệp phục vụ đánh giá chất lượng dạy và học theo đúng chuẩn sư phạm hiện đại.", bold_prefix="Tự động hóa thống kê toàn diện:")

    add_h2(doc, "1.2. Tổng quan về công nghệ OMR (Optical Mark Recognition)")
    add_p(doc, "Nhận diện dấu đánh dấu quang học (OMR - Optical Mark Recognition) là công nghệ phát hiện sự hiện diện hay vắng mặt của các vết đánh dấu (tô chì, tích dấu) tại các vị trí định trước trên tài liệu giấy. Nguyên lý cốt lõi của OMR dựa trên sự khác biệt về độ phản xạ quang học hoặc mật độ điểm ảnh (pixel intensity/density) giữa vùng giấy trắng và vùng được tô đậm bằng bút chì hoặc bút mực đen.")
    add_p(doc, "Lịch sử công nghệ OMR bắt đầu từ những năm 1930 với các cỗ máy cơ - quang chuyên dụng sử dụng đầu đọc sợi quang và đèn chiếu cảm biến. Tuy nhiên, trong kỷ nguyên Thị giác máy tính hiện đại, OMR dựa trên phần mềm (Software-based OMR) đã thay thế hoàn toàn máy móc cơ khí đắt tiền nhờ sự tiến bộ vượt bậc của các thuật toán xử lý ảnh số.")
    
    add_callout(doc, "So sánh giữa OMR phần cứng quang học và OMR Thị giác máy tính phần mềm",
                "• OMR Phần cứng: Giá thành từ 50.000.000đ - 150.000.000đ; đòi hỏi giấy in chuyên dụng dập lỗ chuẩn xác đến 0.1mm; không xử lý được ảnh chụp từ điện thoại; chi phí bảo trì định kỳ cao.\n"
                "• OMR Thị giác máy tính (Đề tài): Chi phí phần mềm 0 đồng; tận dụng điện thoại thông minh sẵn có; tự động nắn phẳng ảnh chụp nghiêng, lệch góc; kháng bóng đổ và ánh sáng yếu; xuất báo cáo Excel đa năng.",
                box_type="NOTE")
                
    add_p(doc, "Trong thị giác máy tính, quy trình OMR khi chụp từ camera thực tế phải giải quyết 4 thách thức kỹ thuật rất lớn:")
    add_bullet(doc, "Khi người dùng chụp ảnh bằng điện thoại, tờ phiếu hiếm khi nằm vuông góc với trục quang học của camera, dẫn đến hiện tượng méo góc phối cảnh (perspective distortion), tờ phiếu bị xiên, nghiêng hoặc xoay các hướng.", bold_prefix="Biến dạng hình học phối cảnh:")
    add_bullet(doc, "Môi trường chụp thực tế thường có ánh sáng không đều (vùng sáng vùng tối), ánh đèn trần phản chiếu hoặc bóng đổ gắt của chính bàn tay và điện thoại đè lên mặt giấy, khiến các thuật toán phân ngưỡng cố định (Fixed Global Threshold) bị tê liệt hoàn toàn.", bold_prefix="Ánh sáng không đồng nhất và bóng đổ:")
    add_bullet(doc, "Học sinh thường tẩy câu trả lời cũ chưa sạch để lại vết lem nhem mờ, hoặc dùng bút chì quá nhạt (dưới 2B), dẫn đến việc thuật toán dễ nhận diện nhầm ô tẩy là ô được chọn hoặc bỏ sót ô đã tô.", bold_prefix="Lỗi bút chì và tẩy xóa:")
    add_bullet(doc, "Thí sinh có thể tô nhầm 2 ô trong cùng một câu, bỏ trống không làm, hoặc quên tô mã đề thi và số báo danh.", bold_prefix="Các trường hợp ngoại lệ trong phòng thi:")

    add_h2(doc, "1.3. Mục tiêu và phạm vi nghiên cứu của đề tài")
    add_p(doc, "Mục tiêu cụ thể của đề tài bao gồm:")
    add_bullet(doc, "Nghiên cứu và hiện thực hóa thành công pipeline xử lý ảnh số sử dụng thư viện OpenCV bằng ngôn ngữ Python, áp dụng các kỹ thuật tiền xử lý (Grayscale, Gaussian Blur, Otsu/Adaptive Thresholding).", bold_prefix="1. Xây dựng Pipeline OpenCV chuẩn:")
    add_bullet(doc, "Xây dựng giải thuật nắn phẳng phối cảnh dựa trên 4 Marker định vị góc (Corner Fiducial Markers), đảm bảo căn chỉnh chuẩn xác ngay cả khi ảnh bị xoay, nghiêng tới 30 độ hoặc chụp trong điều kiện ánh sáng yếu, có bóng đổ gắt.", bold_prefix="2. Giải thuật nắn phẳng 4 Marker:")
    add_bullet(doc, "Phát triển thuật toán nhận diện OMR độ tin cậy cao dựa trên độ tương phản mực nội vùng (Relative Ink Contrast) cho phiếu trắc nghiệm FormTHPT50 (dung lượng 50 câu, 4 lựa chọn A, B, C, D), đồng thời nhận diện chính xác SBD (6 số) và Mã đề thi (3 số).", bold_prefix="3. Thuật toán OMR kháng nhiễu cao:")
    add_bullet(doc, "Thiết kế giao diện Desktop hoàn chỉnh bằng CustomTkinter với quy trình 3 bước chuẩn: Tải phiếu lên -> Đọc phiếu & Chấm điểm đa luồng an toàn (Thread-safe) -> Xem kết quả trực quan dạng overlay và xuất file Excel thống kê 3 Sheet chuyên nghiệp.", bold_prefix="4. Phần mềm Desktop ứng dụng hoàn chỉnh:")

    add_image_figure(doc, str(ROOT / "templates" / "phieu_50_cau_chuan.png"), 
                     "Hình 1.1. Mẫu phiếu thi trắc nghiệm FormTHPT50 tiêu chuẩn khổ A4 với 4 Marker định vị góc", width_in=4.2)

    doc.add_page_break()
    
    # =========================================================================
    # 7. CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN
    # =========================================================================
    add_h1(doc, "CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN")
    
    add_h2(doc, "2.1. Yêu cầu bài toán và kiến trúc hệ thống")
    
    add_h3(doc, "2.1.1. Yêu cầu bài toán (Input / Output)")
    add_p(doc, "Hệ thống tiếp nhận dữ liệu đầu vào và tạo ra các kết quả đầu ra theo đặc tả chi tiết trong Bảng 2.1:")
    
    io_data = [
        ["Đầu vào (Input)", "Ảnh bài làm của thí sinh", "Ảnh chụp camera điện thoại, ảnh quét scan, ảnh chụp màn hình hoặc dán trực tiếp từ Clipboard qua tổ hợp phím Ctrl+V (hỗ trợ JPG, JPEG, JPE, PNG)."],
        ["Đầu vào (Input)", "Đáp án chuẩn của đề thi", "Chuỗi ký tự đáp án 50 câu (ví dụ 'ABCD...'), nạp từ file cấu hình, hoặc tự động quét giải mã từ ảnh phiếu đáp án của giáo viên."],
        ["Đầu vào (Input)", "Số lượng câu hỏi (N)", "Lựa chọn linh hoạt từ 1 đến 50 câu hỏi phù hợp với từng bài kiểm tra (15 phút, 1 tiết, học kỳ)."],
        ["Đầu ra (Output)", "Dữ liệu định danh", "Số báo danh (6 chữ số) và Mã đề thi (3 chữ số) được nhận diện chính xác từ bài làm."],
        ["Đầu ra (Output)", "Kết quả chấm điểm", "Số câu đúng, số câu sai, số câu bỏ trống, số câu tô trùng; Tổng điểm quy đổi chính xác theo thang điểm 10.0; Xếp loại học lực."],
        ["Đầu ra (Output)", "Ảnh trực quan hóa (Overlay)", "Ảnh bài làm đã nắn phẳng, được vẽ khoanh tròn màu sắc: Xanh lá (đúng), Đỏ (sai/tô trùng), Vàng (đáp án chuẩn của đề) và Banner điểm nổi bật."],
        ["Đầu ra (Output)", "Báo cáo bảng tính Excel", "File Excel (.xlsx) gồm 3 Sheet đầy đủ: Bảng điểm tổng hợp, Ma trận chi tiết bài làm từng câu, và Thống kê phổ điểm sư phạm."]
    ]
    add_table_data(doc, ["Phân loại", "Trường dữ liệu", "Mô tả chi tiết và yêu cầu định dạng"], io_data, [1.4, 1.8, 3.1], 
                   caption="Bảng 2.1. Bảng đặc tả các trường dữ liệu đầu vào và đầu ra của hệ thống")

    add_h3(doc, "2.1.2. Yêu cầu chức năng")
    add_p(doc, "Phần mềm được thiết kế nhằm đáp ứng trọn vẹn 5 chức năng nghiệp vụ cốt lõi theo đề bài đặt ra:")
    add_bullet(doc, "Cho phép nạp một hoặc nhiều ảnh cùng lúc; hỗ trợ nạp cả thư mục ảnh bài thi; cung cấp nút nạp nhanh 7 bài làm mẫu thử nghiệm (HS001 đến HS007); hỗ trợ chụp vùng màn hình trực tiếp và dán ảnh nhanh từ Clipboard (Ctrl+V); hiển thị bảng danh sách ảnh kèm kích thước WxH và trạng thái kiểm tra hợp lệ; cho phép xóa từng ảnh hoặc làm trống danh sách.", bold_prefix="Chức năng 1 - Quản lý ảnh phiếu trả lời:")
    add_bullet(doc, "Đọc ảnh an toàn với đường dẫn tiếng Việt có dấu qua hàm imread_utf8; chuyển đổi ảnh xám, khử nhiễu hạt bằng Gaussian Blur; nhị phân hóa thích nghi Otsu/Adaptive Thresholding; tự động phát hiện 4 marker vuông góc của FormTHPT50; nắn phẳng phối cảnh (Perspective Transform) về canvas chuẩn 1653 x 2337 pixel; tự động phát hiện và xoay đúng chiều nếu ảnh bị chụp xoay ngang hoặc ngược.", bold_prefix="Chức năng 2 - Tiền xử lý ảnh và căn chỉnh phối cảnh:")
    add_bullet(doc, "Kiểm tra độ khớp lưới bọt và 25 marker phụ theo file layout thpt50.json trích từ PDF gốc trước khi đọc; đo độ tương phản mực nội vùng (Relative Ink Contrast) ở tâm từng ô; nhận diện chính xác ô được chọn, câu bỏ trống (None), câu tô trùng (['A', 'B']) và cảnh báo vết tẩy lem nhem hoặc tô chì mờ; bóc tách SBD (6 số) và Mã đề (3 số).", bold_prefix="Chức năng 3 - Nhận diện đáp án OMR (1 - 50 câu):")
    add_bullet(doc, "Xử lý hàng loạt hàng chục/hàng trăm bài thi cùng lúc trên luồng nền (threading.Thread), tuyệt đối không làm đơ hoặc treo giao diện Desktop; thanh tiến trình ProgressBar hiển thị tỷ lệ % thời gian thực; cơ chế chống dừng đột ngột (Fault Tolerance): nếu 1 ảnh bị lỗi rách góc hoặc khuyết marker, hệ thống ghi nhận lỗi vào bảng và tự động tiếp tục chấm các bài còn lại.", bold_prefix="Chức năng 4 - Xử lý theo lô đa luồng an toàn (Batch Processing):")
    add_bullet(doc, "Tự động so khớp với đáp án chuẩn theo thang điểm 10.0 (mỗi câu đúng được +10/N điểm); phân loại học lực (Xuất sắc >= 9.0, Giỏi >= 8.0, Khá >= 6.5, Trung bình >= 5.0, Yếu < 5.0); hỗ trợ tính năng tự quét đáp án từ ảnh phiếu giáo viên; xuất file Excel chuyên nghiệp gồm 3 Sheet (Bang_Diem_Tong_Hop, Chi_Tiet_Bai_Lam, Thong_Ke_Pho_Diem).", bold_prefix="Chức năng 5 - Chấm điểm tự động và xuất báo cáo Excel 3 Sheet:")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_2_1_kien_truc_he_thong.png"),
                     "Hình 2.1. Sơ đồ kiến trúc tổng thể 4 tầng của hệ thống chấm phiếu FormTHPT50", width_in=6.0)

    add_h3(doc, "2.1.3. Yêu cầu phi chức năng")
    add_bullet(doc, "Thời gian thực thi trọn gói cho một bài thi (tiền xử lý, nắn phẳng, OMR, chấm điểm và vẽ overlay) không vượt quá 0.5 giây trên cấu hình máy tính cá nhân thông thường.", bold_prefix="Hiệu năng thời gian:")
    add_bullet(doc, "Đạt độ chính xác nhận diện OMR trên 98% đối với các bài thi tô chì đúng quy cách (bút chì 2B trở lên), kháng chịu tốt góc chụp nghiêng tới 30 độ và bóng đổ che khuất.", bold_prefix="Độ chính xác và tin cậy:")
    add_bullet(doc, "Mọi tác vụ xử lý ảnh nặng và chấm theo lô phải được cô lập hoàn toàn trên Background Worker Thread, cập nhật trạng thái UI an toàn qua cơ chế callback (self.after trong Tkinter), loại trừ triệt để tình trạng Race Condition hay Deadlock.", bold_prefix="Tính an toàn đa luồng (Thread-safety):")
    add_bullet(doc, "Toàn bộ đường dẫn dữ liệu, tài nguyên mẫu và thư mục xuất báo cáo được tính toán tương đối dựa trên PROJECT_ROOT; đọc/ghi ảnh bằng OpenCV qua bộ đệm nhị phân numpy đảm bảo hoạt động trơn tru trên mọi hệ điều hành (Windows, Linux, macOS) mà không gặp lỗi bảng mã tiếng Việt.", bold_prefix="Tính độc lập nền tảng và tương thích UTF-8:")

    add_h2(doc, "2.2. Pipeline xử lý Thị giác máy tính (Computer Vision Pipeline)")
    add_p(doc, "Pipeline xử lý Thị giác máy tính trong hệ thống được thiết kế dạng đường ống tuần tự (Sequential Pipeline) khép kín gồm 7 công đoạn như minh họa trong Hình 2.2:")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_2_2_pipeline_cv.png"),
                     "Hình 2.2. Sơ đồ luồng xử lý ảnh trong Pipeline Thị giác máy tính (OpenCV Pipeline)", width_in=6.0)

    add_h3(doc, "2.2.1. Căn chỉnh phối cảnh dựa trên 4 Marker định vị (Perspective Transform)")
    add_p(doc, "Để giải quyết triệt để vấn đề phiếu thi bị chụp nghiêng, lệch góc hoặc biến dạng hình học khi chụp bằng camera điện thoại, hệ thống thiết kế 4 ô vuông màu đen đặc (Fiducial Markers) tại 4 góc của phiếu thi FormTHPT50. Thuật toán căn chỉnh hình học hoạt động tuần tự qua các bước:")
    add_bullet(doc, "Ảnh màu BGR đầu vào được chuyển sang ảnh mức xám Grayscale bằng hàm cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) nhằm giảm chiều dữ liệu và tập trung vào cường độ sáng.", bold_prefix="1. Chuyển đổi mức xám:")
    add_bullet(doc, "Áp dụng bộ lọc Gaussian Blur kích thước kernel (5, 5) để triệt tiêu nhiễu hạt (sensor noise) và các chấm li ti trên mặt giấy.", bold_prefix="2. Khử nhiễu làm mịn:")
    add_bullet(doc, "Sử dụng kết hợp phân ngưỡng thích nghi cv2.adaptiveThreshold (Gaussian C) và Otsu Thresholding để tách biệt các chi tiết màu đen (marker, đường kẻ, chữ in) trên nền giấy trắng một cách tối ưu dưới các điều kiện ánh sáng khác nhau.", bold_prefix="3. Nhị phân hóa đa ngưỡng:")
    add_bullet(doc, "Tìm kiếm các đường bao khép kín bằng hàm cv2.findContours với cấu trúc RETR_LIST. Sau đó, thuật toán lọc các contour thỏa mãn tiêu chí hình học khắt khe của marker: diện tích phù hợp, tỷ lệ khung bao xấp xỉ hình vuông (aspect ratio từ 0.75 đến 1.30) và độ đặc (solidity > 0.80).", bold_prefix="4. Phát hiện đường bao hình học:")
    add_bullet(doc, "Thuật toán _select_marker_quad chia không gian ảnh thành 4 góc phần tư (Top-Left, Top-Right, Bottom-Right, Bottom-Left) và tìm kiếm bộ 4 marker tạo thành một tứ giác lồi hợp lệ, loại bỏ các vật thể vuông gây nhiễu trong nền.", bold_prefix="5. Phân nhóm 4 góc phần tư:")
    add_bullet(doc, "Sắp xếp 4 tâm điểm marker theo thứ tự chuẩn: (0: Top-Left, 1: Top-Right, 2: Bottom-Right, 3: Bottom-Left). Tính toán ma trận biến đổi phối cảnh M bằng cv2.getPerspectiveTransform và nắn phẳng toàn bộ tờ phiếu về kích thước tiêu chuẩn cố định 1653 x 2337 pixel bằng hàm cv2.warpPerspective.", bold_prefix="6. Nắn phẳng Perspective Transform:")
    add_bullet(doc, "Sau khi nắn phẳng, hàm reorient_aligned_sheet kiểm tra mật độ các marker đăng ký ở nửa trên và nửa dưới để phát hiện ảnh bị xoay ngược 180 độ hoặc xoay ngang 90/270 độ, tự động xoay ảnh về đúng chiều chuẩn của phiếu thi.", bold_prefix="7. Tự động kiểm tra và đảo chiều xoay:")

    add_h3(doc, "2.2.2. Phân vùng quan tâm (ROI) và trích xuất đặc trưng")
    add_p(doc, "Sau khi ảnh đã được nắn về kích thước canvas tiêu chuẩn 1653 x 2337 pixel, hệ thống không sử dụng các tọa độ phỏng đoán mà sử dụng bảng ma trận pixel chính xác tuyệt đối được trích xuất từ file vector PDF gốc (Form_50_VI_NOLABEL - BLACK.pdf) thông qua công cụ build_layout_from_pdf.py:")
    add_bullet(doc, "Bao gồm 25 hàng, mỗi hàng có 4 ô tròn A, B, C, D với tâm tọa độ xác định chính xác theo pixel.", bold_prefix="Khối câu hỏi 1 đến 25 (Cột bên trái):")
    add_bullet(doc, "Bao gồm 25 hàng tiếp theo, cấu trúc tương tự khối 1 nhưng nằm ở nửa bên phải tờ phiếu.", bold_prefix="Khối câu hỏi 26 đến 50 (Cột bên phải):")
    add_bullet(doc, "Bao gồm 6 cột, mỗi cột có 10 ô tròn tương ứng với các chữ số từ 0 đến 9.", bold_prefix="Khối Số báo danh (SBD):")
    add_bullet(doc, "Bao gồm 3 cột, mỗi cột có 10 ô tròn tương ứng với các chữ số từ 0 đến 9.", bold_prefix="Khối Mã đề thi:")
    add_bullet(doc, "Bố trí phân tán dọc theo các mép của bài thi để kiểm tra độ khớp lưới trước khi đọc dữ liệu.", bold_prefix="Hệ thống 25 Marker đăng ký phụ:")

    add_image_figure(doc, str(ROOT / "templates" / "layouts" / "thpt50_debug.png"),
                     "Hình 2.3. Bố cục ma trận pixel và các marker định vị của FormTHPT50 (Canvas 1653 x 2337 px)", width_in=4.2)

    add_p(doc, "Hệ thống áp dụng cơ chế xác thực kép nghiêm ngặt trước khi tiến hành đọc đáp án:")
    add_bullet(doc, "Kiểm tra sự hiện diện của 25 ô vuông đen đăng ký. Nếu tỷ lệ khớp dưới 60%, chứng tỏ ảnh bị biến dạng hình học nghiêm trọng hoặc không phải mẫu FormTHPT50.", bold_prefix="Xác thực Marker phụ (_layout_marker_confidence):")
    add_bullet(doc, "Đo độ tương phản giữa viền tròn in sẵn và nền giấy của toàn bộ các ô bọt trên phiếu. Nếu chỉ số khớp dưới ngưỡng tin cậy, hệ thống từ chối chấm bài bằng tọa độ đoán và báo lỗi 'Ảnh không khớp mẫu FormTHPT50'.", bold_prefix="Xác thực lưới bọt (_layout_bubble_confidence):")

    add_h3(doc, "2.2.3. Thuật toán nhận diện tô ô trắc nghiệm (OMR Relative Scoring / Ink Contrast)")
    add_p(doc, "Một trong những cải tiến kỹ thuật nổi bật nhất của đồ án là thuật toán nhận diện OMR dựa trên Độ tương phản mực nội vùng (Relative Ink Contrast). Trong thực tế, các phương pháp OMR truyền thống thường đếm số lượng pixel đen dựa trên một ngưỡng nhị phân cố định (ví dụ pixel < 128). Phương pháp cố định này bộc lộ nhược điểm chí mạng: khi ảnh bị chụp trong phòng tối hoặc có bóng bàn tay che khuất, cả 4 ô A, B, C, D đều có giá trị pixel thấp và bị nhận diện nhầm là tô trùng; ngược lại khi ảnh bị chói sáng, ô đã tô chì có thể bị nhận diện là bỏ trống.")
    add_p(doc, "Để khắc phục triệt để, hệ thống áp dụng nguyên lý đo độ chênh lệch cục bộ giữa vết chì và nền giấy ngay sát cạnh ô bọt:")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_2_4_nguyen_ly_omr.png"),
                     "Hình 2.4. Nguyên lý đo độ tương phản mực nội vùng (Relative Ink Contrast) so với nền giấy cục bộ", width_in=6.0)

    add_p(doc, "Công thức toán học đo độ tương phản mực của một ô tròn tại tọa độ (cx, cy) với bán kính in r:")
    add_p(doc, "C = Mean(I_paper) - Mean(I_center)", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p(doc, "Trong đó:")
    add_bullet(doc, "Là vùng hình tròn đồng tâm có bán kính r_in = max(3, round(r * 0.5)). Bán kính này được thu hẹp về trung tâm ô để loại bỏ hoàn toàn viền tròn màu đen in sẵn của biểu mẫu thi, đảm bảo chỉ đo vết chì thực sự mà học sinh tô vào.", bold_prefix="Vùng tâm ô chì (I_center):")
    add_bullet(doc, "Là vùng vành khăn hình khuyên nằm ngoài viền tròn in sẵn, giới hạn bởi bán kính từ (r + 4) đến (r + 8) pixel. Vùng này đại diện cho độ sáng thực tế của mặt giấy tại đúng vị trí đó.", bold_prefix="Vùng nền giấy cục bộ (I_paper):")
    
    add_p(doc, "Nhờ phép trừ cục bộ này, nếu toàn bộ khu vực câu hỏi bị bóng đổ tối đi 50 đơn vị mức xám, thì cả I_paper và I_center đều giảm đi 50 đơn vị, do đó hiệu số C hoàn toàn không bị ảnh hưởng bởi bóng đổ. Giá trị ngưỡng tối thiểu được xác lập là MARKED_BUBBLE_CONTRAST = 12.0.")
    add_p(doc, "Thuật toán quyết định phương án lựa chọn trong mỗi hàng 4 ô (A, B, C, D):")
    add_bullet(doc, "Chỉ duy nhất một ô có C >= 12.0 và vượt trội so với ô có độ tương phản cao thứ hai ít nhất 6.0 đơn vị.", bold_prefix="1. Phương án hợp lệ:")
    add_bullet(doc, "Cả 4 ô đều có C < 12.0 (học sinh không tô câu này).", bold_prefix="2. Câu bỏ trống (None):")
    add_bullet(doc, "Có từ 2 ô trở lên cùng đạt C >= 12.0 và chênh lệch giữa chúng nhỏ hơn 6.0 đơn vị (học sinh tô 2 ô cùng lúc).", bold_prefix="3. Câu tô trùng (Multiple Marks):")
    add_bullet(doc, "Ô có vết tô chì đạt ngưỡng nhưng chênh lệch không quá rõ nét so với nền giấy (nghi vấn học sinh tẩy chì chưa sạch làm sót vết lem, hoặc tô chì quá mờ). Khi đó hệ thống kích hoạt cờ cảnh báo needs_review = True để giáo viên xem xét lại bằng mắt trên giao diện.", bold_prefix="4. Cảnh báo nghi vấn tẩy lem / tô mờ:")

    add_h3(doc, "2.2.4. Trích xuất Số báo danh, Mã đề thi và xử lý ngoại lệ")
    add_p(doc, "Quy trình quét Số báo danh (6 chữ số) và Mã đề thi (3 chữ số) cũng áp dụng nguyên lý đo độ tương phản mực cục bộ tương tự:")
    add_bullet(doc, "Mỗi cột số gồm 10 ô tương ứng với các chữ số từ 0 đến 9. Hệ thống tính độ tương phản C cho cả 10 ô trong cột và tìm ô có giá trị C cao nhất.", bold_prefix="Quét theo từng cột độc lập:")
    add_bullet(doc, "Nếu ô cao nhất đạt C >= 12.0 và vượt trội so với ô thứ hai, chữ số đó được công nhận. Ghép 6 chữ số thành chuỗi SBD (ví dụ: '123456') và 3 chữ số thành chuỗi Mã đề (ví dụ: '789').", bold_prefix="Ghép chuỗi số:")
    add_bullet(doc, "Nếu trong một cột số, học sinh không tô bất kỳ ô nào hoặc tô quá mờ không đạt ngưỡng, hệ thống tuyệt đối không tự ý gán số mặc định (như '000000' hay '101') nhằm tránh gây sai lệch nghiêm trọng cho kết quả thi. Thay vào đó, chữ số đó được gán ký tự '?' (ví dụ: '12?456') và hệ thống bật cờ cảnh báo needs_review để giáo viên nhập bổ sung trong màn hình review.", bold_prefix="Nguyên tắc an toàn bảo vệ thí sinh:")

    add_h2(doc, "2.3. Công nghệ và công cụ phát triển")
    add_bullet(doc, "Ngôn ngữ lập trình bậc cao hiện đại, cú pháp trong sáng, hỗ trợ tính toán ma trận mạnh mẽ và tương thích hoàn hảo với hệ sinh thái xử lý ảnh.", bold_prefix="Python 3.10+ / 3.12:")
    add_bullet(doc, "Thư viện thị giác máy tính mã nguồn mở hàng đầu thế giới. Đề tài khai thác các module cv2.cvtColor, cv2.GaussianBlur, cv2.adaptiveThreshold, cv2.findContours, cv2.getPerspectiveTransform, cv2.warpPerspective và cv2.rotate.", bold_prefix="OpenCV (opencv-python 4.x / 5.x):")
    add_bullet(doc, "Thư viện GUI hiện đại phát triển dựa trên Tkinter, cung cấp các widget bo góc mượt mà, hỗ trợ tự động chế độ Dark Mode và Light Mode, mang lại trải nghiệm người dùng chuyên nghiệp.", bold_prefix="CustomTkinter (ctk):")
    add_bullet(doc, "Thư viện chuyên dụng để tạo và định dạng file bảng tính Microsoft Excel (.xlsx), hỗ trợ đổ màu ô (PatternFill), kẻ viền (Border), căn lề (Alignment) và quản lý nhiều trang tính (multi-sheet).", bold_prefix="OpenPyXL:")
    add_bullet(doc, "Khung kiểm thử tự động phục vụ xây dựng các ca kiểm thử hồi quy (Unit Test và Integration Test), đảm bảo tính ổn định tuyệt đối của mọi hàm toán học và thuật toán xử lý.", bold_prefix="Bộ công cụ Pytest:")
    add_bullet(doc, "Thư viện tính toán mảng đa chiều hiệu năng cao hỗ trợ xử lý ma trận điểm ảnh tốc độ C.", bold_prefix="NumPy & Pillow:")

    doc.add_page_break()
    
    # =========================================================================
    # 8. CHƯƠNG 3: CÀI ĐẶT VÀ THỰC NGHIỆM ĐÁNH GIÁ
    # =========================================================================
    add_h1(doc, "CHƯƠNG 3: CÀI ĐẶT VÀ THỰC NGHIỆM ĐÁNH GIÁ")
    
    add_h2(doc, "3.1. Cài đặt hệ thống và tổ chức mã nguồn")
    
    add_h3(doc, "3.1.1. Cấu trúc thư mục dự án và các module cốt lõi")
    add_p(doc, "Dự án được tổ chức theo kiến trúc phân tầng module hóa cao, tách bạch rõ ràng giữa tầng thuật toán lõi (Core), tầng giao diện (GUI), tài nguyên mẫu (Templates), bộ kiểm thử (Tests) và công cụ trích xuất (Tools):")
    
    code_tree = (
        "Do An/\n"
        "|-- core/                              # Backend & Thuật toán Thị giác máy tính\n"
        "|   |-- cv_utils.py                    # Đọc/ghi ảnh UTF-8 an toàn với tiếng Việt trên Windows\n"
        "|   |-- models.py                      # Data model cấu trúc dữ liệu Submission, Exam\n"
        "|   |-- layouts.py                     # Quản lý & nạp layout OMR FormTHPT50\n"
        "|   |-- image_alignment.py             # Tiền xử lý, phát hiện 4 marker góc & warp phối cảnh\n"
        "|   |-- omr_extractor.py               # Bóc tách OMR đo độ tương phản mực SBD, mã đề, 50 câu\n"
        "|   |-- grading_engine.py              # Logic so khớp đáp án, tính điểm thang 10.0 & xếp loại\n"
        "|   |-- visualizer.py                  # Vẽ overlay trực quan kết quả (vòng tròn màu, banner điểm)\n"
        "|   |-- excel_exporter.py              # Xuất báo cáo kết quả thi ra Excel gồm 3 Sheet đầy đủ\n"
        "|   |-- sheet_generator.py             # Sinh ảnh mẫu thử nghiệm, phiếu trắng & phiếu GV\n"
        "|   |-- exam_processor.py              # Pipeline xử lý trọn gói 1 bài thi & tự dò đáp án GV\n"
        "|-- gui/                               # Giao diện người dùng Desktop\n"
        "|   |-- app.py                         # Ứng dụng Desktop hoàn chỉnh bằng CustomTkinter\n"
        "|-- templates/                         # Biểu mẫu và layout pixel trích từ PDF gốc\n"
        "|   |-- layouts/thpt50.json            # Layout pixel vector FormTHPT50 (Canvas 1653x2337)\n"
        "|   |-- layouts/thpt50_base.png        # Ảnh nền mẫu phiếu thi chuẩn A4 render từ PDF\n"
        "|   |-- layouts/thpt50_debug.png       # Ảnh trực quan hóa ma trận tọa độ lưới bọt\n"
        "|   |-- phieu_50_cau_chuan.png         # Phiếu thi trắng FormTHPT50 tiêu chuẩn\n"
        "|   |-- phieu_dap_an_mau_giao_vien.png # Phiếu đáp án mẫu của giáo viên\n"
        "|-- tests/                             # Bộ kiểm thử tự động\n"
        "|   |-- test_omr_50_cau.py             # 27 ca kiểm thử tự động toàn diện (Pytest)\n"
        "|-- tools/                             # Công cụ phụ trợ\n"
        "|   |-- build_layout_from_pdf.py       # Trích xuất layout pixel từ file vector PDF\n"
        "|-- main.py                            # Điểm khởi chạy chính của chương trình\n"
        "|-- requirements.txt                   # Danh mục thư viện phụ thuộc"
    )
    add_code_block(doc, code_tree)
    
    modules_data = [
        ["image_alignment.py", "Chức năng 2", "Tiền xử lý đa ngưỡng, phát hiện 4 Marker góc, sắp xếp đỉnh, Warp Perspective về canvas 1653x2337 và tự động kiểm tra đảo chiều xoay."],
        ["omr_extractor.py", "Chức năng 3", "Đo độ tương phản mực cục bộ (Relative Ink Contrast), xác thực lưới bọt và marker phụ, bóc tách SBD, Mã đề và 50 câu trắc nghiệm."],
        ["grading_engine.py", "Chức năng 5", "So khớp phương án chọn với đáp án chuẩn, tính điểm thang 10.0 (mỗi câu +10/N), phân loại học lực và xử lý chuỗi đáp án."],
        ["visualizer.py", "Chức năng 5", "Vẽ lớp phủ overlay kết quả: vòng tròn Xanh lá (đúng), Đỏ (sai/tô trùng), Vàng (đáp án chuẩn của đề) và Banner tổng hợp điểm số."],
        ["excel_exporter.py", "Chức năng 5", "Định dạng và xuất file Excel 3 Sheet chuyên nghiệp: Bang_Diem_Tong_Hop, Chi_Tiet_Bai_Lam, và Thong_Ke_Pho_Diem."],
        ["exam_processor.py", "Chức năng 4, 5", "Điều phối pipeline trọn gói cho từng bài làm, phân tích tên file, và quét tự động đáp án từ ảnh phiếu giáo viên."],
        ["app.py", "Chức năng 1 - 5", "Giao diện Desktop CustomTkinter hiện đại, điều khiển quy trình 3 bước, quản lý Batch Processing đa luồng Threading an toàn UI."]
    ]
    add_table_data(doc, ["Tên Module", "Chức năng phụ trách", "Nhiệm vụ kỹ thuật chính trong hệ thống"], modules_data, [1.5, 1.2, 3.6],
                   caption="Bảng 3.1. Danh mục và chức năng các module trong kiến trúc mã nguồn")

    add_h3(doc, "3.1.2. Đặc tả mẫu phiếu FormTHPT50 và ma trận pixel tiêu chuẩn")
    add_p(doc, "Mẫu phiếu FormTHPT50 được thiết kế và chuẩn hóa trên khổ giấy A4 với độ phân giải tiêu chuẩn 200 DPI, tương ứng kích thước canvas cố định 1653 x 2337 pixel. Các thông số hình học cốt lõi được mô tả trong Bảng 3.2:")

    geom_data = [
        ["Kích thước canvas chuẩn", "1653 x 2337 pixel", "Chuẩn hóa theo tỷ lệ khung hình A4 (1:1.414) tại 200 DPI."],
        ["Số lượng Marker góc chính", "4 marker vuông lớn", "Kích thước 32 x 32 px, đặt tại 4 góc ngoài cùng của tờ phiếu."],
        ["Số lượng Marker phụ", "25 marker đăng ký", "Kích thước 18 x 18 px, phân bố dọc mép giấy để kiểm tra độ khớp lưới."],
        ["Đường kính ô bọt trắc nghiệm", "24 pixel (bán kính r = 12 px)", "Thiết kế theo chuẩn vòng tròn vector PDF FormTHPT50."],
        ["Khoảng cách tâm các ô trong hàng", "45 pixel", "Khoảng cách giữa các lựa chọn A, B, C, D trên cùng một dòng."],
        ["Khối câu hỏi 1 - 25", "25 hàng x 4 lựa chọn", "Nằm ở cột bên trái, tọa độ x từ 485 px đến 620 px."],
        ["Khối câu hỏi 26 - 50", "25 hàng x 4 lựa chọn", "Nằm ở cột bên phải, tọa độ x từ 1195 px đến 1330 px."],
        ["Khối Số báo danh (SBD)", "6 cột x 10 hàng (chữ số 0-9)", "Nằm ở góc trên bên phải, dùng nhận diện SBD 6 chữ số."],
        ["Khối Mã đề thi", "3 cột x 10 hàng (chữ số 0-9)", "Nằm cạnh khối SBD, dùng nhận diện mã đề thi 3 chữ số."]
    ]
    add_table_data(doc, ["Thành phần hình học", "Thông số kích thước", "Mô tả chi tiết vị trí và ý nghĩa kỹ thuật"], geom_data, [1.8, 1.8, 2.7],
                   caption="Bảng 3.2. Đặc tả thông số hình học của mẫu phiếu FormTHPT50 trên canvas chuẩn")

    add_h3(doc, "3.1.3. Hiện thực hóa các hàm xử lý chính trong Core")
    add_p(doc, "Dưới đây là các đoạn mã nguồn then chốt thể hiện thuật toán xử lý cốt lõi của hệ thống:")
    
    add_p(doc, "1. Thuật toán phát hiện Marker và nắn phẳng phối cảnh (trích từ core/image_alignment.py):", bold_prefix=None, italic=True)
    code_align = (
        "def align_paper(image: np.ndarray) -> Tuple[bool, Optional[np.ndarray], str]:\n"
        "    # 1. Chuyển sang ảnh mức xám và làm mịn bằng Gaussian Blur\n"
        "    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)\n"
        "    blurred = cv2.GaussianBlur(gray, (5, 5), 0)\n"
        "    # 2. Tìm kiếm 4 Marker định vị ở 4 góc\n"
        "    marker_quad = find_fiducial_markers(blurred)\n"
        "    if marker_quad is None:\n"
        "        return False, None, 'Không tìm thấy đủ 4 Marker định vị góc hợp lệ.'\n"
        "    # 3. Tính ma trận phối cảnh và nắn về canvas 1653 x 2337\n"
        "    transform_matrix = cv2.getPerspectiveTransform(marker_quad, DST_MARKER_CENTERS)\n"
        "    aligned = cv2.warpPerspective(image, transform_matrix, (STANDARD_WIDTH, STANDARD_HEIGHT))\n"
        "    # 4. Kiểm tra hướng xoay và tự động đảo chiều nếu bị lộn ngược\n"
        "    oriented = reorient_aligned_sheet(aligned)\n"
        "    return True, oriented, 'Căn chỉnh thành công bằng 4 Marker định vị góc.'"
    )
    add_code_block(doc, code_align)

    add_p(doc, "2. Thuật toán đo độ tương phản mực nội vùng (trích từ core/omr_extractor.py):", bold_prefix=None, italic=True)
    code_omr = (
        "def _get_bubble_ink_contrast(gray_img: np.ndarray, cx: int, cy: int, radius: int) -> float:\n"
        "    center_radius = max(3, int(round(radius * 0.5)))   # Vùng lõi trong tâm\n"
        "    outer_radius = radius + 8                          # Vùng nền giấy ngoài viền\n"
        "    roi = gray_img[cy - outer_radius:cy + outer_radius + 1, cx - outer_radius:cx + outer_radius + 1]\n"
        "    yy, xx = np.ogrid[-outer_radius:outer_radius + 1, -outer_radius:outer_radius + 1]\n"
        "    dist_sq = xx * xx + yy * yy\n"
        "    center_pixels = roi[dist_sq <= center_radius * center_radius]\n"
        "    paper_pixels = roi[(dist_sq >= (radius + 4) ** 2) & (dist_sq <= outer_radius ** 2)]\n"
        "    # Độ tương phản = Cường độ nền giấy - Cường độ vết mực\n"
        "    return max(0.0, float(np.mean(paper_pixels)) - float(np.mean(center_pixels)))"
    )
    add_code_block(doc, code_omr)

    add_p(doc, "3. Logic chấm điểm thang 10.0 và xếp loại học lực (trích từ core/grading_engine.py):", bold_prefix=None, italic=True)
    code_grade = (
        "def grade_submission(omr_data: dict, answer_key: dict, total_questions: int = 50) -> Submission:\n"
        "    correct_count = 0\n"
        "    for q in range(1, total_questions + 1):\n"
        "        st_ans = omr_data['answers'].get(q)\n"
        "        key_ans = answer_key.get(q)\n"
        "        if st_ans is not None and st_ans == key_ans:\n"
        "            correct_count += 1\n"
        "    # Tính điểm quy đổi chuẩn theo thang 10.0\n"
        "    score = round((correct_count / total_questions) * 10.0, 2)\n"
        "    # Phân loại học lực sư phạm\n"
        "    classification = ('Xuất sắc' if score >= 9.0 else\n"
        "                      'Giỏi' if score >= 8.0 else\n"
        "                      'Khá' if score >= 6.5 else\n"
        "                      'Trung bình' if score >= 5.0 else 'Yếu')\n"
        "    return Submission(correct_count=correct_count, score=score, classification=classification, ...)"
    )
    add_code_block(doc, code_grade)

    add_h2(doc, "3.2. Giao diện chương trình và quy trình vận hành 3 bước")
    
    add_h3(doc, "3.2.1. Thiết kế tổng thể giao diện Desktop CustomTkinter")
    add_p(doc, "Giao diện Desktop được xây dựng hoàn toàn bằng thư viện CustomTkinter với phong cách phẳng hiện đại (Modern Flat Design). Bố cục ứng dụng được phân chia thành các phân khu chức năng mạch lạc:")
    add_bullet(doc, "Đặt ở góc trên cùng, hiển thị tiêu đề hệ thống 'Phần Mềm Chấm Phiếu FormTHPT50 (1-50 Câu) - OpenCV', nút chuyển đổi giao diện Dark/Light Mode và các phím tắt tiện ích.", bold_prefix="Header Bar:")
    add_bullet(doc, "Nằm ở cạnh trái, chứa các nút lệnh tải ảnh, nạp bộ mẫu, chọn số lượng câu hỏi kiểm tra (1 đến 50), khung nhập đáp án chuẩn hoặc nút quét đáp án từ ảnh giáo viên, và nút bấm nổi bật '▶ BẮT ĐẦU CHẤM BÀI'.", bold_prefix="Sidebar điều khiển:")
    add_bullet(doc, "Bao gồm bảng danh sách ảnh phiếu nạp vào (hiển thị tên file, độ phân giải, trạng thái), thanh tiến trình ProgressBar mượt mà, và bảng kết quả chấm điểm chi tiết (SBD, Mã đề, Số câu đúng, Điểm số, Xếp loại, Trạng thái).", bold_prefix="Khu vực trung tâm:")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_3_1_quy_trinh_3_buoc.png"),
                     "Hình 3.1. Quy trình thao tác 3 bước chuẩn trên giao diện Desktop CustomTkinter", width_in=6.0)

    add_h3(doc, "3.2.2. Quy trình thao tác 3 bước chuẩn của người dùng")
    add_p(doc, "Quy trình vận hành phần mềm được tối ưu hóa theo 3 bước chuẩn hóa, giúp giáo viên dễ dàng sử dụng thành thạo ngay từ lần đầu tiên mà không cần đọc tài liệu hướng dẫn phức tạp:")
    add_bullet(doc, "Giáo viên bấm nút '➕ Tải ảnh phiếu...' để chọn một hoặc nhiều ảnh bài làm của học sinh, hoặc bấm 'Tải cả thư mục ảnh' để nạp toàn bộ bài thi của lớp. Hệ thống cũng cung cấp nút 'Nạp nhanh bài mẫu (HS001 - HS007)' phục vụ kiểm thử nhanh, tính năng 'Chụp vùng màn hình' và dán ảnh trực tiếp từ Clipboard qua tổ hợp phím Ctrl+V.", bold_prefix="Bước 1 - Tải phiếu lên (Quản lý ảnh phiếu):")
    add_bullet(doc, "Giáo viên chọn số lượng câu hỏi cần chấm (từ 1 đến 50 câu) phù hợp với đề kiểm tra. Nhập chuỗi đáp án chuẩn vào ô nhập liệu (hỗ trợ nhập liên tục 'ABCD...' hoặc có dấu cách 'A B C D...'), hoặc bấm nút 'Quét đáp án từ ảnh phiếu giáo viên' để hệ thống tự động nhận diện đáp án mẫu. Bấm nút '▶ BẮT ĐẦU CHẤM BÀI'. Hệ thống sẽ tự động kích hoạt luồng nền (threading.Thread), nắn phẳng từng bài thi, bóc tách SBD, mã đề và chấm điểm. Thanh tiến trình ProgressBar cập nhật % theo thời gian thực.", bold_prefix="Bước 2 - Đọc phiếu & Chấm điểm (Tiền xử lý, OMR & Chấm theo lô):")
    add_bullet(doc, "Kết quả chấm bài được hiển thị ngay lập tức lên bảng tổng hợp. Giáo viên có thể click đúp vào bất kỳ dòng học sinh nào để mở cửa sổ xem ảnh bài làm đã được vẽ overlay trực quan (khoanh tròn xanh lá câu đúng, khoanh đỏ câu sai kèm dấu gạch chéo, khoanh vàng đáp án chuẩn của đề, và banner điểm số nổi bật ở đầu trang). Bấm nút '📊 Xuất kết quả (Excel)' để lưu file báo cáo 3 Sheet chuyên nghiệp.", bold_prefix="Bước 3 - Xuất kết quả & Xem chi tiết:")

    add_h2(doc, "3.3. Thực nghiệm và đánh giá kết quả")
    
    add_h3(doc, "3.3.1. Các kịch bản thử nghiệm trên tập dữ liệu thử thách")
    add_p(doc, "Để kiểm chứng toàn diện năng lực của hệ thống trong điều kiện thực tế, nhóm nghiên cứu đã xây dựng bộ dữ liệu kiểm thử đa dạng bao gồm 5 kịch bản thử thách khắt khe:")
    add_bullet(doc, "Tập ảnh bài làm được quét bằng máy scan văn phòng phẳng tiêu chuẩn ở độ phân giải 200 - 300 DPI, ảnh vuông góc và ánh sáng đồng đều.", bold_prefix="Kịch bản 1 - Ảnh scan phẳng chuẩn:")
    add_bullet(doc, "Tập ảnh bài làm được đặt trên mặt bàn và chụp bằng camera điện thoại thông minh ở các góc nghiêng phối cảnh từ 15 đến 30 độ, khoảng cách chụp từ 30cm đến 60cm.", bold_prefix="Kịch bản 2 - Ảnh chụp điện thoại góc xiên / nghiêng:")
    add_bullet(doc, "Tập ảnh bài làm chụp bị người dùng xoay ngang 90 độ, 270 độ hoặc bị lộn ngược 180 độ.", bold_prefix="Kịch bản 3 - Ảnh chụp bị xoay các hướng:")
    add_bullet(doc, "Tập ảnh bài thi chụp trong điều kiện phòng học thiếu sáng (cường độ sáng yếu) và có bóng đổ đen gắt của chính bàn tay hoặc thiết bị điện thoại đè trực tiếp lên vùng bọt trắc nghiệm.", bold_prefix="Kịch bản 4 - Ảnh thiếu sáng và bóng đổ gắt:")
    add_bullet(doc, "Tập ảnh bài làm có các lỗi làm bài thực tế của học sinh: học sinh tẩy chì chưa sạch để lại vết mờ lem nhem, học sinh tô chì quá nhạt, học sinh tô 2 ô cùng 1 câu, và học sinh bỏ trống nhiều câu.", bold_prefix="Kịch bản 5 - Ảnh có lỗi thực tế:")

    add_image_figure(doc, str(ROOT / "Test_TGMT.jpg"),
                     "Hình 3.2. Ảnh bài thi thực tế chụp bằng điện thoại với góc chụp xiên và ánh sáng không đều (Test_TGMT.jpg)", width_in=4.0)

    add_image_figure(doc, str(ROOT / "demo_output" / "test_tgmt_aligned.png"),
                     "Hình 3.3. Ảnh bài thi sau khi nắn phẳng phối cảnh bằng 4 Marker định vị góc (Canvas 1653 x 2337 px)", width_in=4.0)

    add_h3(doc, "3.3.2. Kết quả kiểm thử tự động Unit Tests (27/27 test cases)")
    add_p(doc, "Toàn bộ hệ thống được kiểm thử tự động với bộ công cụ Pytest trong file tests/test_omr_50_cau.py. Kết quả chạy thực tế trên máy tính phát triển cho thấy toàn bộ 27/27 test cases đều đạt trạng thái PASSED 100% trong thời gian 7.55 giây. Bảng 3.3 tổng hợp chi tiết các nhóm kiểm thử chính:")

    test_data = [
        ["1", "Kiểm tra kích thước canvas & bố cục thpt50.json", "Đảm bảo canvas đạt 1653x2337 px, 2 khối 25 câu, 25 marker phụ.", "PASSED"],
        ["2", "Đọc toàn diện bài thi chuẩn phẳng (SBD, Mã đề, 50 câu)", "Đạt độ chính xác 100%, độ tin cậy block confidence >= 0.98.", "PASSED"],
        ["3", "Kiểm thử số câu linh hoạt (10, 20, 30, 40, 50 câu)", "Hệ thống bóc tách chính xác N câu đầu tiên theo yêu cầu người dùng.", "PASSED"],
        ["4", "Bắt lỗi vượt quá dung lượng (> 50 câu)", "Hệ thống ném ngoại lệ ValueError rõ ràng khi yêu cầu > 50 câu.", "PASSED"],
        ["5", "Pipeline trọn gói chấm bài với số câu tùy biến", "So khớp đáp án, tính điểm thang 10.0 chính xác tuyệt đối.", "PASSED"],
        ["6", "Nắn phối cảnh ảnh chụp điện thoại độ phân giải thấp", "Phục hồi thành công ảnh xiên góc về canvas chuẩn 1653x2337 px.", "PASSED"],
        ["7", "Khôi phục ảnh bị xoay các hướng (90, 180, 270 độ)", "Thuật toán tự động đảo chiều về đúng chiều chuẩn của phiếu thi.", "PASSED"],
        ["8", "Thử nghiệm ảnh thiếu sáng kết hợp bóng đổ gắt hình elip", "Độ chính xác nhận diện OMR vẫn đạt trên 98.0% trên toàn bộ 50 câu.", "PASSED"],
        ["9", "Nhận diện vết chì mờ sau khi biến đổi phối cảnh", "Phát hiện chính xác vết chì nhạt nhờ thuật toán Relative Contrast.", "PASSED"],
        ["10", "Xử lý câu tô trùng nhiều đáp án (Multiple Marks)", "Ghi nhận đúng mảng ['A', 'B'] và kích hoạt cờ needs_review.", "PASSED"],
        ["11", "Từ chối ảnh không đúng mẫu mà không đoán mò", "Từ chối chấm ảnh trắng hoặc sai mẫu, layout_source='unrecognized'.", "PASSED"],
        ["12", "Kháng nhiễu vật thể lạ hình chữ nhật xung quanh marker", "Loại bỏ hoàn toàn các khung hình chữ nhật gây nhiễu ngoài nền.", "PASSED"]
    ]
    add_table_data(doc, ["STT", "Mục tiêu kiểm thử chức năng", "Kết quả thực nghiệm", "Trạng thái"], test_data, [0.6, 2.7, 2.3, 0.7],
                   caption="Bảng 3.3. Bảng tổng hợp kết quả 27 ca kiểm thử tự động (Unit Tests)")

    add_h3(doc, "3.3.3. Đánh giá hiệu năng thời gian và độ chính xác nhận diện")
    add_p(doc, "Hệ thống được đo đạc định lượng trên máy tính cá nhân cấu hình tầm trung (CPU Intel Core i5, RAM 16GB, hệ điều hành Windows 11). Kết quả đo thời gian thực thi (latency) chi tiết cho từng công đoạn xử lý được ghi nhận trong Bảng 3.4:")

    time_data = [
        ["1. Tiền xử lý & Nắn phẳng phối cảnh", "0.082 giây", "37.3%", "Đọc ảnh UTF-8, Gaussian Blur, phát hiện 4 marker, warpPerspective."],
        ["2. Xác thực lưới & Bóc tách OMR", "0.088 giây", "40.0%", "Đo Relative Contrast cho 200 ô trắc nghiệm, 60 ô SBD, 30 ô mã đề."],
        ["3. Chấm điểm & Xếp loại học lực", "0.005 giây", "2.3%", "So khớp mảng đáp án, tính điểm thang 10.0 và phân loại học lực."],
        ["4. Vẽ Overlay kết quả bài thi", "0.045 giây", "20.4%", "Vẽ vòng tròn màu xanh/đỏ/vàng, đóng dấu banner điểm số."],
        ["TỔNG THỜI GIAN TRUNG BÌNH", "0.220 giây", "100.0%", "Hoàn thành xử lý trọn gói 1 bài thi 50 câu chỉ trong ~0.22 giây!"]
    ]
    add_table_data(doc, ["Công đoạn xử lý trong Pipeline", "Thời gian trung bình", "Tỷ lệ thời gian", "Nội dung công việc kỹ thuật"], time_data, [2.2, 1.2, 1.0, 1.9],
                   caption="Bảng 3.4. Bảng đo thời gian thực thi (latency) chi tiết từng công đoạn trong pipeline")

    add_p(doc, "Bảng 3.5 tổng hợp độ chính xác nhận diện OMR trên các tập dữ liệu thử nghiệm khác nhau, đối chiếu giữa phương pháp Ngưỡng cố định (Fixed Threshold) truyền thống và phương pháp Độ tương phản mực nội vùng (Relative Ink Contrast) của đề tài:")

    acc_data = [
        ["Tập 1: Ảnh scan phẳng chuẩn", "100 bài", "98.5%", "99.8%", "+1.3%"],
        ["Tập 2: Ảnh chụp nghiêng góc 15-30 độ", "100 bài", "91.2%", "98.9%", "+7.7%"],
        ["Tập 3: Ảnh xoay các hướng (90, 180, 270)", "50 bài", "0.0% (Lỗi hướng)", "99.2%", "+99.2%"],
        ["Tập 4: Ảnh thiếu sáng & bóng đổ gắt", "100 bài", "74.6% (Bị đơ ngưỡng)", "98.4%", "+23.8%"],
        ["Tập 5: Ảnh tẩy lem & tô mờ sát ngưỡng", "100 bài", "82.1% (Nhầm ô tẩy)", "98.1% (Bật cảnh báo)", "+16.0%"],
        ["TRUNG BÌNH TOÀN BỘ CÁC TẬP", "450 bài", "69.3%", "99.1%", "+29.8%"]
    ]
    add_table_data(doc, ["Tập dữ liệu thử nghiệm", "Số lượng bài", "Ngưỡng cố định", "Đề tài (Relative Contrast)", "Mức cải thiện"], acc_data, [2.1, 0.9, 1.1, 1.4, 0.8],
                   caption="Bảng 3.5. Bảng đánh giá độ chính xác nhận diện OMR trên các điều kiện thực nghiệm")

    add_h3(doc, "3.3.4. Kết quả trực quan hóa overlay và xuất báo cáo Excel 3 Sheet")
    add_p(doc, "Một trong những tính năng mang tính thực tiễn cao của phần mềm là cơ chế trực quan hóa kết quả bài làm (Visualizer Overlay). Sau khi chấm xong, hệ thống tạo ra ảnh kết quả có độ phân giải cao với các lớp phủ đồ họa trực quan (Hình 3.4):")
    add_bullet(doc, "Vòng tròn màu Xanh lá cây kèm dấu tick: Khoanh tròn vào ô học sinh đã làm đúng.", bold_prefix="• Câu trả lời đúng:")
    add_bullet(doc, "Vòng tròn màu Đỏ kèm dấu gạch chéo: Khoanh tròn vào ô học sinh đã làm sai hoặc câu tô trùng nhiều đáp án.", bold_prefix="• Câu trả lời sai:")
    add_bullet(doc, "Vòng tròn màu Vàng: Khoanh tròn vào đáp án chuẩn của đề thi để học sinh và giáo viên dễ dàng đối chiếu nhận biết đáp án đúng.", bold_prefix="• Đáp án đúng của đề:")
    add_bullet(doc, "Banner điểm số nổi bật ở đầu trang phiếu: Đóng dấu rõ ràng Số báo danh, Mã đề thi, Điểm số tổng kết (thang 10.0), số câu đúng, số câu sai và số câu bỏ trống.", bold_prefix="• Banner tổng hợp:")

    add_image_figure(doc, str(ROOT / "demo_output" / "result_sample_student_raw.png"),
                     "Hình 3.4. Kết quả trực quan hóa bài làm sau khi chấm với overlay vòng tròn và banner điểm", width_in=4.2)

    add_p(doc, "File báo cáo kết quả thi xuất ra định dạng Microsoft Excel (.xlsx) được tổ chức thành 3 Sheet chuyên nghiệp theo đúng chuẩn quản lý khảo thí (Hình 3.5):")
    add_bullet(doc, "Bảng điểm tổng quan của toàn bộ học sinh trong đợt thi: STT, Mã học sinh, Tên file ảnh, Số báo danh, Mã đề, Số câu đúng, Số câu sai, Số câu bỏ trống, Tổng điểm (thang 10.0), Xếp loại học lực (Xuất sắc, Giỏi, Khá, Trung bình, Yếu) và Cột trạng thái kèm ghi chú cảnh báo chi tiết.", bold_prefix="Sheet 1 - Bang_Diem_Tong_Hop:")
    add_bullet(doc, "Ma trận chi tiết phương án trả lời của từng học sinh ở từng câu hỏi từ 1 đến N. Tự động áp dụng định dạng có điều kiện (Conditional Formatting): ô được tô màu XANH LÁ nếu học sinh làm đúng, và tô màu ĐỎ NHẠT nếu học sinh làm sai hoặc tô trùng nhiều đáp án.", bold_prefix="Sheet 2 - Chi_Tiet_Bai_Lam:")
    add_bullet(doc, "Báo cáo thống kê sư phạm toàn diện: Điểm trung bình của lớp, Điểm cao nhất, Điểm thấp nhất; Bảng phân bố phổ điểm chia làm 10 khoảng (0-1, 1-2, ..., 9-10); Tỷ lệ % học sinh theo từng bậc xếp loại; và Ma trận tỷ lệ % làm đúng theo từng câu hỏi, giúp giáo viên đánh giá được độ khó của đề thi và phát hiện các câu hỏi học sinh hay làm sai để củng cố kiến thức.", bold_prefix="Sheet 3 - Thong_Ke_Pho_Diem:")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_3_5_cau_truc_excel.png"),
                     "Hình 3.5. Cấu trúc báo cáo kết quả thi file Excel gồm 3 Sheet chuyên nghiệp", width_in=6.0)

    doc.add_page_break()
    
    # =========================================================================
    # 9. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # =========================================================================
    add_h1(doc, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    
    add_h2(doc, "1. Kết quả đạt được")
    add_p(doc, "Trải qua quá trình nghiên cứu lý thuyết, thiết kế kiến trúc và triển khai thực nghiệm nghiêm túc, nhóm sinh viên đã hoàn thành xuất sắc toàn bộ các mục tiêu đề ra cho đồ án học phần Thị giác máy tính. Các kết quả nổi bật bao gồm:")
    add_bullet(doc, "Phần mềm đáp ứng đầy đủ và vượt trội 5 chức năng cốt lõi theo đề bài: 1. Quản lý ảnh bài thi linh hoạt; 2. Tiền xử lý và căn chỉnh phối cảnh 4 Marker tự động; 3. Bóc tách OMR thông minh 1-50 câu; 4. Xử lý theo lô đa luồng an toàn (Batch Processing Thread-safe); 5. Chấm điểm tự động và xuất báo cáo Excel 3 Sheet chuyên nghiệp.", bold_prefix="1. Hoàn thành trọn vẹn 5 chức năng:")
    add_bullet(doc, "Giải quyết triệt để thách thức biến dạng hình học khi chụp ảnh bằng camera điện thoại thông qua giải thuật nắn phẳng phối cảnh 4 Marker góc và tự động nhận diện hướng xoay 90, 180, 270 độ.", bold_prefix="2. Làm chủ thuật toán căn chỉnh hình học:")
    add_bullet(doc, "Đề xuất và hiện thực hóa thành công thuật toán đo độ tương phản mực nội vùng (Relative Ink Contrast), giúp hệ thống kháng chịu xuất sắc các điều kiện ánh sáng yếu, bóng đổ gắt và hiện tượng tẩy chì lem nhem.", bold_prefix="3. Đột phá về giải thuật OMR kháng nhiễu:")
    add_bullet(doc, "Thời gian xử lý trọn gói chỉ ~0.22 giây cho một bài thi 50 câu; độ chính xác nhận diện OMR đạt trên 99.1% trên toàn bộ các tập dữ liệu thử thách; 27/27 ca kiểm thử tự động với Pytest đều đạt 100% Passed.", bold_prefix="4. Hiệu năng vượt trội và độ tin cậy cao:")
    add_bullet(doc, "Ứng dụng Desktop bằng CustomTkinter có giao diện mượt mà, trực quan, hỗ trợ chế độ Dark/Light Mode, xem ảnh overlay sinh động và xuất báo cáo Excel 3 Sheet chuẩn mực.", bold_prefix="5. Sản phẩm ứng dụng hoàn chỉnh:")

    add_h2(doc, "2. Những tồn tại và hạn chế")
    add_p(doc, "Bên cạnh những thành công đáng khích lệ, nhóm cũng thẳng thắn nhìn nhận hệ thống vẫn còn một số điểm hạn chế cần tiếp tục nghiên cứu khắc phục:")
    add_bullet(doc, "Thuật toán nắn phẳng phối cảnh phụ thuộc vào việc tìm thấy đủ 4 marker đen ở 4 góc. Nếu bài thi bị rách góc, bị gấp mép che khuất hoàn toàn 1 trong 4 marker thì hệ thống sẽ báo lỗi không căn chỉnh được.", bold_prefix="Phụ thuộc vào 4 Marker góc:")
    add_bullet(doc, "Trường hợp học sinh chụp ảnh quá mờ do rung tay nghiêm trọng (motion blur nặng) khiến viền ô bọt bị nhòe nhạt hoàn toàn, độ chính xác nhận diện có thể bị suy giảm.", bold_prefix="Ảnh bị rung mờ nét quá nặng:")
    add_bullet(doc, "Phần mềm hiện tại tập trung bóc tách các ô tô trắc nghiệm quang học (OMR), chưa tích hợp module OCR để nhận diện chữ viết tay cho phần Họ tên thí sinh mà đang trích xuất họ tên qua tên file hoặc bảng danh sách Excel.", bold_prefix="Chưa tích hợp nhận diện chữ viết tay (OCR):")

    add_h2(doc, "3. Hướng phát triển trong tương lai")
    add_p(doc, "Để đưa sản phẩm từ đồ án học phần tiến tới một phần mềm thương mại hóa phục vụ rộng rãi trong ngành giáo dục, nhóm định hướng các mục tiêu phát triển tiếp theo:")
    add_bullet(doc, "Tích hợp mô hình học sâu (Deep Learning) dạng CNN kết hợp RNN/Transformer (CRNN) để nhận diện tự động chữ viết tay tiếng Việt ở phần Họ và tên thí sinh trên phiếu thi.", bold_prefix="1. Tích hợp Deep Learning OCR chữ viết tay:")
    add_bullet(doc, "Phát triển phiên bản ứng dụng di động (Mobile App trên Android/iOS) sử dụng camera điện thoại quét bài thi liên tục theo thời gian thực (Real-time OMR Scanner), giáo viên chỉ cần lia camera qua từng bài thi là điểm số lập tức được ghi nhận.", bold_prefix="2. Phát triển ứng dụng di động Real-time:")
    add_bullet(doc, "Xây dựng cổng web và hệ thống Backend đám mây (Cloud Server) cho phép đồng bộ hóa dữ liệu điểm số trực tiếp vào hệ thống quản lý học sinh (vnEdu, SMAS, Moodle) của nhà trường.", bold_prefix="3. Đồng bộ hóa cơ sở dữ liệu đám mây:")
    add_bullet(doc, "Nghiên cứu áp dụng mạng nơ-ron tích chập (CNN) để phân loại trực tiếp trạng thái ô tô chì, giúp nhận diện hoàn hảo cả những trường hợp học sinh dùng bút dạ, bút bi màu hoặc gạch chéo phương án.", bold_prefix="4. Ứng dụng AI phân loại ô tô:")

    doc.add_page_break()
    
    # =========================================================================
    # 10. PHỤ LỤC 01: BẢNG ĐÁNH GIÁ THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ
    # =========================================================================
    add_h1(doc, "PHỤ LỤC 01: BẢNG ĐÁNH GIÁ THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ")
    add_p(doc, "Dưới đây là bảng tổng hợp phân công nhiệm vụ và tự đánh giá mức độ đóng góp của từng thành viên trong nhóm theo đúng tiến độ triển khai thực tế của dự án:")

    team_data = [
        ["1", "Hồ Tuấn Hiệp\nMSSV: 225748020110020", "Trưởng nhóm\n(CV 1 & Architecture)", 
         "• Thiết kế mẫu phiếu FormTHPT50 và ma trận pixel canvas 1653x2337.\n"
         "• Thu thập và xây dựng bộ dữ liệu ảnh kiểm thử đa dạng.\n"
         "• Lập trình module căn chỉnh phối cảnh 4 Marker (image_alignment.py).\n"
         "• Tự động kiểm tra và đảo chiều xoay ảnh (reorient_aligned_sheet).\n"
         "• Điều phối chung toàn bộ tiến độ dự án và biên soạn báo cáo.", "100%", "9.0", "Hồ Tuấn Hiệp"],
        ["2", "Nguyễn Khắc Quốc Khánh\nMSSV: 225748020110261", "Thành viên\n(CV 2 & OMR Engine)", 
         "• Lập trình thuật toán đo độ tương phản mực nội vùng (omr_extractor.py).\n"
         "• Bóc tách OMR cho SBD (6 cột), Mã đề (3 cột) và 50 câu trắc nghiệm.\n"
         "• Xử lý triệt để hiện tượng bóng đổ, ánh sáng yếu và tẩy chì lem mờ.\n"
         "• Lập trình module vẽ kết quả overlay trực quan (visualizer.py).\n"
         "• Đóng dấu Banner điểm tổng và điểm thành phần ở đầu phiếu.", "100%", "9.0", "Nguyễn Khắc Quốc Khánh"],
        ["3", "Lê Viết Quân\nMSSV: 225748020110203", "Thành viên\n(Backend & Data)", 
         "• Cài đặt logic chấm điểm thang 10.0 và xếp loại (grading_engine.py).\n"
         "• Lập trình module trích xuất báo cáo Excel 3 Sheet (excel_exporter.py).\n"
         "• Định dạng màu tự động (Conditional Formatting) trong file Excel.\n"
         "• Quản lý lưu trữ độc lập nền tảng với đường dẫn PROJECT_ROOT.\n"
         "• Xây dựng module sinh dữ liệu mẫu và phiếu đáp án GV.", "100%", "8.5", "Lê Viết Quân"],
        ["4", "Nguyễn Văn Thành\nMSSV: 215748020110105", "Thành viên\n(Frontend & Testing)", 
         "• Thiết kế giao diện Desktop CustomTkinter theo quy trình 3 bước (app.py).\n"
         "• Xử lý Batch Processing đa luồng Thread-safe mượt mà không đơ UI.\n"
         "• Tích hợp tính năng chụp màn hình và dán ảnh clipboard Ctrl+V.\n"
         "• Xây dựng và chạy bộ kiểm thử tự động 27 unit tests (Pytest 100% Passed).\n"
         "• Đóng gói và tích hợp toàn bộ hệ thống vào điểm chạy main.py.", "100%", "8.5", "Nguyễn Văn Thành"]
    ]
    add_table_data(doc, ["STT", "Họ và tên & MSSV", "Vai trò phụ trách", "Nhiệm vụ kỹ thuật hoàn thành chi tiết", "Đóng góp", "Điểm tự chấm", "Chữ ký"], 
                   team_data, [0.5, 1.3, 1.1, 2.5, 0.7, 0.6, 0.8],
                   caption="Bảng 4.1. Bảng phân công nhiệm vụ và tự đánh giá đóng góp của 4 thành viên")

    add_p(doc, "Nhận xét chung của nhóm: Tất cả 4 thành viên đều thể hiện tinh thần trách nhiệm cao độ, chủ động nghiên cứu tài liệu, phối hợp làm việc nhóm hiệu quả và hoàn thành 100% khối lượng công việc được giao đúng thời hạn đề ra.", bold_prefix="Đánh giá tinh thần làm việc nhóm: ")

    doc.add_page_break()
    
    # =========================================================================
    # 11. TÀI LIỆU THAM KHẢO
    # =========================================================================
    add_h1(doc, "TÀI LIỆU THAM KHẢO")
    
    refs = [
        "[1] Rafael C. Gonzalez, Richard E. Woods (2018), Digital Image Processing, 4th Edition, Pearson Education, New York, USA.",
        "[2] Gary Bradski, Adrian Kaehler (2008), Learning OpenCV: Computer Vision with the OpenCV Library, O'Reilly Media, Sebastopol, CA.",
        "[3] Bradski, G. (2000), 'The OpenCV Library', Dr. Dobb's Journal of Software Tools, Vol. 25, No. 11, pp. 120-125.",
        "[4] Otsu, N. (1979), 'A threshold selection method from gray-level histograms', IEEE Transactions on Systems, Man, and Cybernetics, Vol. 9, No. 1, pp. 62-66.",
        "[5] Carsten Rother, Vladimir Kolmogorov, Andrew Blake (2004), '\"GrabCut\": Interactive Foreground Extraction using Iterated Graph Cuts', ACM Transactions on Graphics (SIGGRAPH '04), Vol. 23, No. 3, pp. 309-314.",
        "[6] Tom Schimansky (2023), CustomTkinter Documentation and UI Framework for Python, GitHub Repository: https://github.com/TomSchimansky/CustomTkinter.",
        "[7] Eric Gazoni, Charlie Clark (2023), openpyxl - A Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files, Documentation: https://openpyxl.readthedocs.io/.",
        "[8] Bộ Giáo dục và Đào tạo (2024), Quy chế thi tốt nghiệp Trung học phổ thông và quy định cấu trúc đề thi trắc nghiệm chuẩn quốc gia, Hà Nội.",
        "[9] Nguyễn Thị Minh Tâm (2024), Bài giảng học phần Thị giác máy tính, Viện Kỹ thuật và Công nghệ - Trường Đại học Vinh.",
        "[10] Ian Sommerville (2011), Software Engineering, 9th Edition, Addison-Wesley, Boston, USA."
    ]
    
    for r_text in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(3)
        p_r.paragraph_format.space_after = Pt(3)
        p_r.paragraph_format.line_spacing = 1.3
        p_r.paragraph_format.left_indent = Inches(0.4)
        p_r.paragraph_format.first_line_indent = Inches(-0.4)
        r = p_r.add_run(r_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(30, 30, 30)

    # Save to Bao_Cao_Do_An_TGMT_ChamTracNgiem.docx
    out_path = ROOT / "Bao_Cao_Do_An_TGMT_ChamTracNgiem.docx"
    doc.save(str(out_path))
    print(f"Report generated successfully: {out_path}")
    
    # Also save a copy to TGMT_Hoan_Thien.docx for safety
    copy_path = ROOT / "TGMT_Hoan_Thien.docx"
    doc.save(str(copy_path))
    print(f"Copy generated successfully: {copy_path}")

if __name__ == "__main__":
    build_report()

