#!/usr/bin/env python3
"""Render Paper 10 Markdown sources to stable, readable PDFs with ReportLab."""

from __future__ import annotations

import argparse
import hashlib
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
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
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


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "pdf"
PAGE_WIDTH = letter[0] - 1.35 * inch
BLUE = colors.HexColor("#315b7d")
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#536174")
RULE = colors.HexColor("#cbd5e1")
PALE = colors.HexColor("#eef4f8")
MATH = ROOT / "figures" / "math"
MATH_DPI = 320
MATH_FONT_SIZE = 10.0


def configure_fonts() -> tuple[str, str, str, str]:
    """Prefer bundled DejaVu fonts for broad punctuation coverage."""

    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for regular in candidates:
        if not regular.exists():
            continue
        if "DejaVu" in regular.name:
            family_dir = regular.parent
            bold = family_dir / "DejaVuSans-Bold.ttf"
            italic = family_dir / "DejaVuSans-Oblique.ttf"
            bold_italic = family_dir / "DejaVuSans-BoldOblique.ttf"
        else:
            family_dir = regular.parent
            bold = family_dir / "Arial Bold.ttf"
            italic = family_dir / "Arial Italic.ttf"
            bold_italic = family_dir / "Arial Bold Italic.ttf"
        if all(path.exists() for path in (bold, italic, bold_italic)):
            pdfmetrics.registerFont(TTFont("PaperSans", str(regular)))
            pdfmetrics.registerFont(TTFont("PaperSans-Bold", str(bold)))
            pdfmetrics.registerFont(TTFont("PaperSans-Italic", str(italic)))
            pdfmetrics.registerFont(TTFont("PaperSans-BoldItalic", str(bold_italic)))
            pdfmetrics.registerFontFamily(
                "PaperSans",
                normal="PaperSans",
                bold="PaperSans-Bold",
                italic="PaperSans-Italic",
                boldItalic="PaperSans-BoldItalic",
            )
            return "PaperSans", "PaperSans-Bold", "PaperSans-Italic", "PaperSans-BoldItalic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique"


REGULAR, BOLD, ITALIC, BOLD_ITALIC = configure_fonts()


def math_asset_name(expression: str) -> str:
    normalized = " ".join(expression.strip().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest() + ".png"


def math_asset(expression: str) -> Path:
    path = MATH / math_asset_name(expression)
    if not path.exists():
        raise FileNotFoundError(f"missing rendered math asset: {path}; run build_artifacts.py first")
    return path


def math_dimensions(expression: str, target_font_size: float) -> tuple[Path, float, float]:
    path = math_asset(expression)
    with PILImage.open(path) as image:
        width_px, height_px = image.size
    scale = target_font_size / MATH_FONT_SIZE
    return path, width_px * 72.0 / MATH_DPI * scale, height_px * 72.0 / MATH_DPI * scale


def inline_markup(raw: str, font_size: float = 9.15) -> str:
    math_spans: list[str] = []

    def math_span(match: re.Match[str]) -> str:
        expression = match.group(1).strip()
        path, width, height = math_dimensions(expression, font_size)
        max_inline_height = 1.18 * font_size
        if height > max_inline_height:
            ratio = max_inline_height / height
            width *= ratio
            height *= ratio
        math_spans.append(
            f'<img src="{path}" width="{width:.3f}" height="{height:.3f}" valign="-1.3"/>'
        )
        return f"@@MATH{len(math_spans) - 1}@@"

    protected = re.sub(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", math_span, raw)
    escaped = html.escape(protected, quote=False)
    code_spans: list[str] = []

    def code(match: re.Match[str]) -> str:
        code_spans.append(match.group(1))
        return f"@@CODE{len(code_spans) - 1}@@"

    escaped = re.sub(r"`([^`]+)`", code, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", rf'<font name="{BOLD}">\1</font>', escaped)
    escaped = re.sub(r"\*([^*]+)\*", rf'<font name="{ITALIC}">\1</font>', escaped)
    for index, value in enumerate(code_spans):
        escaped = escaped.replace(
            f"@@CODE{index}@@",
            f'<font name="Courier" color="#25364a">{value}</font>',
        )
    for index, value in enumerate(math_spans):
        escaped = escaped.replace(f"@@MATH{index}@@", value)
    return escaped


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="PaperTitle", fontName=BOLD, fontSize=19.5, leading=23.5,
        alignment=TA_CENTER, textColor=INK, spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        name="H1", fontName=BOLD, fontSize=15, leading=18,
        textColor=BLUE, spaceBefore=13, spaceAfter=7, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="H2", fontName=BOLD, fontSize=11.8, leading=14.2,
        textColor=INK, spaceBefore=10, spaceAfter=5, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="H3", fontName=BOLD_ITALIC, fontSize=10.2, leading=12.5,
        textColor=INK, spaceBefore=8, spaceAfter=4, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="Body", fontName=REGULAR, fontSize=9.15, leading=12.1,
        textColor=INK, spaceAfter=5.2, alignment=TA_LEFT, splitLongWords=True,
    ))
    styles.add(ParagraphStyle(
        name="Reference", parent=styles["Body"], fontSize=7.6, leading=9.7,
        leftIndent=9, firstLineIndent=-9, spaceAfter=3.5,
    ))
    styles.add(ParagraphStyle(
        name="Small", parent=styles["Body"], fontSize=7.1, leading=8.7,
        spaceAfter=2.5,
    ))
    styles.add(ParagraphStyle(
        name="Caption", fontName=ITALIC, fontSize=7.5, leading=9.3,
        alignment=TA_CENTER, textColor=MUTED, spaceBefore=4, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Quote", parent=styles["Body"], fontName=ITALIC,
        leftIndent=0.28 * inch, rightIndent=0.28 * inch,
        borderColor=BLUE, borderWidth=0, borderPadding=6,
        textColor=colors.HexColor("#26364b"), spaceBefore=3, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Meta", fontName=REGULAR, fontSize=9, leading=12,
        alignment=TA_CENTER, textColor=MUTED, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="CodeBlock", fontName="Courier", fontSize=7.2, leading=9,
        leftIndent=8, rightIndent=8, borderColor=RULE, borderWidth=0.4,
        borderPadding=6, backColor=colors.HexColor("#f8fafc"), spaceAfter=6,
    ))
    return styles


def paragraph(raw: str, style) -> Paragraph:
    return Paragraph(inline_markup(raw, style.fontSize), style)


def table_from_lines(lines: list[str], styles, page_width: float) -> Table:
    raw_rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":", " "}:
            continue
        raw_rows.append(cells)
    columns = max(len(row) for row in raw_rows)
    for row in raw_rows:
        row.extend([""] * (columns - len(row)))

    max_lengths = [max(len(row[index]) for row in raw_rows) for index in range(columns)]
    weights = [max(5.0, min(float(length), 34.0)) for length in max_lengths]
    total = sum(weights)
    widths = [page_width * weight / total for weight in weights]
    minimum = 0.62 * inch
    if columns >= 5:
        minimum = 0.48 * inch
    widths = [max(minimum, width) for width in widths]
    scale = page_width / sum(widths)
    widths = [width * scale for width in widths]

    rows = [
        [Paragraph(inline_markup(cell, styles["Small"].fontSize), styles["Small"]) for cell in row]
        for row in raw_rows
    ]
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("FONTNAME", (0, 0), (-1, 0), BOLD),
        ("GRID", (0, 0), (-1, -1), 0.28, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfdff")]),
    ]))
    return table


