#!/usr/bin/env python3
"""Render the methods/feasibility Markdown manuscript to HTML and PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

import markdown
from weasyprint import HTML


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]
SOURCE = ROOT / "MANUSCRIPT.md"
HTML_OUTPUT = (
    REPOSITORY / "output" / "html" / "paper8_binding_test_methods_feasibility_v0.html"
)
PDF_OUTPUT = (
    REPOSITORY / "output" / "pdf" / "paper8_binding_test_methods_feasibility_v0.pdf"
)

LATEX_REPLACEMENTS = (
    (r"\rho", "rho"),
    (r"\in", " in "),
    (r"\pm", "+/-"),
    (r"\times", "x"),
)


def prepare_markdown(source: str) -> str:
    """Normalize typography and the manuscript's small inline-math subset."""

    normalized = (
        source.replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "--")
        .replace("\u2212", "-")
    )

    def inline(match: re.Match[str]) -> str:
        value = match.group(1)
        for old, new in LATEX_REPLACEMENTS:
            value = value.replace(old, new)
        return f'<span class="math">{html.escape(value)}</span>'

    return re.sub(r"\\\((.*?)\\\)", inline, normalized, flags=re.DOTALL)


def stylesheet() -> str:
    return """
@page {
  size: Letter;
  margin: 0.68in 0.70in 0.66in;
  @top-left {
    content: "THE BINDING TEST";
    color: #526777;
    font: 700 8pt Arial, sans-serif;
    letter-spacing: 0.08em;
  }
  @top-right {
    content: "METHODS & FEASIBILITY PREPRINT";
    color: #6f7f89;
    font: 700 8pt Arial, sans-serif;
    letter-spacing: 0.05em;
  }
  @bottom-center {
    content: counter(page);
    color: #61717c;
    font: 9pt Arial, sans-serif;
  }
}
@page:first { @top-left { content: none; } @top-right { content: none; } }
html { color: #17242d; background: #fff; }
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 10pt;
  line-height: 1.42;
  margin: 0;
  hyphens: auto;
}
h1, h2, h3 { font-family: Arial, Helvetica, sans-serif; color: #14324a; page-break-after: avoid; }
h1 { font-size: 29pt; line-height: 1.04; margin: 0.65in 0 0.14in; letter-spacing: -0.025em; }
h1 + h2 { font-size: 15pt; font-weight: 500; line-height: 1.25; color: #476477; margin: 0 0 0.28in; border: 0; }
h2 { font-size: 16pt; line-height: 1.18; margin: 0.28in 0 0.11in; padding-bottom: 0.045in; border-bottom: 1.2pt solid #bdd0da; }
h3 { font-size: 11.7pt; line-height: 1.22; margin: 0.19in 0 0.07in; }
p { margin: 0 0 0.10in; orphans: 3; widows: 3; }
strong { color: #14324a; }
em { color: #253c4d; }
a { color: #0b607d; text-decoration: none; }
ul, ol { margin: 0.055in 0 0.12in 0.24in; padding-left: 0.13in; }
li { margin: 0.025in 0; }
code { font-family: "SFMono-Regular", Consolas, monospace; font-size: 8.6pt; background: #f0f3f5; padding: 0.01in 0.025in; }
.math { font-family: "Times New Roman", Georgia, serif; color: #172e40; }
blockquote { margin: 0.13in 0; padding: 0.09in 0.14in; border-left: 3pt solid #3a8f9b; background: #f2f7f8; color: #29414e; }
"""


def render() -> tuple[Path, Path]:
    prepared = prepare_markdown(SOURCE.read_text(encoding="utf-8"))
    body = markdown.markdown(
        prepared,
        extensions=("extra", "sane_lists"),
        output_format="html5",
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Binding Test - Methods and Feasibility Preprint</title>
  <meta name="author" content="Thomas Ryan">
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
    html_path, pdf_path = render()
    print(html_path)
    print(pdf_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
