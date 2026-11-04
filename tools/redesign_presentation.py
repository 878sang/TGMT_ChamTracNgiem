"""Create a 17-slide, presentation-ready edition of the OMR project deck."""

from copy import deepcopy
from pathlib import Path
import subprocess
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Slide_Bao_Cao_TGMT_ChamTracNghiem.pptx"
OUTPUT = ROOT / "Slide_Bao_Cao_TGMT_ChamTracNghiem_17slides.pptx"

BG = RGBColor(11, 18, 32)
CARD = RGBColor(16, 26, 46)
CARD_ALT = RGBColor(20, 34, 60)
BORDER = RGBColor(30, 48, 77)
CYAN = RGBColor(0, 212, 255)
WHITE = RGBColor(255, 255, 255)
LIGHT = RGBColor(226, 232, 240)
MUTED = RGBColor(148, 163, 184)
GREEN = RGBColor(16, 185, 129)


def remove_shape(slide, shape):
    slide.shapes._spTree.remove(shape._element)


def add_text(slide, text, x, y, w, h, size, color, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = "Segoe UI"
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    return box


def add_bg(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG
    bg.line.fill.background()
    slide.shapes._spTree.remove(bg._element)
    slide.shapes._spTree.insert(2, bg._element)


def add_footer(slide, text):
    add_text(slide, text, 0.8, 7.06, 10.5, 0.25, 9, MUTED)


def add_page_number(slide, number):
    add_text(slide, f"{number:02d} / 17", 11.35, 0.42, 1.15, 0.28, 12, CYAN, True, PP_ALIGN.RIGHT)


def make_metrics_slide(prs, subtitle, metric_data, footer):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_text(slide, subtitle, 0.8, 0.62, 11.7, 0.85, 18, WHITE, True)
    add_page_number(slide, 3)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.63), Inches(11.73), Inches(0.025))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BORDER
    bar.line.fill.background()

    for idx, (value, desc, accent) in enumerate(metric_data):
        x = 0.8 + idx * 2.98
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.05), Inches(2.78), Inches(3.55))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_ALT if idx == 2 else CARD
        card.line.color.rgb = accent
        card.line.width = Pt(1.2)
        add_text(slide, value, x + 0.18, 3.05, 2.42, 0.75, 25, accent, True, PP_ALIGN.CENTER)
        add_text(slide, desc, x + 0.2, 3.95, 2.38, 1.15, 12, LIGHT, False, PP_ALIGN.CENTER)
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 0.8), Inches(5.23), Inches(1.18), Inches(0.035))
        line.fill.solid()
        line.fill.fore_color.rgb = accent
        line.line.fill.background()
    add_footer(slide, footer)
    return slide


def make_latency_slide(prs, heading, row_data, footer):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide)
    add_text(slide, heading, 0.8, 0.55, 10.4, 0.82, 21, WHITE, True)
    add_page_number(slide, 14)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.52), Inches(11.73), Inches(0.035))
    line.fill.solid()
    line.fill.fore_color.rgb = CYAN
    line.line.fill.background()

    for idx, (headline, detail, original_fill) in enumerate(row_data):
        y = 1.85 + idx * 1.23
        accent = CYAN if idx in (0, 2) else GREEN
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(y), Inches(11.73), Inches(1.02))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD if idx % 2 == 0 else CARD_ALT
        card.line.color.rgb = BORDER
        card.line.width = Pt(0.8)
        rail = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(0.075), Inches(1.02))
        rail.fill.solid()
        rail.fill.fore_color.rgb = accent
        rail.line.fill.background()
        add_text(slide, headline, 1.08, y + 0.12, 10.95, 0.34, 12, WHITE, True)
        add_text(slide, detail, 1.08, y + 0.53, 10.95, 0.32, 10.5, MUTED)
    add_footer(slide, footer)
    return slide


def set_slide_order(prs, order):
    slide_ids = list(prs.slides._sldIdLst)
    sld_id_list = prs.slides._sldIdLst
    for item in slide_ids:
        sld_id_list.remove(item)
    for idx in order:
        sld_id_list.append(slide_ids[idx])


def main():
    generated_source = not SOURCE.exists()
    if generated_source:
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_presentation.py"), str(SOURCE)],
            cwd=ROOT,
            check=True,
        )
    prs = Presentation(SOURCE)
    if len(prs.slides) != 15:
        raise RuntimeError(f"Expected 15 source slides, found {len(prs.slides)}")

    # Move the four existing KPI cards and their subtitle into a dedicated visual slide.
    context_slide = prs.slides[1]
    subtitle_shape = context_slide.shapes[3]
    subtitle = subtitle_shape.text
    footer = prs.slides[1].shapes[6].text
    metric_shapes = [context_slide.shapes[i] for i in range(10, 14)]
    metric_data = []
    for shape in metric_shapes:
        lines = [p.text for p in shape.text_frame.paragraphs]
        accent = shape.line.color.rgb or CYAN
        metric_data.append((lines[0], lines[1], accent))
    remove_shape(context_slide, subtitle_shape)
    for shape in metric_shapes:
        remove_shape(context_slide, shape)
    metrics_slide = make_metrics_slide(prs, subtitle, metric_data, footer)

    # Give the detailed processing-time breakdown its own readable slide.
    experiment_slide = prs.slides[11]
    footer2 = experiment_slide.shapes[6].text
    breakdown_shapes = [experiment_slide.shapes[i] for i in range(11, 16)]
    heading = breakdown_shapes[0].text_frame.paragraphs[0].text
    row_data = []
    for shape in breakdown_shapes[1:]:
        paragraphs = [p.text for p in shape.text_frame.paragraphs]
        row_data.append((paragraphs[0], paragraphs[1], shape.fill.fore_color.rgb))
    for shape in breakdown_shapes:
        remove_shape(experiment_slide, shape)
    latency_slide = make_latency_slide(prs, heading, row_data, footer2)

    # The two newly created slides are appended initially; reorder them into their narrative positions.
    # Existing IDs 0..14, metrics 15, latency 16.
    set_slide_order(prs, [0, 1, 15, *range(2, 12), 16, *range(12, 15)])

    # Refresh only the slide counters; section names, prose, figures, and data remain verbatim.
    for slide_no, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text.strip()
                if len(text) >= 7 and text[:2].isdigit() and " / " in text[:8]:
                    paragraph = shape.text_frame.paragraphs[0]
                    paragraph.text = f"{slide_no:02d} / 17"
                    paragraph.font.name = "Segoe UI"
                    paragraph.font.size = Pt(12)
                    paragraph.font.bold = True
                    paragraph.font.color.rgb = CYAN

    prs.save(OUTPUT)
    if generated_source and SOURCE.exists():
        SOURCE.unlink()
    print(f"SUCCESS: Saved {OUTPUT.name} with {len(prs.slides)} slides.")


if __name__ == "__main__":
    main()
