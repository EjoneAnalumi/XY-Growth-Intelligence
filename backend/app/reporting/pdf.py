"""Convert the escaped report HTML to a branded, offline PDF."""

import re
from io import BytesIO
from pathlib import Path

import reportlab
from xhtml2pdf import pisa
from xhtml2pdf.files import ResourceAccessPolicy

# ReportLab ships redistributable Bitstream Vera fonts for accented Latin text.
FONT_DIR = Path(reportlab.__file__).parent / "fonts"

PRINT_CSS = """
@font-face { font-family: ReportVera; src: url("report-font:regular"); }
@font-face { font-family: ReportVera; src: url("report-font:bold"); font-weight: bold; }
@page { size: a4; margin: 18mm; }
body { font-family: ReportVera; font-size: 10pt; color: #17202a; }
h1 { font-size: 28pt; color: #0f766e; margin-bottom: 12pt; }
h2 { font-size: 16pt; color: #0f766e; margin-top: 18pt; margin-bottom: 8pt;
     -pdf-keep-with-next: true; }
h3, h4 { font-size: 12pt; -pdf-keep-with-next: true; }
p { margin: 4pt 0 9pt; line-height: 1.5; }
.brand { font-size: 12pt; color: #0f766e; font-weight: bold; }
.confidential { font-size: 9pt; color: #475569; }
.meta { background-color: #eef7f4; padding: 10pt; }
.meta span { color: #475569; }
.finding { margin-top: 12pt; padding: 8pt; border-bottom: 1pt solid #cbd5e1; }
.badge { font-weight: bold; color: #475569; }
.severity-high { color: #991b1b; }
.severity-medium { color: #9a3412; }
.method, .evidence { font-size: 9pt; }
.disclaimer { background-color: #fffbeb; padding: 10pt; }
.footer { color: #64748b; font-size: 8pt; margin-top: 16pt; }
li { margin-bottom: 5pt; }
"""


def deny_resource(uri: str, relative: str | None = None) -> str:
    """Never fetch URLs or arbitrary local files while generating a report."""
    if uri in {"report-font:regular", "report-font:bold"}:
        return str(FONT_DIR / ("Vera.ttf" if uri.endswith("regular") else "VeraBd.ttf"))
    raise ValueError("External PDF resources are not permitted.")


def render_pdf_bytes(title: str, html: str) -> bytes:
    # Preserve the preview body and replace screen CSS with print-compatible CSS.
    document = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.I | re.S)
    if "</head>" in document:
        document = document.replace("</head>", f"<style>{PRINT_CSS}</style></head>")
    else:
        document = f"<html><head><style>{PRINT_CSS}</style></head><body>{document}</body></html>"
    output = BytesIO()
    result = pisa.CreatePDF(
        document,
        dest=output,
        encoding="utf-8",
        link_callback=deny_resource,
        context_meta={"title": title, "author": "XY CYBER"},
        resource_policy=ResourceAccessPolicy(allow_remote=False, base_dir=FONT_DIR),
    )
    if result.err:
        raise ValueError("Report PDF could not be rendered.")
    return output.getvalue()