def image_flowable(base_dir: Path, alt: str, relative_path: str, styles, page_width: float):
    full_path = (base_dir / relative_path).resolve()
    if not full_path.exists():
        raise FileNotFoundError(f"missing figure: {full_path}")
    with PILImage.open(full_path) as image:
        width_px, height_px = image.size
    ratio = min(page_width / width_px, 4.75 * inch / height_px)
    rendered = Image(str(full_path), width=width_px * ratio, height=height_px * ratio, hAlign="CENTER")
    return KeepTogether([rendered, Paragraph(inline_markup(alt, styles["Caption"].fontSize), styles["Caption"])])


def math_flowable(expression: str, page_width: float):
    path, width, height = math_dimensions(expression, 11.2)
    ratio = min(1.0, 0.92 * page_width / width)
    rendered = Image(str(path), width=width * ratio, height=height * ratio, hAlign="CENTER")
    return KeepTogether([Spacer(1, 2), rendered, Spacer(1, 7)])


def build_story(path: Path, styles, page_width: float, add_end_break: bool = False):
    lines = path.read_text(encoding="utf-8").splitlines()
    story: list = []
    para: list[str] = []
    bullets: list[str] = []
    numbers: list[str] = []
    code: list[str] = []
    in_code = False
    in_references = False
    title_seen = False
    index = 0

    def flush_para():
        if para:
            raw = " ".join(part.strip() for part in para).strip()
            style = styles["Reference"] if in_references else styles["Body"]
            story.append(paragraph(raw, style))
            para.clear()

    def flush_lists():
        if bullets:
            items = [ListItem(paragraph(item, styles["Body"]), leftIndent=9) for item in bullets]
            story.append(ListFlowable(items, bulletType="bullet", start="circle", leftIndent=20, bulletFontName=REGULAR))
            story.append(Spacer(1, 2))
            bullets.clear()
        if numbers:
            items = [ListItem(paragraph(item, styles["Body"]), leftIndent=11) for item in numbers]
            story.append(ListFlowable(items, bulletType="1", start="1", leftIndent=23, bulletFontName=REGULAR))
            story.append(Spacer(1, 2))
            numbers.clear()

    def flush_code():
        if code:
            wrapped: list[str] = []
            for raw in code:
                wrapped.extend(textwrap.wrap(raw, width=96, subsequent_indent="  ", break_long_words=True, break_on_hyphens=False) or [""])
            story.append(Preformatted("\n".join(wrapped), styles["CodeBlock"]))
            code.clear()

    while index < len(lines):
        line = lines[index].rstrip()
        if line.startswith("```"):
            if in_code:
                in_code = False
                flush_code()
            else:
                flush_para()
                flush_lists()
                in_code = True
            index += 1
            continue
        if in_code:
            code.append(line)
            index += 1
            continue
        math_match = re.fullmatch(r"\$\$([^$]+)\$\$", line.strip())
        if math_match:
            flush_para()
            flush_lists()
            story.append(math_flowable(math_match.group(1).strip(), page_width))
            index += 1
            continue
        image_match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", line.strip())
        if image_match:
            flush_para()
            flush_lists()
            story.append(image_flowable(path.parent, image_match.group(1), image_match.group(2), styles, page_width))
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and lines[index + 1].startswith("|"):
            flush_para()
            flush_lists()
            table_lines = [line]
            index += 1
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index].rstrip())
                index += 1
            story.append(table_from_lines(table_lines, styles, page_width))
            story.append(Spacer(1, 7))
            continue
        if not line.strip():
            flush_para()
            flush_lists()
            index += 1
            continue
        if line.strip() == "---":
            flush_para()
            flush_lists()
            story.append(PageBreak())
            index += 1
            continue
        if line.startswith("# "):
            flush_para()
            flush_lists()
            if title_seen:
                story.append(PageBreak())
            story.append(Paragraph(inline_markup(line[2:].strip(), styles["PaperTitle"].fontSize), styles["PaperTitle"]))
            title_seen = True
        elif line.startswith("## "):
            flush_para()
            flush_lists()
            heading = line[3:].strip()
            in_references = heading in {"References", "S14. References unique to the supplement"}
            story.append(Paragraph(inline_markup(heading, styles["H1"].fontSize), styles["H1"]))
        elif line.startswith("### "):
            flush_para()
            flush_lists()
            story.append(Paragraph(inline_markup(line[4:].strip(), styles["H2"].fontSize), styles["H2"]))
        elif line.startswith("#### "):
            flush_para()
            flush_lists()
            story.append(Paragraph(inline_markup(line[5:].strip(), styles["H3"].fontSize), styles["H3"]))
        elif line.startswith("> "):
            flush_para()
            flush_lists()
            story.append(paragraph(line[2:].strip(), styles["Quote"]))
        elif line.startswith("- "):
            flush_para()
            if numbers:
                flush_lists()
            bullets.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            flush_para()
            if bullets:
                flush_lists()
            numbers.append(re.sub(r"^\d+\.\s+", "", line))
        elif not story or (title_seen and len(story) < 8 and line.startswith("**")):
            flush_para()
            flush_lists()
            story.append(Paragraph(inline_markup(line.rstrip("  "), styles["Meta"].fontSize), styles["Meta"]))
        else:
            para.append(line)
        index += 1

    flush_para()
    flush_lists()
    flush_code()
    if add_end_break:
        story.append(PageBreak())
    return story


