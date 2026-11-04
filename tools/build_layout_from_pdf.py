"""Build an OMR layout JSON and visual overlay from a vector answer-sheet PDF."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

import pymupdf
from PIL import Image, ImageDraw, ImageFont


ANSWER_DIAMETER_PT = 11.88
DIGIT_DIAMETER_PT = 9.28


def _spans(page: pymupdf.Page) -> list[tuple[str, pymupdf.Rect]]:
    result: list[tuple[str, pymupdf.Rect]] = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                result.append((span["text"].strip(), pymupdf.Rect(span["bbox"])))
    return result


def _circle_candidates(page: pymupdf.Page) -> list[dict[str, float]]:
    circles = []
    for drawing in page.get_drawings():
        rect = drawing["rect"]
        if (
            drawing["type"] != "s"
            or len(drawing["items"]) != 4
            or abs(rect.width - rect.height) > 0.08
        ):
            continue
        diameter = (rect.width + rect.height) / 2
        if min(abs(diameter - ANSWER_DIAMETER_PT), abs(diameter - DIGIT_DIAMETER_PT)) > 0.12:
            continue
        circles.append(
            {
                "x": (rect.x0 + rect.x1) / 2,
                "y": (rect.y0 + rect.y1) / 2,
                "diameter_pt": diameter,
            }
        )
    return circles


def _black_square_markers(page: pymupdf.Page, scale: float) -> list[dict[str, Any]]:
    markers = []
    for drawing in page.get_drawings():
        rect = drawing["rect"]
        fill = drawing.get("fill")
        if (
            drawing["type"] not in ("f", "fs")
            or fill is None
            or max(fill) > 0.01
            or not 7 <= rect.width <= 16
            or not 7 <= rect.height <= 16
            or abs(rect.width - rect.height) > 0.5
        ):
            continue
        markers.append(
            {
                "id": f"marker_{len(markers) + 1:02d}",
                "x": round((rect.x0 + rect.x1) / 2 * scale, 2),
                "y": round((rect.y0 + rect.y1) / 2 * scale, 2),
                "size": round((rect.width + rect.height) / 2 * scale, 2),
            }
        )
    return markers


def _pixel_point(circle: dict[str, float], scale: float) -> dict[str, float]:
    return {"x": round(circle["x"] * scale, 2), "y": round(circle["y"] * scale, 2)}


def _build_answer_blocks(
    spans: list[tuple[str, pymupdf.Rect]],
    circles: list[dict[str, float]],
    scale: float,
) -> list[dict[str, Any]]:
    answer_circles = [
        circle
        for circle in circles
        if abs(circle["diameter_pt"] - ANSWER_DIAMETER_PT) < 0.2
        and circle["y"] > 320
    ]
    question_labels = []
    for text, rect in spans:
        if not text.isdigit() or not 1 <= int(text) <= 50 or rect.y0 < 300:
            continue
        question_labels.append((int(text), rect))

    answer_rows: dict[int, list[dict[str, float]]] = {}
    for question, label in question_labels:
        label_x = label.x1
        label_y = (label.y0 + label.y1) / 2
        row = [
            circle
            for circle in answer_circles
            if label_x < circle["x"] < label_x + 160
            and abs(circle["y"] - label_y) <= 5
        ]
        if len(row) != 4:
            raise ValueError(
                f"Question label {question} matched {len(row)} answer bubbles; expected 4."
            )
        answer_rows[question] = sorted(row, key=lambda circle: circle["x"])

    if set(answer_rows) != set(range(1, 51)):
        missing = sorted(set(range(1, 51)) - set(answer_rows))
        raise ValueError(f"Could not map all question labels; missing {missing}.")

    blocks = []
    for block_id, questions in (("answers_left", range(1, 26)), ("answers_right", range(26, 51))):
        question_rows = []
        for question in questions:
            row = answer_rows[question]
            question_rows.append(
                {
                    "question": question,
                    "y": round(statistics.mean(circle["y"] for circle in row) * scale, 2),
                    "options": {
                        option: _pixel_point(circle, scale)
                        for option, circle in zip("ABCD", row, strict=True)
                    },
                }
            )
        first_row = answer_rows[question_rows[0]["question"]]
        x_steps = [
            first_row[index + 1]["x"] - first_row[index]["x"] for index in range(3)
        ]
        y_steps = [
            question_rows[index + 1]["y"] - question_rows[index]["y"]
            for index in range(24)
        ]
        blocks.append(
            {
                "id": block_id,
                "type": "answers",
                "first_question": question_rows[0]["question"],
                "rows": len(question_rows),
                "options_per_row": 4,
                "option_order": list("ABCD"),
                "origin": question_rows[0]["options"]["A"],
                "pitch_x": round(statistics.median(x_steps) * scale, 2),
                "pitch_y": round(statistics.median(y_steps), 2),
                "radius": round(
                    statistics.median(circle["diameter_pt"] for circle in first_row)
                    * scale
                    / 2,
                    2,
                ),
                "questions": question_rows,
            }
        )
    return blocks


def _build_id_blocks(
    spans: list[tuple[str, pymupdf.Rect]],
    circles: list[dict[str, float]],
    scale: float,
) -> dict[str, dict[str, Any]]:
    digit_circles = [
        circle
        for circle in circles
        if abs(circle["diameter_pt"] - DIGIT_DIAMETER_PT) < 0.2
    ]
    heading_rects: dict[str, pymupdf.Rect] = {}
    for text, rect in spans:
        lowered = text.lower()
        if rect.y0 >= 100 or rect.x0 < 400:
            continue
        if "số báo danh" in lowered:
            heading_rects["student_id"] = rect
        elif "mã đề thi" in lowered:
            heading_rects["exam_code"] = rect
    if set(heading_rects) != {"student_id", "exam_code"}:
        raise ValueError("Could not find both SBD and exam-code headings in PDF text.")

    result: dict[str, dict[str, Any]] = {}
    sorted_headings = sorted(heading_rects.items(), key=lambda item: item[1].x0)
    for heading_index, (block_id, heading) in enumerate(sorted_headings):
        x_limit = (
            sorted_headings[heading_index + 1][1].x0 - 3
            if heading_index + 1 < len(sorted_headings)
            else heading.x1 + 70
        )
        candidates = [
            circle
            for circle in digit_circles
            if heading.x0 - 2 < circle["x"] < x_limit
            and heading.y1 < circle["y"] < heading.y1 + 190
        ]
        xs = sorted({round(circle["x"], 1) for circle in candidates})
        ys = sorted({round(circle["y"], 1) for circle in candidates})
        if not xs or len(ys) != 10 or len(candidates) != len(xs) * 10:
            raise ValueError(
                f"{block_id} grid is incomplete: {len(xs)} columns, {len(ys)} digit rows, "
                f"{len(candidates)} bubbles."
            )
        columns = []
        for x in xs:
            column = sorted(
                (circle for circle in candidates if abs(circle["x"] - x) <= 0.2),
                key=lambda circle: circle["y"],
            )
            if len(column) != 10:
                raise ValueError(f"{block_id} column at x={x} has {len(column)} bubbles.")
            columns.append(
                {
                    "column": len(columns) + 1,
                    "digits": [
                        {"digit": digit, **_pixel_point(circle, scale)}
                        for digit, circle in enumerate(column)
                    ],
                }
            )
        y_steps = [
            candidates_for_row - previous
            for previous, candidates_for_row in zip(ys, ys[1:])
        ]
        result[block_id] = {
            "id": block_id,
            "type": "digits",
            "rows": 10,
            "columns": len(xs),
            "origin": _pixel_point(
                min(candidates, key=lambda circle: (circle["x"], circle["y"])), scale
            ),
            "pitch_x": round(statistics.median(b - a for a, b in zip(xs, xs[1:])) * scale, 2)
            if len(xs) > 1
            else 0,
            "pitch_y": round(statistics.median(y_steps) * scale, 2),
            "radius": round(
                statistics.median(circle["diameter_pt"] for circle in candidates) * scale / 2,
                2,
            ),
            "digit_order": list(range(10)),
            "columns_data": columns,
        }
    return result


def build_layout(pdf_path: Path, dpi: int) -> tuple[dict[str, Any], Image.Image]:
    document = pymupdf.open(pdf_path)
    if len(document) != 1:
        raise ValueError(f"Expected a single-page PDF, got {len(document)} pages.")
    page = document[0]
    scale = dpi / 72
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    spans = _spans(page)
    circles = _circle_candidates(page)
    layout = {
        "name": "FormTHPT50",
        "source_pdf": pdf_path.name,
        "dpi": dpi,
        "canvas_w": pixmap.width,
        "canvas_h": pixmap.height,
        "capacity": 50,
        "markers": _black_square_markers(page, scale),
        "blocks": _build_answer_blocks(spans, circles, scale),
        "id_blocks": _build_id_blocks(spans, circles, scale),
    }
    return layout, image


def write_debug_overlay(layout: dict[str, Any], image: Image.Image, output: Path) -> None:
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for marker in layout["markers"]:
        half = marker["size"] / 2
        draw.rectangle(
            (
                marker["x"] - half,
                marker["y"] - half,
                marker["x"] + half,
                marker["y"] + half,
            ),
            outline=(255, 0, 0),
            width=2,
        )
    for block in layout["blocks"]:
        for row in block["questions"]:
            for option, point in row["options"].items():
                radius = block["radius"]
                draw.ellipse(
                    (point["x"] - radius, point["y"] - radius, point["x"] + radius, point["y"] + radius),
                    outline=(0, 120, 255),
                    width=2,
                )
                draw.text((point["x"] - 4, point["y"] - 5), option, fill=(220, 0, 0), font=font)
            first = row["options"]["A"]
            draw.text((first["x"] - 45, first["y"] - 5), str(row["question"]), fill=(0, 140, 0), font=font)
    for block in layout["id_blocks"].values():
        for column in block["columns_data"]:
            for bubble in column["digits"]:
                radius = block["radius"]
                draw.ellipse(
                    (
                        bubble["x"] - radius,
                        bubble["y"] - radius,
                        bubble["x"] + radius,
                        bubble["y"] + radius,
                    ),
                    outline=(200, 0, 200),
                    width=2,
                )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--output", type=Path, default=Path("templates/layouts/thpt50.json"))
    parser.add_argument(
        "--debug-image",
        type=Path,
        default=Path("templates/layouts/thpt50_debug.png"),
    )
    parser.add_argument(
        "--base-image",
        type=Path,
        default=Path("templates/layouts/thpt50_base.png"),
    )
    args = parser.parse_args()
    layout, image = build_layout(args.pdf, args.dpi)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(layout, indent=2), encoding="utf-8")
    args.base_image.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.base_image)
    write_debug_overlay(layout, image, args.debug_image)
    print(f"Layout: {args.output}")
    print(f"Debug overlay: {args.debug_image}")
    print(f"Base image: {args.base_image}")
    print(f"Canvas: {layout['canvas_w']}x{layout['canvas_h']} px at {args.dpi} DPI")
    print(f"Answer blocks: {len(layout['blocks'])}, 25 rows each, 4 options")
    for key, block in layout["id_blocks"].items():
        print(f"{key}: {block['columns']} columns x {block['rows']} digit rows")
    print(f"Black-square markers: {len(layout['markers'])}")


if __name__ == "__main__":
    main()
