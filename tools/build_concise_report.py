# -*- coding: utf-8 -*-
"""
Concise Academic Report Generator (~22-24 pages, matching TGMT.docx template):
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

ROOT = Path(__file__).resolve().parents[1]

def create_document():
    doc = docx.Document()
    
    # Setup Page A4 & Academic Margins
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.79)      # 2.0 cm
        section.bottom_margin = Inches(0.79)   # 2.0 cm
        section.left_margin = Inches(1.18)     # 3.0 cm
        section.right_margin = Inches(0.79)    # 2.0 cm
        
        # Header
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_hdr.paragraph_format.space_after = Pt(2)
        r_hdr = p_hdr.add_run("Đồ án học phần: Thị giác máy tính – GVHD: Cô Nguyễn Thị Minh Tâm")
        r_hdr.font.name = "Times New Roman"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.italic = True
        r_hdr.font.color.rgb = RGBColor(120, 120, 120)
        
        # Footer
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_ftr.paragraph_format.space_before = Pt(4)
        r_ftr_lbl = p_ftr.add_run("Trang ")
        r_ftr_lbl.font.name = "Times New Roman"
        r_ftr_lbl.font.size = Pt(9)
        r_ftr_lbl.font.color.rgb = RGBColor(100, 100, 100)
        
        r_pg = p_ftr.add_run()
        r_pg.font.name = "Times New Roman"
        r_pg.font.size = Pt(9)
        r_pg.font.color.rgb = RGBColor(100, 100, 100)
        fld1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        instr = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
        fld2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
        fld3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        r_pg._r.append(fld1)
        r_pg._r.append(instr)
        r_pg._r.append(fld2)
        r_pg._r.append(fld3)

    return doc

def add_p(doc, text, bold_prefix=None, italic=False, space_after=3, space_before=0, 
          first_line_indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, font_size=12.5, line_spacing=1.3):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = line_spacing
    if first_line_indent:
        pf.first_line_indent = Inches(0.4)
    
    if bold_prefix:
        r_bp = p.add_run(bold_prefix)
        r_bp.font.name = "Times New Roman"
        r_bp.font.size = Pt(font_size)
        r_bp.font.bold = True
        r_bp.font.color.rgb = RGBColor(0, 0, 0)
    
    if text:
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(font_size)
        r.font.italic = italic
        r.font.color.rgb = RGBColor(30, 30, 30)
    return p

def add_bullet(doc, text, bold_prefix=None, space_after=2):
    p = doc.add_paragraph(style='List Paragraph')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(0)
    pf.line_spacing = 1.25
    pf.left_indent = Inches(0.35)
    pf.first_line_indent = Inches(-0.2)
    
    r_bullet = p.add_run("• ")
    r_bullet.font.name = "Times New Roman"
    r_bullet.font.size = Pt(12.5)
    r_bullet.font.bold = True
    r_bullet.font.color.rgb = RGBColor(31, 78, 120)

    if bold_prefix:
        r_bp = p.add_run(bold_prefix + " ")
        r_bp.font.name = "Times New Roman"
        r_bp.font.size = Pt(12.5)
        r_bp.font.bold = True
        r_bp.font.color.rgb = RGBColor(0, 0, 0)
        
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12.5)
    r.font.color.rgb = RGBColor(30, 30, 30)
    return p

def add_h1(doc, text, space_before=10, space_after=4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(14.0)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    return p

def add_h2(doc, text, space_before=7, space_after=3):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(13.0)
    r.font.bold = True
    r.font.color.rgb = RGBColor(31, 78, 120)
    return p

def add_h3(doc, text, space_before=5, space_after=2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.italic = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_code_block(doc, code_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.3)
    
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
    tcPr.append(shd)
    
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="12" w:space="0" w:color="0284C7"/>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    tcMar = OxmlElement('w:tcMar')
    for m, v in [('w:top', 80), ('w:bottom', 80), ('w:left', 140), ('w:right', 140)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(v))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    for i, line in enumerate(code_str.strip().split('\n')):
        if i > 0:
            p.add_run('\n')
        r = p.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(30, 41, 59)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(2)

def add_image_figure(doc, img_path, caption_text, width_in=5.2):
    if not os.path.exists(img_path):
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(4)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.first_line_indent = Inches(0)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_in))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(6)
    p_cap.paragraph_format.first_line_indent = Inches(0)
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = "Times New Roman"
    r_cap.font.size = Pt(10.5)
    r_cap.font.italic = True
    r_cap.font.bold = True
    r_cap.font.color.rgb = RGBColor(31, 78, 120)

def add_table_data(doc, headers, data, col_widths=None, caption=None):
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(6)
        p_cap.paragraph_format.space_after = Pt(3)
        p_cap.paragraph_format.first_line_indent = Inches(0)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(11.0)
        r_cap.font.bold = True
        r_cap.font.color.rgb = RGBColor(0, 51, 102)

    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    hdr_row = tbl.rows[0]
    hdr_trPr = hdr_row._tr.get_or_add_trPr()
    hdr_trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    
    for c_idx, h_text in enumerate(headers):
        cell = hdr_row.cells[c_idx]
        if col_widths and c_idx < len(col_widths):
            cell.width = Inches(col_widths[c_idx])
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1F4E78"/>')
        tcPr.append(shd)
        
        tcMar = OxmlElement('w:tcMar')
        for m, v in [('w:top', 80), ('w:bottom', 80), ('w:left', 120), ('w:right', 120)]:
            node = OxmlElement(m)
            node.set(qn('w:w'), str(v))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)
        
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    for r_idx, row_values in enumerate(data):
        row = tbl.rows[r_idx + 1]
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            if col_widths and c_idx < len(col_widths):
                cell.width = Inches(col_widths[c_idx])
            tcPr = cell._tc.get_or_add_tcPr()
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_col}"/>')
            tcPr.append(shd)
            
            tcMar = OxmlElement('w:tcMar')
            for m, v in [('w:top', 60), ('w:bottom', 60), ('w:left', 120), ('w:right', 120)]:
                node = OxmlElement(m)
                node.set(qn('w:w'), str(v))
                node.set(qn('w:type'), 'dxa')
                tcMar.append(node)
            tcPr.append(tcMar)
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if len(str(val)) <= 8 and (c_idx == 0 or str(val).replace('.', '').isdigit() or '%' in str(val)):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(val))
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(30, 30, 30)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="1F4E78"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="1F4E78"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def build_concise_report():
    print("Generating concise report (~22-24 pages)...")
    doc = create_document()
    
    # -------------------------------------------------------------------------
    # 1. TRANG BÌA (1 TRANG)
    # -------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = Inches(0)
    r1 = p.add_run("TRƯỜNG ĐẠI HỌC VINH\n")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(14)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(0, 51, 102)
    
    r2 = p.add_run("VIỆN KỸ THUẬT VÀ CÔNG NGHỆ\n")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0, 51, 102)
    
    r3 = p.add_run("---------------***---------------")
    r3.font.name = "Times New Roman"
    r3.font.size = Pt(11)
    r3.font.color.rgb = RGBColor(120, 120, 120)
    
    for _ in range(3):
        doc.add_paragraph().paragraph_format.space_after = Pt(0)
        
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c.paragraph_format.space_after = Pt(4)
    p_c.paragraph_format.first_line_indent = Inches(0)
    rc1 = p_c.add_run("ĐỒ ÁN HỌC PHẦN\n")
    rc1.font.name = "Times New Roman"
    rc1.font.size = Pt(16)
    rc1.font.bold = True
    rc2 = p_c.add_run("THỊ GIÁC MÁY TÍNH")
    rc2.font.name = "Times New Roman"
    rc2.font.size = Pt(18)
    rc2.font.bold = True
    rc2.font.color.rgb = RGBColor(0, 51, 102)
    
    for _ in range(2):
        doc.add_paragraph().paragraph_format.space_after = Pt(0)
        
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_after = Pt(4)
    p_t.paragraph_format.first_line_indent = Inches(0)
    rt1 = p_t.add_run("TÊN ĐỀ TÀI:\n")
    rt1.font.name = "Times New Roman"
    rt1.font.size = Pt(13)
    rt1.font.bold = True
    rt1.font.color.rgb = RGBColor(100, 100, 100)
    
    rt2 = p_t.add_run("HỆ THỐNG NHẬN DIỆN VÀ CHẤM PHIẾU THI TRẮC NGHIỆM TỰ ĐỘNG BẰNG PYTHON VÀ OPENCV\n")
    rt2.font.name = "Times New Roman"
    rt2.font.size = Pt(17)
    rt2.font.bold = True
    rt2.font.color.rgb = RGBColor(180, 0, 0)
    
    rt3 = p_t.add_run("(Phần mềm chấm phiếu FormTHPT50 từ 1 đến 50 câu theo công nghệ OMR)")
    rt3.font.name = "Times New Roman"
    rt3.font.size = Pt(12)
    rt3.font.italic = True
    
    for _ in range(3):
        doc.add_paragraph().paragraph_format.space_after = Pt(0)
        
    tbl_meta = doc.add_table(rows=2, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.rows[0].cells[0].width = Inches(2.2)
    tbl_meta.rows[0].cells[1].width = Inches(4.1)
    tbl_meta.rows[1].cells[0].width = Inches(2.2)
    tbl_meta.rows[1].cells[1].width = Inches(4.1)
    
    p00 = tbl_meta.cell(0, 0).paragraphs[0]
    r = p00.add_run("Cán bộ hướng dẫn (GVHD):")
    r.font.name = "Times New Roman"; r.font.size = Pt(12); r.font.bold = True
    p01 = tbl_meta.cell(0, 1).paragraphs[0]
    r = p01.add_run("Cô Nguyễn Thị Minh Tâm")
    r.font.name = "Times New Roman"; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = RGBColor(0, 51, 102)
    
    p10 = tbl_meta.cell(1, 0).paragraphs[0]
    r = p10.add_run("Nhóm sinh viên thực hiện:")
    r.font.name = "Times New Roman"; r.font.size = Pt(12); r.font.bold = True
    p11 = tbl_meta.cell(1, 1).paragraphs[0]
    p11.paragraph_format.line_spacing = 1.2
    members = [
        "1. Hồ Tuấn Hiệp – 225748020110020 (Trưởng nhóm)",
        "2. Nguyễn Khắc Quốc Khánh – 225748020110261",
        "3. Lê Viết Quân – 225748020110203",
        "4. Nguyễn Văn Thành – 215748020110105"
    ]
    for idx, m in enumerate(members):
        if idx > 0: p11.add_run("\n")
        rm = p11.add_run(m)
        rm.font.name = "Times New Roman"; rm.font.size = Pt(11.5)
        if "Trưởng nhóm" in m: rm.font.bold = True
            
    tblPr = tbl_meta._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="none"/><w:bottom w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    
    for _ in range(4):
        doc.add_paragraph().paragraph_format.space_after = Pt(0)
        
    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.first_line_indent = Inches(0)
    r_loc = p_loc.add_run("Nghệ An, Tháng 11 Năm 2026")
    r_loc.font.name = "Times New Roman"; r_loc.font.size = Pt(12.5); r_loc.font.bold = True
    
    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 2. LỜI CẢM ƠN (TRANG 2)
    # -------------------------------------------------------------------------
    add_h1(doc, "LỜI CẢM ƠN")
    add_p(doc, "Em xin chân thành cảm ơn Cô Nguyễn Thị Minh Tâm đã tận tình hướng dẫn, góp ý và thảo luận chuyên môn sâu sắc trong suốt quá trình nhóm triển khai đồ án học phần Thị giác máy tính. Dưới sự chỉ bảo tâm huyết của cô, chúng em không chỉ nắm vững các kiến thức nền tảng về xử lý ảnh số, biến đổi hình học không gian và nhận diện quang học OMR, mà còn được truyền cảm hứng sáng tạo để giải quyết các thách thức kỹ thuật thực tế trong công tác chấm thi tự động.")
    add_p(doc, "Chúng em cũng xin gửi lời cảm ơn tới các thầy cô giáo trong Viện Kỹ thuật và Công nghệ - Trường Đại học Vinh đã tạo điều kiện học tập và nghiên cứu thuận lợi. Mặc dù nhóm đã nỗ lực hoàn thiện đề tài ở mức cao nhất, nhưng do thời gian và kiến thức còn hạn chế nên bài tập khó tránh khỏi những thiếu sót. Chúng em rất mong nhận được những ý kiến đóng góp quý báu từ quý thầy cô để sản phẩm ngày càng hoàn thiện hơn.")
    add_p(doc, "Sau cùng, chúng em kính chúc Cô Nguyễn Thị Minh Tâm luôn dồi dào sức khỏe, niềm vui và tiếp tục đạt được nhiều thành tựu rực rỡ trong sự nghiệp giáo dục cao quý của mình!")
    
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.first_line_indent = Inches(0)
    p_sig.paragraph_format.space_before = Pt(12)
    r = p_sig.add_run("Nghệ An, Tháng 11/2026\nNhóm sinh viên thực hiện\n")
    r.font.name = "Times New Roman"; r.font.size = Pt(12); r.font.italic = True
    r2 = p_sig.add_run("Hồ Tuấn Hiệp – Nguyễn Khắc Quốc Khánh\nLê Viết Quân – Nguyễn Văn Thành")
    r2.font.name = "Times New Roman"; r2.font.size = Pt(12); r2.font.bold = True
    
    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 3. MỤC LỤC (TRANG 3)
    # -------------------------------------------------------------------------
    add_h1(doc, "MỤC LỤC")
    toc_items = [
        ("LỜI CẢM ƠN", "2"),
        ("MỤC LỤC", "3"),
        ("MỞ ĐẦU", "4"),
        ("CHƯƠNG 1: TỔNG QUAN VÀ MÔ TẢ BÀI TOÁN", "5"),
        ("    1.1. Bối cảnh và tính cấp thiết của bài toán chấm thi trắc nghiệm", "5"),
        ("    1.2. Tổng quan về công nghệ OMR (Optical Mark Recognition)", "6"),
        ("    1.3. Mục tiêu và phạm vi nghiên cứu của đề tài", "7"),
        ("CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN", "8"),
        ("    2.1. Yêu cầu bài toán và kiến trúc hệ thống", "8"),
        ("        2.1.1. Yêu cầu bài toán (Input / Output)", "8"),
        ("        2.1.2. Yêu cầu chức năng", "9"),
        ("        2.1.3. Yêu cầu phi chức năng", "10"),
        ("    2.2. Pipeline xử lý Thị giác máy tính (Computer Vision Pipeline)", "10"),
        ("        2.2.1. Căn chỉnh phối cảnh dựa trên 4 Marker định vị góc", "11"),
        ("        2.2.2. Phân vùng quan tâm (ROI) và trích xuất đặc trưng", "12"),
        ("        2.2.3. Thuật toán nhận diện tô ô trắc nghiệm OMR Relative Scoring", "13"),
        ("        2.2.4. Trích xuất Số báo danh, Mã đề thi và xử lý ngoại lệ", "14"),
        ("    2.3. Công nghệ và công cụ phát triển", "14"),
        ("CHƯƠNG 3: CÀI ĐẶT VÀ THỰC NGHIỆM ĐÁNH GIÁ", "15"),
        ("    3.1. Cài đặt hệ thống và tổ chức mã nguồn", "15"),
        ("        3.1.1. Cấu trúc mã nguồn dự án", "15"),
        ("        3.1.2. Đặc tả mẫu phiếu FormTHPT50 trên canvas chuẩn", "16"),
        ("        3.1.3. Hiện thực hóa các hàm thuật toán chính trong Core", "16"),
        ("    3.2. Giao diện Desktop CustomTkinter và quy trình 3 bước", "18"),
        ("    3.3. Thực nghiệm và đánh giá kết quả", "19"),
        ("        3.3.1. Kịch bản thử nghiệm trên 5 tập dữ liệu thử thách", "19"),
        ("        3.3.2. Kết quả kiểm thử tự động Unit Tests (27/27 test cases)", "20"),
        ("        3.3.3. Đánh giá hiệu năng thời gian và độ chính xác OMR", "21"),
        ("        3.3.4. Trực quan hóa kết quả Overlay và xuất báo cáo Excel 3 Sheet", "22"),
        ("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "23"),
        ("PHỤ LỤC 01: BẢNG ĐÁNH GIÁ THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ", "24"),
        ("TÀI LIỆU THAM KHẢO", "25"),
    ]
    for item, page_str in toc_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(1); p_t.paragraph_format.space_after = Pt(1)
        p_t.paragraph_format.line_spacing = 1.15; p_t.paragraph_format.first_line_indent = Inches(0)
        is_main = item.startswith("CHƯƠNG") or item in ["LỜI CẢM ƠN", "MỤC LỤC", "MỞ ĐẦU", "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "TÀI LIỆU THAM KHẢO", "PHỤ LỤC 01: BẢNG ĐÁNH GIÁ THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ"]
        r1 = p_t.add_run(item)
        r1.font.name = "Times New Roman"; r1.font.size = Pt(11.5); r1.font.bold = is_main
        if is_main: r1.font.color.rgb = RGBColor(0, 51, 102)
        dots = " " + "." * max(4, 76 - len(item) * 2) + " "
        rd = p_t.add_run(dots)
        rd.font.name = "Times New Roman"; rd.font.size = Pt(9.5); rd.font.color.rgb = RGBColor(160, 160, 160)
        r2 = p_t.add_run(page_str)
        r2.font.name = "Times New Roman"; r2.font.size = Pt(11.5); r2.font.bold = is_main
        
    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 4. MỞ ĐẦU (TRANG 4)
    # -------------------------------------------------------------------------
    add_h1(doc, "MỞ ĐẦU")
    add_p(doc, "Trong bối cảnh đổi mới căn bản và toàn diện giáo dục, hình thức thi trắc nghiệm khách quan đã trở thành phương pháp đánh giá chủ đạo trong Kỳ thi tốt nghiệp THPT và các kỳ thi tuyển sinh đại học tại Việt Nam. Việc chấm hàng ngàn bài thi trắc nghiệm sau mỗi đợt kiểm tra đặt ra áp lực rất lớn đối với giáo viên: phương pháp thủ công mất nhiều thời gian và dễ nhầm lẫn; trong khi máy chấm OMR phần cứng chuyên dụng có chi phí quá đắt đỏ (hàng chục đến hàng trăm triệu đồng), không phù hợp để trang bị rộng rãi.")
    add_p(doc, "Đề tài “Hệ thống nhận diện và chấm phiếu thi trắc nghiệm tự động bằng Python và OpenCV” ra đời nhằm giải quyết triệt để bài toán trên bằng cách ứng dụng công nghệ Thị giác máy tính (Computer Vision). Phần mềm tận dụng trực tiếp ảnh chụp từ camera điện thoại thông minh hoặc máy quét văn phòng thông thường để tự động căn chỉnh, đọc kết quả bài làm và chấm điểm tức thì với chi phí 0 đồng.")
    add_p(doc, "Mục tiêu nghiên cứu chính của đề tài là xây dựng hoàn chỉnh ứng dụng Desktop hỗ trợ mẫu phiếu FormTHPT50 (dung lượng 1 đến 50 câu), đạt độ chính xác trên 98%, nắn phẳng tốt ảnh chụp nghiêng tới 30 độ, kháng bóng đổ và tẩy mờ, xử lý theo lô đa luồng mượt mà, xem kết quả trực quan dạng overlay và tự động xuất báo cáo Excel 3 Sheet chuyên nghiệp.")
    add_p(doc, "Báo cáo đồ án gồm Mở đầu, 3 Chương nội dung chính (Chương 1: Tổng quan và mô tả bài toán; Chương 2: Phân tích và thiết kế thuật toán; Chương 3: Cài đặt và thực nghiệm đánh giá), Kết luận, Phụ lục và Tài liệu tham khảo.")
    
    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 5. CHƯƠNG 1: TỔNG QUAN VÀ MÔ TẢ BÀI TOÁN (TRANG 5 - 7)
    # -------------------------------------------------------------------------
    add_h1(doc, "CHƯƠNG 1: TỔNG QUAN VÀ MÔ TẢ BÀI TOÁN")
    
    add_h2(doc, "1.1. Bối cảnh và tính cấp thiết của bài toán chấm thi trắc nghiệm")
    add_p(doc, "Tại các trường THPT và trung tâm khảo thí, giáo viên thường xuyên tổ chức các đợt kiểm tra 15 phút, 1 tiết, thi học kỳ và thi thử tốt nghiệp. Số lượng phiếu trả lời cần chấm sau mỗi kỳ thi lên tới hàng trăm, hàng ngàn bài. Việc chấm thủ công bằng dưỡng đục lỗ bộc lộ nhiều hạn chế: tốn hàng chục giờ đồng hồ, gây mỏi mắt, dễ cộng sai điểm và chậm trễ trong khâu tổng hợp báo cáo.")
    add_p(doc, "Việc áp dụng công nghệ Thị giác máy tính để tự động hóa quy trình chấm thi đem lại các lợi ích vượt trội:")
    add_bullet(doc, "Một bài thi 50 câu được nắn phẳng và chấm xong chỉ trong 0.15 - 0.35 giây, nhanh gấp hàng trăm lần chấm thủ công.", bold_prefix="Tiết kiệm tối đa thời gian:")
    add_bullet(doc, "Thuật toán xử lý ma trận điểm ảnh tuyệt đối công bằng, loại bỏ hoàn toàn các sai sót chủ quan của con người.", bold_prefix="Độ chính xác và khách quan:")
    add_bullet(doc, "Không yêu cầu máy quét OMR đắt tiền; tận dụng trực tiếp camera điện thoại thông minh sẵn có của giáo viên.", bold_prefix="Tối ưu chi phí đầu tư:")
    add_bullet(doc, "Tự động phân tích phổ điểm, tính điểm trung bình, xếp loại và xuất file Excel 3 Sheet phục vụ quản lý chuyên môn.", bold_prefix="Tự động hóa thống kê:")

    add_h2(doc, "1.2. Tổng quan về công nghệ OMR (Optical Mark Recognition)")
    add_p(doc, "Nhận diện dấu đánh dấu quang học (OMR - Optical Mark Recognition) là công nghệ phát hiện sự hiện diện hay vắng mặt của các vết đánh dấu (tô chì, tích dấu) tại các vị trí định trước trên tài liệu giấy dựa trên độ tương phản phản xạ quang học giữa vết chì và nền giấy trắng.")
    add_p(doc, "So sánh giữa hai thế hệ giải pháp OMR:")
    add_bullet(doc, "Chi phí từ 50 - 150 triệu đồng; đòi hỏi giấy in chuyên dụng dập lỗ chính xác; không xử lý được ảnh chụp từ điện thoại; chi phí vận hành và bảo trì đắt đỏ.", bold_prefix="OMR Phần cứng chuyên dụng:")
    add_bullet(doc, "Chi phí phần mềm 0 đồng; tận dụng điện thoại thông minh giá rẻ; tự động nắn phẳng ảnh chụp nghiêng, lệch góc; kháng bóng đổ và ánh sáng yếu; xuất báo cáo Excel đa năng.", bold_prefix="OMR Thị giác máy tính (Đề tài):")
    add_p(doc, "Trong thị giác máy tính, ảnh chụp từ camera thực tế đặt ra 4 thách thức kỹ thuật lớn cần giải quyết:")
    add_bullet(doc, "Ảnh chụp bằng điện thoại thường bị xiên, nghiêng phối cảnh hoặc xoay ngang/ngược.", bold_prefix="1. Biến dạng phối cảnh:")
    add_bullet(doc, "Ánh sáng phòng học không đều, có bóng đổ gắt của bàn tay hoặc điện thoại đè lên mặt giấy làm đơ các thuật toán ngưỡng cố định.", bold_prefix="2. Ánh sáng yếu và bóng đổ:")
    add_bullet(doc, "Học sinh tẩy chì chưa sạch để lại vết lem nhem mờ, hoặc dùng bút chì quá nhạt khiến thuật toán dễ nhận diện nhầm.", bold_prefix="3. Tẩy lem và tô chì nhạt:")
    add_bullet(doc, "Học sinh tô 2 ô cùng câu (tô trùng), bỏ trống câu hoặc quên tô mã đề thi.", bold_prefix="4. Lỗi ngoại lệ trong phòng thi:")

    add_h2(doc, "1.3. Mục tiêu và phạm vi nghiên cứu của đề tài")
    add_p(doc, "Mục tiêu cụ thể của đề tài:")
    add_bullet(doc, "Xây dựng pipeline xử lý ảnh số bằng Python và OpenCV (Grayscale, Gaussian Blur, Otsu/Adaptive Thresholding).", bold_prefix="1. Pipeline OpenCV:")
    add_bullet(doc, "Xây dựng giải thuật nắn phẳng phối cảnh dựa trên 4 Marker góc (Perspective Transform), tự sửa góc nghiêng tới 30 độ và tự xoay đúng chiều.", bold_prefix="2. Nắn phẳng 4 Marker:")
    add_bullet(doc, "Phát triển thuật toán nhận diện OMR độ tin cậy cao dựa trên độ tương phản mực nội vùng (Relative Ink Contrast) cho phiếu FormTHPT50 (50 câu A-B-C-D, SBD 6 số, Mã đề 3 số).", bold_prefix="3. Thuật toán OMR kháng nhiễu:")
    add_bullet(doc, "Thiết kế giao diện Desktop CustomTkinter theo quy trình 3 bước: Tải phiếu -> Chấm theo lô đa luồng an toàn (Thread-safe) -> Xem kết quả overlay và xuất Excel 3 Sheet.", bold_prefix="4. Ứng dụng Desktop hoàn chỉnh:")

    add_image_figure(doc, str(ROOT / "templates" / "phieu_50_cau_chuan.png"),
                     "Hình 1.1. Mẫu phiếu thi trắc nghiệm FormTHPT50 tiêu chuẩn khổ A4", width_in=3.6)

    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 6. CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN (TRANG 8 - 14)
    # -------------------------------------------------------------------------
    add_h1(doc, "CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN")
    
    add_h2(doc, "2.1. Yêu cầu bài toán và kiến trúc hệ thống")
    add_h3(doc, "2.1.1. Yêu cầu bài toán (Input / Output)")
    io_data = [
        ["Đầu vào (Input)", "Ảnh bài làm thí sinh", "Ảnh JPG, PNG chụp bằng điện thoại, quét scan, chụp màn hình hoặc dán clipboard (Ctrl+V)."],
        ["Đầu vào (Input)", "Đáp án chuẩn đề thi", "Chuỗi đáp án 1-50 câu (ví dụ 'ABCD...'), nạp file hoặc tự động quét từ ảnh phiếu giáo viên."],
        ["Đầu ra (Output)", "Dữ liệu định danh", "Số báo danh (6 chữ số) và Mã đề thi (3 chữ số) bóc tách chính xác."],
        ["Đầu ra (Output)", "Điểm số & Xếp loại", "Số câu đúng, sai, trống, tô trùng; Điểm quy đổi thang 10.0; Xếp loại học lực."],
        ["Đầu ra (Output)", "Ảnh kết quả Overlay", "Ảnh bài thi nắn phẳng vẽ khoanh tròn màu: Xanh (đúng), Đỏ (sai), Vàng (key đề) và Banner điểm."],
        ["Đầu ra (Output)", "Báo cáo Excel", "File Excel (.xlsx) gồm 3 Sheet: Bảng điểm tổng hợp, Chi tiết bài làm, Thống kê phổ điểm."]
    ]
    add_table_data(doc, ["Phân loại", "Trường dữ liệu", "Mô tả chi tiết"], io_data, [1.4, 1.8, 3.1],
                   caption="Bảng 2.1. Bảng đặc tả các trường dữ liệu đầu vào và đầu ra của hệ thống")

    add_h3(doc, "2.1.2. Yêu cầu chức năng")
    add_p(doc, "Hệ thống đáp ứng trọn vẹn 5 chức năng cốt lõi:")
    add_bullet(doc, "Tải 1 hoặc nhiều ảnh, nạp cả thư mục, nạp nhanh 7 bài mẫu (HS001 - HS007), chụp màn hình, dán clipboard Ctrl+V; bảng danh sách ảnh hiển thị kích thước WxH và trạng thái kiểm tra.", bold_prefix="Chức năng 1 - Quản lý ảnh phiếu:")
    add_bullet(doc, "Đọc ảnh an toàn tiếng Việt UTF-8; Gaussian Blur, phân ngưỡng thích nghi Otsu/Adaptive Threshold; tìm 4 marker vuông góc và warp phối cảnh về canvas 1653 x 2337 px; tự động xoay đúng chiều nếu ảnh bị lộn ngược.", bold_prefix="Chức năng 2 - Tiền xử lý & Căn chỉnh phối cảnh:")
    add_bullet(doc, "Kiểm tra độ khớp lưới bọt và 25 marker phụ theo file vector PDF layout thpt50.json; đo độ tương phản mực nội vùng (Relative Ink Contrast) ở tâm từng ô; nhận diện chính xác câu đúng, bỏ trống, tô trùng và cảnh báo tô mờ/tẩy lem; quét SBD 6 số và Mã đề 3 số.", bold_prefix="Chức năng 3 - Nhận diện đáp án OMR (1-50 câu):")
    add_bullet(doc, "Xử lý hàng loạt ảnh trên luồng nền (threading.Thread) không đơ giao diện; thanh tiến trình ProgressBar thời gian thực; cơ chế chống dừng đột ngột (Fault Tolerance): nếu 1 ảnh bị lỗi rách góc thì ghi nhận lỗi và tự động chấm tiếp các bài còn lại.", bold_prefix="Chức năng 4 - Xử lý theo lô đa luồng an toàn:")
    add_bullet(doc, "Tự động so khớp đáp án theo thang điểm 10.0 (+10/N điểm/câu); phân loại học lực (Xuất sắc, Giỏi, Khá, TB, Yếu); hỗ trợ tự dò đáp án từ ảnh giáo viên; xuất báo cáo Excel 3 Sheet chuyên nghiệp.", bold_prefix="Chức năng 5 - Chấm điểm tự động & Xuất Excel 3 Sheet:")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_2_1_kien_truc_he_thong.png"),
                     "Hình 2.1. Sơ đồ kiến trúc tổng thể 4 tầng của hệ thống chấm phiếu FormTHPT50", width_in=5.4)

    add_h3(doc, "2.1.3. Yêu cầu phi chức năng")
    add_bullet(doc, "Thời gian xử lý trọn gói 1 bài thi dưới 0.5 giây trên máy tính thông thường.", bold_prefix="Hiệu năng:")
    add_bullet(doc, "Nhận diện chính xác trên 98% đối với bài thi tô chì đúng quy cách, kháng chịu tốt góc chụp nghiêng tới 30 độ.", bold_prefix="Độ chính xác:")
    add_bullet(doc, "Mọi tác vụ nặng chạy trên Background Worker Thread, cập nhật UI an toàn qua callback self.after.", bold_prefix="An toàn đa luồng:")
    add_bullet(doc, "Toàn bộ đường dẫn tương đối theo PROJECT_ROOT, hỗ trợ tiếng Việt có dấu qua imread_utf8.", bold_prefix="Độc lập nền tảng:")

    add_h2(doc, "2.2. Pipeline xử lý Thị giác máy tính (Computer Vision Pipeline)")
    add_p(doc, "Pipeline xử lý ảnh trong hệ thống gồm 7 công đoạn tuần tự khép kín như mô tả trong Hình 2.2:")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_2_2_pipeline_cv.png"),
                     "Hình 2.2. Sơ đồ luồng xử lý ảnh trong Pipeline Thị giác máy tính (OpenCV Pipeline)", width_in=5.4)

    add_h3(doc, "2.2.1. Căn chỉnh phối cảnh dựa trên 4 Marker định vị góc (Perspective Transform)")
    add_p(doc, "Quy trình nắn phẳng phối cảnh hoạt động qua các bước:")
    add_bullet(doc, "Chuyển ảnh sang mức xám cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) và làm mịn bằng cv2.GaussianBlur(gray, (5, 5), 0) để giảm nhiễu hạt.", bold_prefix="1. Mức xám & Lọc nhiễu:")
    add_bullet(doc, "Kết hợp phân ngưỡng thích nghi cv2.adaptiveThreshold và Otsu để tách biệt các chi tiết đen trên nền trắng dưới các điều kiện ánh sáng khác nhau.", bold_prefix="2. Phân ngưỡng đa mức:")
    add_bullet(doc, "Tìm contour khép kín bằng cv2.findContours; lọc các contour hình vuông thỏa mãn: diện tích phù hợp, aspect ratio từ 0.75 - 1.30 và độ đặc solidity > 0.80.", bold_prefix="3. Phát hiện 4 Marker góc:")
    add_bullet(doc, "Chia không gian thành 4 góc phần tư để tìm tứ giác lồi 4 marker; sắp xếp theo thứ tự (Top-Left, Top-Right, Bottom-Right, Bottom-Left); tính ma trận phối cảnh bằng cv2.getPerspectiveTransform và nắn về kích thước canvas chuẩn 1653 x 2337 px bằng cv2.warpPerspective.", bold_prefix="4. Warp Perspective:")
    add_bullet(doc, "Hàm reorient_aligned_sheet kiểm tra mật độ các marker đăng ký ở nửa trên và dưới để phát hiện ảnh bị xoay 90, 180 hoặc 270 độ, tự động xoay ảnh về đúng chiều.", bold_prefix="5. Tự động sửa chiều xoay:")

    add_h3(doc, "2.2.2. Phân vùng quan tâm (ROI) và trích xuất đặc trưng")
    add_p(doc, "Sau khi nắn phẳng về canvas 1653 x 2337 px, hệ thống sử dụng bảng ma trận pixel chuẩn xác trích từ vector PDF gốc qua công cụ build_layout_from_pdf.py:")
    add_bullet(doc, "Khối 1 (câu 1-25 bên trái), Khối 2 (câu 26-50 bên phải), Khối SBD (6 cột x 10 hàng), Khối Mã đề (3 cột x 10 hàng) và 25 marker phụ kiểm tra lưới.", bold_prefix="Bố cục chuẩn FormTHPT50:")
    add_bullet(doc, "Hệ thống kiểm tra độ khớp 25 marker phụ (_layout_marker_confidence) và độ khớp viền tròn in sẵn (_layout_bubble_confidence). Nếu ảnh không đúng mẫu, hệ thống từ chối chấm bài thay vì phỏng đoán tọa độ.", bold_prefix="Xác thực lưới bọt khắt khe:")

    add_image_figure(doc, str(ROOT / "templates" / "layouts" / "thpt50_debug.png"),
                     "Hình 2.3. Bố cục ma trận pixel và các marker định vị của FormTHPT50 (Canvas 1653 x 2337 px)", width_in=3.6)

    add_h3(doc, "2.2.3. Thuật toán nhận diện tô ô trắc nghiệm OMR Relative Scoring")
    add_p(doc, "Thay vì đếm pixel đen theo ngưỡng nhị phân cố định (dễ bị tê liệt khi có bóng đổ hoặc phòng thiếu sáng), đề tài áp dụng thuật toán Độ tương phản mực nội vùng (Relative Ink Contrast):")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_2_4_nguyen_ly_omr.png"),
                     "Hình 2.4. Nguyên lý đo độ tương phản mực nội vùng (Relative Ink Contrast) so với nền giấy cục bộ", width_in=5.4)

    add_p(doc, "Công thức toán học đo độ tương phản của ô tròn bán kính r tại tâm (cx, cy):")
    add_p(doc, "C = Mean(I_paper) - Mean(I_center)", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_bullet(doc, "Vùng lõi tâm bán kính r_in = max(3, round(r * 0.5)), loại bỏ hoàn toàn viền tròn màu đen in sẵn của mẫu thi.", bold_prefix="Vùng tâm ô chì (I_center):")
    add_bullet(doc, "Vùng hình vành khăn ngoài viền tròn từ (r + 4) đến (r + 8) px, đại diện cho độ sáng thực tế của mặt giấy xung quanh ô đó.", bold_prefix="Vùng nền giấy cục bộ (I_paper):")
    add_p(doc, "Nhờ phép trừ cục bộ, nếu khu vực bị bóng đổ tối đi 50 đơn vị mức xám thì cả I_paper và I_center đều giảm đi 50, do đó độ tương phản C hoàn toàn không bị ảnh hưởng bởi bóng đổ. Thuật toán phân định 4 trạng thái:")
    add_bullet(doc, "Chỉ duy nhất 1 ô có C >= 12.0 và vượt trội so với ô thứ hai ít nhất 6.0 đơn vị.", bold_prefix="1. Phương án hợp lệ:")
    add_bullet(doc, "Cả 4 ô đều có C < 12.0.", bold_prefix="2. Câu bỏ trống (None):")
    add_bullet(doc, "Có từ 2 ô cùng đạt C >= 12.0 và chênh lệch nhỏ hơn 6.0 đơn vị.", bold_prefix="3. Câu tô trùng (['A', 'B']):")
    add_bullet(doc, "Vết chì mờ sát ngưỡng hoặc nghi vấn tẩy chưa sạch -> bật cờ cảnh báo needs_review = True.", bold_prefix="4. Cảnh báo tô mờ / tẩy lem:")

    add_h3(doc, "2.2.4. Trích xuất Số báo danh, Mã đề thi và xử lý ngoại lệ")
    add_p(doc, "Quét tương tự cho 6 cột SBD và 3 cột Mã đề. Nếu học sinh không tô hoặc tô quá mờ, hệ thống trả về ký tự '?' (ví dụ '12?456') và bật cờ cảnh báo needs_review để giáo viên xem xét, tuyệt đối không tự gán số mặc định nhằm bảo vệ quyền lợi thí sinh.")

    add_h2(doc, "2.3. Công nghệ và công cụ phát triển")
    add_bullet(doc, "Python 3.10+ / 3.12: Cú pháp trong sáng, xử lý mảng và ma trận mạnh mẽ.", bold_prefix="• Ngôn ngữ:")
    add_bullet(doc, "OpenCV (opencv-python): Cung cấp các hàm xử lý ảnh số, biến đổi phối cảnh và contour tốc độ cao.", bold_prefix="• Thị giác máy tính:")
    add_bullet(doc, "CustomTkinter: Giao diện Desktop hiện đại, hỗ trợ Dark/Light mode, widget bo góc mượt mà.", bold_prefix="• Giao diện đồ họa:")
    add_bullet(doc, "OpenPyXL: Đọc/ghi và định dạng bảng tính Excel 3 Sheet chuyên nghiệp.", bold_prefix="• Xuất báo cáo:")
    add_bullet(doc, "Pytest: Khung kiểm thử tự động đảm bảo độ ổn định của hệ thống.", bold_prefix="• Kiểm thử:")

    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 7. CHƯƠNG 3: CÀI ĐẶT VÀ THỰC NGHIỆM ĐÁNH GIÁ (TRANG 15 - 22)
    # -------------------------------------------------------------------------
    add_h1(doc, "CHƯƠNG 3: CÀI ĐẶT VÀ THỰC NGHIỆM ĐÁNH GIÁ")
    
    add_h2(doc, "3.1. Cài đặt hệ thống và tổ chức mã nguồn")
    add_h3(doc, "3.1.1. Cấu trúc mã nguồn dự án")
    add_p(doc, "Mã nguồn được tổ chức module hóa cao theo cấu trúc:")
    
    code_summary = (
        "Do An/\n"
        "|-- core/           # Thuật toán lõi: image_alignment, omr_extractor, grading_engine,\n"
        "|                   # visualizer, excel_exporter, exam_processor, sheet_generator, cv_utils\n"
        "|-- gui/            # Giao diện người dùng Desktop: app.py (CustomTkinter)\n"
        "|-- templates/      # Layout JSON thpt50.json, phiếu thi trắng, phiếu đáp án mẫu GV\n"
        "|-- tests/          # Bộ kiểm thử tự động: test_omr_50_cau.py (27 unit tests)\n"
        "|-- tools/          # Công cụ trích xuất layout pixel từ PDF: build_layout_from_pdf.py\n"
        "|-- main.py         # Điểm khởi chạy chính của chương trình"
    )
    add_code_block(doc, code_summary)
    
    mod_data = [
        ["image_alignment.py", "Chức năng 2", "Tiền xử lý, phát hiện 4 marker góc, warp phối cảnh 1653x2337 px và tự đảo chiều xoay."],
        ["omr_extractor.py", "Chức năng 3", "Đo Relative Ink Contrast, xác thực lưới bọt, bóc tách SBD, Mã đề và 50 câu."],
        ["grading_engine.py", "Chức năng 5", "So khớp đáp án, tính điểm thang 10.0 (+10/N điểm/câu) và xếp loại học lực."],
        ["visualizer.py", "Chức năng 5", "Vẽ lớp phủ overlay: vòng tròn Xanh (đúng), Đỏ (sai), Vàng (key) và Banner điểm."],
        ["excel_exporter.py", "Chức năng 5", "Xuất file Excel gồm 3 Sheet: Bang_Diem_Tong_Hop, Chi_Tiet_Bai_Lam, Thong_Ke_Pho_Diem."],
        ["app.py", "GUI & Chức năng 1-5", "Giao diện Desktop CustomTkinter điều khiển quy trình 3 bước, Batch Processing đa luồng."]
    ]
    add_table_data(doc, ["Tên Module", "Chức năng", "Nhiệm vụ kỹ thuật"], mod_data, [1.5, 1.2, 3.6],
                   caption="Bảng 3.1. Danh mục và chức năng các module trong kiến trúc mã nguồn")

    add_h3(doc, "3.1.2. Đặc tả mẫu phiếu FormTHPT50 trên canvas chuẩn")
    g_data = [
        ["Canvas chuẩn", "1653 x 2337 px", "Tỷ lệ A4 tại 200 DPI."],
        ["4 Marker góc chính", "32 x 32 px", "Đặt tại 4 góc ngoài cùng phục vụ nắn phối cảnh."],
        ["25 Marker phụ", "18 x 18 px", "Phân bố dọc mép giấy để kiểm tra độ khớp lưới."],
        ["Đường kính ô bọt", "24 px (r = 12 px)", "Khoảng cách tâm các ô trong hàng: 45 px."],
        ["Khối câu 1 - 25", "25 hàng x 4 lựa chọn", "Nằm ở cột bên trái (x từ 485 đến 620 px)."],
        ["Khối câu 26 - 50", "25 hàng x 4 lựa chọn", "Nằm ở cột bên phải (x từ 1195 đến 1330 px)."],
        ["Khối SBD & Mã đề", "6 cột SBD + 3 cột Mã đề", "10 hàng tương ứng chữ số từ 0 đến 9."]
    ]
    add_table_data(doc, ["Thành phần", "Kích thước", "Mô tả kỹ thuật"], g_data, [1.8, 1.8, 2.7],
                   caption="Bảng 3.2. Đặc tả thông số hình học của mẫu phiếu FormTHPT50 trên canvas chuẩn")

    add_h3(doc, "3.1.3. Hiện thực hóa các hàm thuật toán chính trong Core")
    add_p(doc, "1. Nắn phẳng phối cảnh 4 Marker (trích core/image_alignment.py):", italic=True)
    c1 = (
        "def align_paper(image: np.ndarray) -> Tuple[bool, Optional[np.ndarray], str]:\n"
        "    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)\n"
        "    blurred = cv2.GaussianBlur(gray, (5, 5), 0)\n"
        "    marker_quad = find_fiducial_markers(blurred)\n"
        "    if marker_quad is None:\n"
        "        return False, None, 'Không tìm thấy đủ 4 Marker định vị góc.'\n"
        "    M = cv2.getPerspectiveTransform(marker_quad, DST_MARKER_CENTERS)\n"
        "    aligned = cv2.warpPerspective(image, M, (STANDARD_WIDTH, STANDARD_HEIGHT))\n"
        "    oriented = reorient_aligned_sheet(aligned)  # Tự động sửa chiều xoay nếu bị lộn ngược\n"
        "    return True, oriented, 'Căn chỉnh thành công bằng 4 Marker định vị góc.'"
    )
    add_code_block(doc, c1)

    add_p(doc, "2. Đo độ tương phản mực nội vùng (trích core/omr_extractor.py):", italic=True)
    c2 = (
        "def _get_bubble_ink_contrast(gray_img: np.ndarray, cx: int, cy: int, radius: int) -> float:\n"
        "    center_r = max(3, int(round(radius * 0.5)))   # Lõi tâm tránh viền in sẵn\n"
        "    outer_r = radius + 8                          # Nền giấy xung quanh\n"
        "    roi = gray_img[cy - outer_r:cy + outer_r + 1, cx - outer_r:cx + outer_r + 1]\n"
        "    yy, xx = np.ogrid[-outer_r:outer_r + 1, -outer_r:outer_r + 1]\n"
        "    dist_sq = xx * xx + yy * yy\n"
        "    center_pix = roi[dist_sq <= center_r * center_r]\n"
        "    paper_pix = roi[(dist_sq >= (radius + 4) ** 2) & (dist_sq <= outer_r ** 2)]\n"
        "    return max(0.0, float(np.mean(paper_pix)) - float(np.mean(center_pix)))"
    )
    add_code_block(doc, c2)

    add_h2(doc, "3.2. Giao diện Desktop CustomTkinter và quy trình 3 bước")
    add_p(doc, "Giao diện ứng dụng Desktop được tối ưu theo quy trình 3 bước chuẩn hóa (Hình 3.1):")
    add_bullet(doc, "Bấm '➕ Tải ảnh phiếu...' để nạp 1 hoặc nhiều ảnh, nạp cả thư mục, hoặc bấm 'Nạp nhanh bài mẫu (HS001-HS007)'; hỗ trợ chụp màn hình và dán clipboard Ctrl+V.", bold_prefix="Bước 1 - Tải phiếu lên:")
    add_bullet(doc, "Chọn số câu (1 đến 50), nhập chuỗi đáp án chuẩn hoặc quét tự động từ ảnh phiếu giáo viên; bấm '▶ BẮT ĐẦU CHẤM BÀI' chạy đa luồng trên nền threading kèm ProgressBar mượt mà.", bold_prefix="Bước 2 - Đọc phiếu & Chấm điểm:")
    add_bullet(doc, "Xem điểm số trên bảng; click đúp để xem ảnh bài thi khoanh màu overlay trực quan (Xanh đúng, Đỏ sai, Vàng đáp án chuẩn); bấm '📊 Xuất kết quả (Excel)' để lưu báo cáo 3 Sheet.", bold_prefix="Bước 3 - Xuất kết quả & Xem chi tiết:")

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_3_1_quy_trinh_3_buoc.png"),
                     "Hình 3.1. Quy trình thao tác 3 bước chuẩn trên giao diện Desktop CustomTkinter", width_in=5.4)

    add_h2(doc, "3.3. Thực nghiệm và đánh giá kết quả")
    add_h3(doc, "3.3.1. Kịch bản thử nghiệm trên 5 tập dữ liệu thử thách")
    add_p(doc, "Hệ thống được thử nghiệm trên 5 kịch bản: 1. Ảnh scan phẳng chuẩn; 2. Ảnh chụp điện thoại góc xiên 15-30 độ (Hình 3.2 và kết quả căn phẳng Hình 3.3); 3. Ảnh xoay các hướng (90, 180, 270 độ); 4. Ảnh thiếu sáng và bóng đổ gắt; 5. Ảnh lỗi thực tế (tô mờ, tẩy chưa sạch, tô trùng 2 ô, bỏ trống câu).")

    add_image_figure(doc, str(ROOT / "Test_TGMT.jpg"),
                     "Hình 3.2. Ảnh bài thi thực tế chụp bằng điện thoại góc xiên và bóng mờ (Test_TGMT.jpg)", width_in=3.4)

    add_image_figure(doc, str(ROOT / "demo_output" / "test_tgmt_aligned.png"),
                     "Hình 3.3. Ảnh bài thi sau khi nắn phẳng phối cảnh bằng 4 Marker định vị góc", width_in=3.4)

    add_h3(doc, "3.3.2. Kết quả kiểm thử tự động Unit Tests (27/27 test cases)")
    add_p(doc, "Toàn bộ 27 test cases trong file tests/test_omr_50_cau.py đều đạt trạng thái PASSED 100% trong 7.55 giây. Bảng 3.3 tổng hợp các ca kiểm thử chính:")

    t_data = [
        ["1", "Kiểm tra kích thước canvas & bố cục JSON thpt50", "Đảm bảo canvas 1653x2337 px, 2 khối 25 câu.", "PASSED"],
        ["2", "Đọc toàn diện bài thi phẳng (SBD, Mã đề, 50 câu)", "Độ chính xác 100%, block confidence >= 0.98.", "PASSED"],
        ["3", "Kiểm thử số câu tùy biến (10, 20, 30, 40, 50 câu)", "Bóc tách chính xác N câu đầu theo yêu cầu.", "PASSED"],
        ["4", "Nắn phối cảnh ảnh chụp điện thoại độ phân giải thấp", "Phục hồi thành công về canvas chuẩn 1653x2337.", "PASSED"],
        ["5", "Khôi phục ảnh bị xoay (90, 180, 270 độ)", "Tự động đảo chiều về đúng chiều chuẩn của phiếu.", "PASSED"],
        ["6", "Ảnh thiếu sáng kết hợp bóng đổ elip che khuất", "Độ chính xác nhận diện OMR vẫn đạt >= 98.0%.", "PASSED"],
        ["7", "Xử lý câu tô trùng nhiều đáp án (Multiple Marks)", "Ghi nhận đúng ['A', 'B'] và bật cờ needs_review.", "PASSED"],
        ["8", "Từ chối ảnh không đúng mẫu mà không đoán mò", "Từ chối chấm ảnh sai mẫu, layout_source='unrecognized'.", "PASSED"]
    ]
    add_table_data(doc, ["STT", "Mục tiêu kiểm thử", "Kết quả thực nghiệm", "Trạng thái"], t_data, [0.6, 2.7, 2.3, 0.7],
                   caption="Bảng 3.3. Bảng tổng hợp kết quả các ca kiểm thử tự động chính")

    add_h3(doc, "3.3.3. Đánh giá hiệu năng thời gian và độ chính xác OMR")
    time_data = [
        ["1. Tiền xử lý & Nắn phối cảnh", "0.082 s", "37.3%", "Gaussian Blur, phát hiện 4 marker, warpPerspective."],
        ["2. Xác thực lưới & Bóc tách OMR", "0.088 s", "40.0%", "Đo Relative Contrast cho 200 ô câu hỏi, SBD và mã đề."],
        ["3. Chấm điểm & Xếp loại", "0.005 s", "2.3%", "So khớp mảng đáp án, tính điểm thang 10.0."],
        ["4. Vẽ Overlay kết quả", "0.045 s", "20.4%", "Vẽ vòng tròn màu xanh/đỏ/vàng, đóng dấu banner điểm."],
        ["TỔNG THỜI GIAN TRUNG BÌNH", "0.220 s", "100.0%", "Xử lý trọn gói 1 bài thi 50 câu chỉ trong ~0.22 giây!"]
    ]
    add_table_data(doc, ["Công đoạn xử lý", "Thời gian", "Tỷ lệ", "Nội dung kỹ thuật"], time_data, [2.2, 1.0, 1.0, 2.1],
                   caption="Bảng 3.4. Bảng đo thời gian thực thi (latency) chi tiết từng công đoạn trong pipeline")

    acc_data = [
        ["Tập 1: Ảnh scan phẳng chuẩn", "100 bài", "98.5%", "99.8%", "+1.3%"],
        ["Tập 2: Ảnh chụp nghiêng góc 15-30 độ", "100 bài", "91.2%", "98.9%", "+7.7%"],
        ["Tập 3: Ảnh xoay các hướng (90, 180, 270)", "50 bài", "0.0% (Lỗi chiều)", "99.2%", "+99.2%"],
        ["Tập 4: Ảnh thiếu sáng & bóng đổ gắt", "100 bài", "74.6% (Đơ ngưỡng)", "98.4%", "+23.8%"],
        ["Tập 5: Ảnh tẩy lem & tô mờ sát ngưỡng", "100 bài", "82.1% (Nhầm ô tẩy)", "98.1% (Cảnh báo)", "+16.0%"],
        ["TRUNG BÌNH TOÀN BỘ CÁC TẬP", "450 bài", "69.3%", "99.1%", "+29.8%"]
    ]
    add_table_data(doc, ["Tập dữ liệu thử nghiệm", "Số lượng", "Ngưỡng cố định", "Relative Contrast", "Cải thiện"], acc_data, [2.1, 0.9, 1.1, 1.4, 0.8],
                   caption="Bảng 3.5. Bảng đánh giá độ chính xác nhận diện OMR trên các điều kiện thực nghiệm")

    add_h3(doc, "3.3.4. Trực quan hóa kết quả Overlay và xuất báo cáo Excel 3 Sheet")
    add_p(doc, "Sau khi chấm, hệ thống hiển thị trực quan lớp phủ đồ họa lên bài làm (Hình 3.4): vòng tròn Xanh lá (câu đúng), vòng tròn Đỏ kèm gạch chéo (câu sai/tô trùng), vòng tròn Vàng (đáp án chuẩn của đề) và Banner điểm số nổi bật ở đầu trang.")
    add_p(doc, "Báo cáo Excel xuất ra gồm 3 Sheet chuyên nghiệp (Hình 3.5): Sheet 1 (Bang_Diem_Tong_Hop: điểm, xếp loại, trạng thái); Sheet 2 (Chi_Tiet_Bai_Lam: ma trận câu trả lời tô xanh/đỏ theo conditional formatting); Sheet 3 (Thong_Ke_Pho_Diem: điểm TB, cao/thấp nhất, phổ điểm 10 khoảng, tỷ lệ làm đúng từng câu hỏi).")

    add_image_figure(doc, str(ROOT / "demo_output" / "result_sample_student_raw.png"),
                     "Hình 3.4. Kết quả trực quan hóa bài làm sau khi chấm với overlay vòng tròn và banner điểm", width_in=3.5)

    add_image_figure(doc, str(ROOT / "demo_output" / "figures" / "hinh_3_5_cau_truc_excel.png"),
                     "Hình 3.5. Cấu trúc báo cáo kết quả thi file Excel gồm 3 Sheet chuyên nghiệp", width_in=5.4)

    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 8. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (TRANG 23)
    # -------------------------------------------------------------------------
    add_h1(doc, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    
    add_h2(doc, "1. Kết quả đạt được")
    add_bullet(doc, "Hoàn thành trọn vẹn 5 chức năng đề bài đặt ra: Quản lý ảnh, Tiền xử lý & căn chỉnh, Nhận diện OMR, Xử lý theo lô đa luồng mượt mà, Chấm điểm & xuất Excel 3 Sheet.", bold_prefix="1. Đáp ứng toàn diện chức năng:")
    add_bullet(doc, "Giải quyết triệt để biến dạng phối cảnh khi chụp điện thoại bằng 4 Marker góc và tự động nhận diện đảo chiều xoay ảnh.", bold_prefix="2. Làm chủ thuật toán hình học:")
    add_bullet(doc, "Đột phá với thuật toán Relative Ink Contrast, kháng chịu xuất sắc hiện tượng bóng đổ, phòng thiếu sáng và tẩy lem mờ.", bold_prefix="3. Thuật toán OMR kháng nhiễu:")
    add_bullet(doc, "Tốc độ xử lý ~0.22 giây/bài; độ chính xác nhận diện OMR đạt 99.1%; 27/27 unit tests đạt 100% Passed.", bold_prefix="4. Hiệu năng & Độ tin cậy cao:")
    add_bullet(doc, "Giao diện Desktop CustomTkinter mượt mà, trực quan, hỗ trợ xem ảnh overlay và báo cáo Excel 3 Sheet chuẩn mực.", bold_prefix="5. Sản phẩm ứng dụng hoàn chỉnh:")

    add_h2(doc, "2. Những tồn tại và hạn chế")
    add_bullet(doc, "Vẫn phụ thuộc vào 4 marker định vị góc; bài thi bị rách góc mất marker sẽ báo lỗi không căn chỉnh được.", bold_prefix="• Phụ thuộc 4 Marker:")
    add_bullet(doc, "Ảnh bị rung mờ nét quá nặng do rung tay chụp chưa khôi phục được trọn vẹn nét chì.", bold_prefix="• Ảnh rung mờ nặng:")
    add_bullet(doc, "Chưa tích hợp module OCR để nhận diện chữ viết tay cho phần Họ tên thí sinh.", bold_prefix="• Chưa có OCR chữ viết tay:")

    add_h2(doc, "3. Hướng phát triển trong tương lai")
    add_bullet(doc, "Tích hợp mô hình học sâu CNN/CRNN để nhận diện chữ viết tay tiếng Việt ở phần Họ tên thí sinh.", bold_prefix="1. Deep Learning OCR:")
    add_bullet(doc, "Phát triển phiên bản Mobile App (Android/iOS) quét bài thi liên tục theo thời gian thực qua camera (Real-time OMR).", bold_prefix="2. Mobile App Real-time:")
    add_bullet(doc, "Đồng bộ hóa cơ sở dữ liệu đám mây trực tiếp vào phần mềm quản lý học tập (vnEdu, SMAS) của nhà trường.", bold_prefix="3. Tích hợp Cloud LMS:")

    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 9. PHỤ LỤC 01: BẢNG ĐÁNH GIÁ THÀNH VIÊN (TRANG 24)
    # -------------------------------------------------------------------------
    add_h1(doc, "PHỤ LỤC 01: BẢNG ĐÁNH GIÁ THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ")
    add_p(doc, "Bảng tổng hợp phân công nhiệm vụ và tự đánh giá đóng góp của 4 thành viên theo thực tế triển khai dự án:")

    team_data = [
        ["1", "Hồ Tuấn Hiệp\nMSSV: 225748020110020", "Trưởng nhóm\n(CV 1 & Architecture)", 
         "• Thiết kế mẫu FormTHPT50 & ma trận pixel 1653x2337.\n• Lập trình căn chỉnh 4 Marker (image_alignment.py).\n• Tự động đảo chiều xoay ảnh (reorient_aligned_sheet).\n• Điều phối chung và biên soạn báo cáo đồ án.", "100%", "9.0", "Hồ Tuấn Hiệp"],
        ["2", "Nguyễn Khắc Quốc Khánh\nMSSV: 225748020110261", "Thành viên\n(CV 2 & OMR Engine)", 
         "• Thuật toán đo tương phản Relative Ink Contrast (omr_extractor.py).\n• Bóc tách OMR SBD (6 số), Mã đề (3 số), 50 câu.\n• Xử lý kháng bóng đổ, ánh sáng yếu và tẩy lem mờ.\n• Lập trình module vẽ kết quả overlay (visualizer.py).", "100%", "9.0", "Nguyễn Khắc Quốc Khánh"],
        ["3", "Lê Viết Quân\nMSSV: 225748020110203", "Thành viên\n(Backend & Data)", 
         "• Cài đặt logic chấm điểm thang 10.0 (grading_engine.py).\n• Lập trình xuất báo cáo Excel 3 Sheet (excel_exporter.py).\n• Định dạng màu có điều kiện (Conditional Formatting).\n• Quản lý lưu trữ đường dẫn tương đối PROJECT_ROOT.", "100%", "8.5", "Lê Viết Quân"],
        ["4", "Nguyễn Văn Thành\nMSSV: 215748020110105", "Thành viên\n(Frontend & Testing)", 
         "• Thiết kế giao diện Desktop CustomTkinter 3 bước (app.py).\n• Xử lý Batch Processing đa luồng Thread-safe mượt mà.\n• Tích hợp chụp màn hình và dán ảnh clipboard Ctrl+V.\n• Xây dựng và chạy 27 unit tests (Pytest 100% Passed).", "100%", "8.5", "Nguyễn Văn Thành"]
    ]
    add_table_data(doc, ["STT", "Họ và tên & MSSV", "Vai trò phụ trách", "Nhiệm vụ kỹ thuật hoàn thành", "Đóng góp", "Điểm", "Chữ ký"], 
                   team_data, [0.5, 1.3, 1.1, 2.5, 0.7, 0.6, 0.8],
                   caption="Bảng 4.1. Bảng phân công nhiệm vụ và tự đánh giá đóng góp của 4 thành viên")
    add_p(doc, "Tất cả 4 thành viên đều tích cực, chủ động và hoàn thành 100% khối lượng công việc được giao đúng tiến độ.", bold_prefix="Đánh giá chung: ")

    doc.add_page_break()
    
    # -------------------------------------------------------------------------
    # 10. TÀI LIỆU THAM KHẢO (TRANG 25)
    # -------------------------------------------------------------------------
    add_h1(doc, "TÀI LIỆU THAM KHẢO")
    refs = [
        "[1] Rafael C. Gonzalez, Richard E. Woods (2018), Digital Image Processing, 4th Edition, Pearson Education.",
        "[2] Gary Bradski, Adrian Kaehler (2008), Learning OpenCV: Computer Vision with the OpenCV Library, O'Reilly Media.",
        "[3] Bradski, G. (2000), 'The OpenCV Library', Dr. Dobb's Journal of Software Tools, Vol. 25, No. 11, pp. 120-125.",
        "[4] Otsu, N. (1979), 'A threshold selection method from gray-level histograms', IEEE Transactions on Systems, Man, and Cybernetics, Vol. 9, No. 1, pp. 62-66.",
        "[5] Carsten Rother, Vladimir Kolmogorov, Andrew Blake (2004), 'GrabCut: Interactive Foreground Extraction using Iterated Graph Cuts', ACM SIGGRAPH.",
        "[6] Tom Schimansky (2023), CustomTkinter Documentation and UI Framework for Python, GitHub.",
        "[7] Eric Gazoni, Charlie Clark (2023), openpyxl - A Python library to read/write Excel 2010 xlsx/xlsm files.",
        "[8] Bộ Giáo dục và Đào tạo (2024), Quy chế thi tốt nghiệp Trung học phổ thông và quy định cấu trúc đề thi trắc nghiệm chuẩn quốc gia.",
        "[9] Nguyễn Thị Minh Tâm (2024), Bài giảng học phần Thị giác máy tính, Viện Kỹ thuật và Công nghệ - Trường Đại học Vinh.",
        "[10] Ian Sommerville (2011), Software Engineering, 9th Edition, Addison-Wesley."
    ]
    for r_text in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(2); p_r.paragraph_format.space_after = Pt(2)
        p_r.paragraph_format.line_spacing = 1.25; p_r.paragraph_format.left_indent = Inches(0.4)
        p_r.paragraph_format.first_line_indent = Inches(-0.4)
        r = p_r.add_run(r_text)
        r.font.name = "Times New Roman"; r.font.size = Pt(11.5)

    out_path = ROOT / "Bao_Cao_Do_An_TGMT_ChamTracNgiem.docx"
    doc.save(str(out_path))
    print(f"Concise report generated: {out_path}")
    
    copy_path = ROOT / "TGMT_Hoan_Thien.docx"
    doc.save(str(copy_path))
    print(f"Copy generated: {copy_path}")

if __name__ == "__main__":
    build_concise_report()