def page_frame(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.35)
    canvas.line(doc.leftMargin, letter[1] - 0.42 * inch, letter[0] - doc.rightMargin, letter[1] - 0.42 * inch)
    canvas.setFont(REGULAR, 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 0.34 * inch, "Ryan - The Intervention-Coverage Barrier")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.34 * inch, f"Page {doc.page}")
    canvas.restoreState()


def render(inputs: list[Path], output: Path, title: str, subject: str):
    styles = make_styles()
    story: list = []
    for index, source in enumerate(inputs):
        story.extend(build_story(source, styles, PAGE_WIDTH, add_end_break=index < len(inputs) - 1))
    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output), pagesize=letter,
        leftMargin=0.675 * inch, rightMargin=0.675 * inch,
        topMargin=0.60 * inch, bottomMargin=0.58 * inch,
        title=title, author="Thomas Ryan", subject=subject,
        keywords="neural replacement, brain emulation, functional fidelity, intervention coverage, verification",
    )
    document.build(story, onFirstPage=page_frame, onLaterPages=page_frame)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--main", type=Path, default=ROOT / "manuscript.md")
    parser.add_argument("--supplement", type=Path, default=ROOT / "supplement.md")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    main_output = output_dir / "ryan_2026_intervention_coverage_barrier.pdf"
    supplement_output = output_dir / "ryan_2026_intervention_coverage_barrier_supplement.pdf"
    complete_output = output_dir / "ryan_2026_intervention_coverage_barrier_complete.pdf"
    render([args.main.resolve()], main_output, "The Intervention-Coverage Barrier", "Paper 10 manuscript")
    render([args.supplement.resolve()], supplement_output, "Supplement: The Intervention-Coverage Barrier", "Paper 10 supplement")
    render([args.main.resolve(), args.supplement.resolve()], complete_output, "The Intervention-Coverage Barrier", "Paper 10 complete manuscript and supplement")
    for path in (main_output, supplement_output, complete_output):
        print(path)


if __name__ == "__main__":
    main()
