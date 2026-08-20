#!/usr/bin/env python3
"""Render the Stage-1 Markdown manuscript to a polished HTML/PDF pair.

This renderer changes only presentation. MANUSCRIPT.md remains the scientific
source of authority. It requires the locally installed markdown and weasyprint
packages and performs no network access.
"""

from __future__ import annotations

import argparse
import base64
import html
import re
from pathlib import Path

import markdown
from weasyprint import HTML


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "MANUSCRIPT.md"
HTML_OUTPUT = ROOT / "output" / "html" / "binding_test_stage1.html"
PDF_OUTPUT = ROOT / "output" / "pdf" / "binding_test_stage1.pdf"
EXPECTED_EMBEDDED_SVG_COUNT = 6


LATEX_REPLACEMENTS = (
    (r"\Delta", "Δ"),
    (r"\Omega", "Ω"),
    (r"\pi", "π"),
    (r"\rho", "ρ"),
    (r"\in", " ∈ "),
    (r"\sim", " ∼ "),
    (r"\mid", " | "),
    (r"\pm", "±"),
    (r"\ge", "≥"),
    (r"\le", "≤"),
    (r"\times", "×"),
    (r"\sum", "Σ"),
)


def normalize_dashes(value: str) -> str:
    """Keep rendered text portable across PDF font stacks."""

    return (
        value.replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "--")
        .replace("\u2212", "-")
    )


def readable_math(value: str) -> str:
    """Convert the manuscript's small LaTeX subset to readable static text."""

    converted = value.strip()
    converted = re.sub(r"\\text\{([^{}]*)\}", r"\1", converted)
    converted = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1/\2)", converted)
    for source, target in LATEX_REPLACEMENTS:
        converted = converted.replace(source, target)
    converted = converted.replace(r"\{", "{").replace(r"\}", "}")
    converted = re.sub(r"\s+", " ", converted)
    return html.escape(converted)


def prepare_markdown(source: str) -> str:
    normalized = normalize_dashes(source)

    def display(match: re.Match[str]) -> str:
        return f'\n<div class="equation">{readable_math(match.group(1))}</div>\n'

    normalized = re.sub(r"\\\[(.*?)\\\]", display, normalized, flags=re.DOTALL)

    def inline(match: re.Match[str]) -> str:
        return f'<span class="math">{readable_math(match.group(1))}</span>'

    return re.sub(r"\\\((.*?)\\\)", inline, normalized, flags=re.DOTALL)


def embed_svg_images(body: str) -> str:
    """Make the rendered HTML/PDF self-contained without network or path lookups."""

    def replace(match: re.Match[str]) -> str:
        relative = match.group(1)
        path = (ROOT / relative).resolve()
        if ROOT not in path.parents or path.suffix.lower() != ".svg":
            raise ValueError(f"unsafe manuscript image path: {relative}")
        payload = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'src="data:image/svg+xml;base64,{payload}"'

    embedded = re.sub(r'src="(figures/[^"]+\.svg)"', replace, body)
    embedded_count = embedded.count('src="data:image/svg+xml;base64,')
    if embedded_count != EXPECTED_EMBEDDED_SVG_COUNT:
        raise ValueError(
            "unexpected embedded SVG count: "
            f"{embedded_count} != {EXPECTED_EMBEDDED_SVG_COUNT}"
        )
    if re.search(r'src="figures/[^"]+\.svg"', embedded):
        raise ValueError("relative SVG reference remained after embedding")
    return embedded


