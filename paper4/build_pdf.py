"""Convert Paper 4 manuscript.md to a PDF."""

from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

import markdown
from weasyprint import HTML


paper_dir = Path(__file__).parent
md_path = paper_dir / "manuscript.md"
pdf_path = paper_dir / "ryan_2026_history_dependent_functional_continuity.pdf"


def render_markdown_figures(text: str) -> str:
    pattern = re.compile(r"!\[([^\]]+)\]\(([^)]+)\)")

    def repl(match: re.Match[str]) -> str:
        caption = html_lib.escape(match.group(1))
        src = html_lib.escape(match.group(2), quote=True)
        return (
            "\n<figure>\n"
            f'  <img src="{src}" alt="{caption}">\n'
            f"  <figcaption>{caption}</figcaption>\n"
            "</figure>\n"
        )

    return pattern.sub(repl, text)


md_text = render_markdown_figures(md_path.read_text(encoding="utf-8"))
html_body = markdown.markdown(md_text, extensions=["tables", "smarty"], output_format="html")

css = """
@page {
    size: letter;
    margin: 0.82in 0.78in 0.82in 0.78in;
    @bottom-center { content: counter(page); font-size: 9pt; color: #666; }
}
body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 10.7pt;
    line-height: 1.48;
    color: #171717;
}
h1 {
    font-size: 18pt;
    text-align: center;
    margin-bottom: 0.35em;
    line-height: 1.24;
}
h2 {
    font-size: 13.5pt;
    margin-top: 1.45em;
    border-bottom: 1px solid #d0d0d0;
    padding-bottom: 0.18em;
    page-break-after: avoid;
}
h3 {
    font-size: 11.8pt;
    margin-top: 1.15em;
    page-break-after: avoid;
}
p {
    margin: 0.55em 0;
    text-indent: 0;
}
ul, ol {
    margin-top: 0.35em;
}
li {
    margin: 0.18em 0;
}
table {
    border-collapse: collapse;
    width: 100%;
    font-size: 7.8pt;
    margin: 0.9em 0;
    break-inside: avoid;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #999;
    padding: 3px 4px;
    text-align: left;
    vertical-align: top;
}
th {
    background: #f0f0f0;
    font-weight: bold;
}
tr:nth-child(even) td {
    background: #fafafa;
}
tr {
    break-inside: avoid;
    page-break-inside: avoid;
}
img {
    max-width: 100%;
    display: block;
    margin: 0 auto;
    page-break-inside: avoid;
}
figure {
    margin: 1.0em auto;
    page-break-inside: avoid;
}
figcaption {
    font-size: 8.7pt;
    line-height: 1.32;
    color: #444;
    text-align: center;
    margin-top: 0.35em;
}
blockquote {
    border-left: 3px solid #ccc;
    margin-left: 0;
    padding-left: 1em;
    color: #555;
}
code {
    font-family: monospace;
    font-size: 8.8pt;
    background: #f5f5f5;
    padding: 1px 3px;
}
"""

full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>
"""

HTML(string=full_html, base_url=str(paper_dir)).write_pdf(str(pdf_path))
print(f"PDF saved to: {pdf_path}")
