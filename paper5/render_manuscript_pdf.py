#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import textwrap
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def inline_markup(text: str) -> str:
    placeholders: list[tuple[str, str]] = []

    def stash_code(match: re.Match[str]) -> str:
        key = f"@@CODE{len(placeholders)}@@"
        code = html.escape(match.group(1))
        placeholders.append((key, f'<font name="Courier">{code}</font>'))
        return key

    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", stash_code, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", escaped)
    for key, value in placeholders:
        escaped = escaped.replace(key, value)
    return escaped


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitlePage",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading1Tight",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            spaceBefore=14,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading2Tight",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            spaceBefore=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading3Tight",
            parent=styles["Heading3"],
            fontSize=11,
            leading=14,
            spaceBefore=10,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyTight",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Quote",
            parent=styles["BodyText"],
            leftIndent=0.25 * inch,
            rightIndent=0.25 * inch,
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=12.5,
            spaceBefore=4,
            spaceAfter=8,
        )
    )
    return styles


def paragraph(text: str, style) -> Paragraph:
    return Paragraph(inline_markup(text), style)


def table_from_lines(lines: list[str], styles, page_width: float) -> Table:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":", " "}:
            continue
        rows.append([Paragraph(inline_markup(cell), styles["SmallBody"]) for cell in cells])

    col_count = max(len(row) for row in rows)
    col_width = page_width / col_count
    table = Table(rows, colWidths=[col_width] * col_count, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def image_flowable(base_dir: Path, alt_text: str, image_path: str, styles, page_width: float):
    full_path = (base_dir / image_path).resolve()
    if not full_path.exists():
        return paragraph(f"[missing image: {image_path}]", styles["BodyTight"])

    with PILImage.open(full_path) as img:
        width_px, height_px = img.size
    ratio = min(page_width / width_px, 4.6 * inch / height_px, 1.0)
    width = width_px * ratio
    height = height_px * ratio
    return KeepTogether(
        [
            Image(str(full_path), width=width, height=height, hAlign="CENTER"),
            Paragraph(inline_markup(alt_text), styles["Caption"]),
        ]
    )


def build_story(markdown_path: Path, styles, page_width: float):
    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    story = []
    paragraph_buffer: list[str] = []
    list_buffer: list[str] = []
    code_buffer: list[str] = []
    in_code = False
    in_references = False
    i = 0

    def flush_paragraph():
        if paragraph_buffer:
            style = styles["SmallBody"] if in_references else styles["BodyTight"]
            para = paragraph(" ".join(paragraph_buffer).strip(), style)
            story.append(KeepTogether([para]) if in_references else para)
            paragraph_buffer.clear()

    def flush_list():
        if list_buffer:
            items = [ListItem(paragraph(item, styles["BodyTight"])) for item in list_buffer]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=18))
            list_buffer.clear()

    def flush_code():
        if code_buffer:
            wrapped_lines: list[str] = []
            for raw_line in code_buffer:
                if len(raw_line) <= 86:
                    wrapped_lines.append(raw_line)
                    continue
                indent = len(raw_line) - len(raw_line.lstrip())
                prefix = " " * min(indent + 2, 12)
                wrapped = textwrap.wrap(
                    raw_line,
                    width=86,
                    subsequent_indent=prefix,
                    break_long_words=True,
                    break_on_hyphens=False,
                )
                wrapped_lines.extend(wrapped or [""])
            story.append(Preformatted("\n".join(wrapped_lines), styles["Code"]))
            story.append(Spacer(1, 6))
            code_buffer.clear()

    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("```"):
            if in_code:
                in_code = False
                flush_code()
            else:
                flush_paragraph()
                flush_list()
                in_code = True
            i += 1
            continue

        if in_code:
            code_buffer.append(line)
            i += 1
            continue

        image_match = re.match(r"!\[(.*?)\]\((.*?)\)", line)
        if image_match:
            flush_paragraph()
            flush_list()
            story.append(image_flowable(markdown_path.parent, image_match.group(1), image_match.group(2), styles, page_width))
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
            flush_paragraph()
            flush_list()
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i].rstrip())
                i += 1
            story.append(table_from_lines(table_lines, styles, page_width))
            story.append(Spacer(1, 8))
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            i += 1
            continue

        if line == "---":
            flush_paragraph()
            flush_list()
            story.append(PageBreak())
            i += 1
            continue

        if line.startswith("# "):
            flush_paragraph()
            flush_list()
            story.append(Paragraph(inline_markup(line[2:].strip()), styles["TitlePage"]))
        elif line.startswith("## "):
            flush_paragraph()
            flush_list()
            in_references = line.strip() == "## References"
            story.append(Paragraph(inline_markup(line[3:].strip()), styles["Heading1Tight"]))
        elif line.startswith("### "):
            flush_paragraph()
            flush_list()
            story.append(Paragraph(inline_markup(line[4:].strip()), styles["Heading2Tight"]))
        elif line.startswith("> "):
            flush_paragraph()
            flush_list()
            story.append(paragraph(line[2:].strip(), styles["Quote"]))
        elif re.match(r"^\d+\. ", line):
            flush_paragraph()
            flush_list()
            paragraph_buffer.append(line)
        elif line.startswith("- "):
            flush_paragraph()
            list_buffer.append(line[2:].strip())
        else:
            paragraph_buffer.append(line)
        i += 1

    flush_paragraph()
    flush_list()
    flush_code()
    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#475569"))
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("paper5/manuscript.md"))
    parser.add_argument("--output", type=Path, default=Path("output/pdf/paper5_causal_preservation_draft.pdf"))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    page_width = letter[0] - 1.4 * inch
    story = build_story(args.input, styles, page_width)

    doc = SimpleDocTemplate(
        str(args.output),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Paper 5: Causal Preservation Under Substrate Transfer",
        author="Thomas Ryan",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(args.output)


if __name__ == "__main__":
    main()