def stylesheet() -> str:
    return """
@page {
  size: Letter;
  margin: 0.72in 0.70in 0.70in 0.70in;
  @top-left {
    content: "THE BINDING TEST";
    color: #496174;
    font: 700 8pt Arial, sans-serif;
    letter-spacing: 0.08em;
  }
  @top-right {
    content: "INTERNAL STAGE-1";
    color: #6f7f89;
    font: 700 8pt Arial, sans-serif;
    letter-spacing: 0.06em;
  }
  @bottom-center {
    content: counter(page);
    color: #61717c;
    font: 9pt Arial, sans-serif;
  }
}
@page:first {
  @top-left { content: none; }
  @top-right { content: none; }
}
html { color: #16232d; background: #ffffff; }
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 10.15pt;
  line-height: 1.44;
  margin: 0;
  hyphens: auto;
}
h1, h2, h3 {
  font-family: Arial, Helvetica, sans-serif;
  color: #14324a;
  page-break-after: avoid;
}
h1 {
  font-size: 28pt;
  line-height: 1.05;
  margin: 0.65in 0 0.14in;
  letter-spacing: -0.025em;
}
h1 + h2 {
  font-size: 15pt;
  font-weight: 500;
  line-height: 1.25;
  color: #476477;
  margin: 0 0 0.27in;
  border: 0;
}
h2 {
  font-size: 16pt;
  line-height: 1.18;
  margin: 0.28in 0 0.11in;
  padding-bottom: 0.045in;
  border-bottom: 1.2pt solid #bdd0da;
}
h3 {
  font-size: 11.7pt;
  line-height: 1.22;
  margin: 0.19in 0 0.07in;
}
p { margin: 0 0 0.095in; orphans: 3; widows: 3; }
strong { color: #14324a; }
em { color: #253c4d; }
a { color: #0b607d; text-decoration: none; }
ul, ol { margin: 0.055in 0 0.12in 0.24in; padding-left: 0.13in; }
li { margin: 0.025in 0; }
blockquote {
  margin: 0.13in 0;
  padding: 0.09in 0.14in;
  border-left: 3pt solid #3a8f9b;
  background: #f2f7f8;
  color: #29414e;
}
code {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 8.7pt;
  background: #f0f3f5;
  padding: 0.01in 0.025in;
  border-radius: 2px;
}
pre {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 8.4pt;
  line-height: 1.35;
  white-space: pre-wrap;
  background: #f0f3f5;
  border: 1px solid #d8e0e4;
  padding: 0.10in;
}
.math, .equation {
  font-family: "Times New Roman", Georgia, serif;
  color: #172e40;
}
.equation {
  text-align: center;
  font-size: 11pt;
  margin: 0.13in 0;
  padding: 0.075in 0.10in;
  background: #f7f9fa;
  border-top: 0.7pt solid #d7e1e6;
  border-bottom: 0.7pt solid #d7e1e6;
}
img {
  display: block;
  max-width: 92%;
  max-height: 5.9in;
  margin: 0.16in auto 0.08in;
  object-fit: contain;
}
img + em, img + strong { display: block; text-align: center; }
hr { border: 0; border-top: 1px solid #ccd8de; margin: 0.18in 0; }
table {
  width: 100%;
  border-collapse: collapse;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8.1pt;
  margin: 0.12in 0 0.18in;
}
th {
  text-align: left;
  color: #ffffff;
  background: #244b63;
  padding: 0.055in;
}
td {
  vertical-align: top;
  border-bottom: 0.6pt solid #cdd8de;
  padding: 0.05in;
}
tbody tr:nth-child(even) { background: #f5f8f9; }
"""


def render() -> tuple[Path, Path]:
    prepared = prepare_markdown(SOURCE.read_text(encoding="utf-8"))
    body = markdown.markdown(
        prepared,
        extensions=("extra", "sane_lists"),
        output_format="html5",
    )
    body = embed_svg_images(body)
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Binding Test - Internal Stage-1</title>
  <meta name="author" content="Authors to be supplied">
  <style>{stylesheet()}</style>
</head>
<body>{body}</body>
</html>
"""
    HTML_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PDF_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUTPUT.write_text(document, encoding="utf-8", newline="\n")
    HTML(string=document, base_url=str(ROOT)).write_pdf(
        PDF_OUTPUT,
        presentational_hints=True,
        custom_metadata=True,
    )
    return HTML_OUTPUT, PDF_OUTPUT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    html_path, pdf_path = render()
    print(html_path.relative_to(ROOT).as_posix())
    print(pdf_path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
