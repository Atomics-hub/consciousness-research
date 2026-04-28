"""Convert Paper 3 manuscript.md to a publication-quality PDF."""

import html as html_lib
import re
from pathlib import Path

import markdown
from weasyprint import HTML


paper_dir = Path(__file__).parent
md_path = paper_dir / "manuscript.md"
pdf_path = paper_dir / "ryan_2026_preservation_benchmark_ast_v0.pdf"

md_text = md_path.read_text()


def render_markdown_figures(text: str) -> str:
    """Convert Markdown image syntax into figures with visible captions."""
    pattern = re.compile(r"!\[([^\]]+)\]\(([^)]+)\)")

    def repl(match: re.Match) -> str:
        caption = html_lib.escape(match.group(1))
        src = html_lib.escape(match.group(2), quote=True)
        return (
            "\n<figure>\n"
            f'  <img src="{src}" alt="{caption}">\n'
            f"  <figcaption>{caption}</figcaption>\n"
            "</figure>\n"
        )

    return pattern.sub(repl, text)


md_text = render_markdown_figures(md_text)

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "smarty"],
    output_format="html",
)

html_body = re.sub(r"(\d+)\^(\d+)", r"\1<sup>\2</sup>", html_body)
html_body = re.sub(r"(\d+)\^\((\d[^)]*)\)", r"\1<sup>\2</sup>", html_body)
html_body = re.sub(r"10\^-(\d+)", r"10<sup>-\1</sup>", html_body)

css = """
@page {
    size: letter;
    margin: 0.85in 0.85in 0.85in 0.85in;
    @bottom-center { content: counter(page); font-size: 10pt; color: #666; }
}
body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.50;
    color: #1a1a1a;
    max-width: 100%;
}
h1 {
    font-size: 18pt;
    text-align: center;
    margin-bottom: 0.3em;
    line-height: 1.25;
}
h2 {
    font-size: 14pt;
    margin-top: 1.55em;
    border-bottom: 1px solid #ccc;
    padding-bottom: 0.2em;
    page-break-after: avoid;
}
h3 {
    font-size: 12pt;
    margin-top: 1.2em;
    page-break-after: avoid;
}
table {
    border-collapse: collapse;
    width: 100%;
    font-size: 8.5pt;
    margin: 1em 0;
    break-inside: avoid;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #999;
    padding: 4px 5px;
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
    margin: 1.1em auto;
    page-break-inside: avoid;
}
figcaption {
    font-size: 9pt;
    line-height: 1.35;
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
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 1.5em 0;
}
em {
    font-style: italic;
}
code {
    font-family: monospace;
    font-size: 9.5pt;
    background: #f5f5f5;
    padding: 1px 3px;
}
"""

full_html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>{css}</style>
</head><body>
{html_body}
</body></html>
"""

HTML(string=full_html, base_url=str(paper_dir)).write_pdf(str(pdf_path))
print(f"PDF saved to: {pdf_path}")
