from html import escape

from app.schemas.reports import ReportGenerateRequest


def assemble_report_html(payload: ReportGenerateRequest) -> str:
    company_name = escape(payload.company_name)
    domain = escape(payload.domain)
    scan_summary = escape(payload.scan_summary)

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8" />',
            "<title>XY CYBER Risk Snapshot</title>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>XY CYBER Cyber Risk Snapshot</h1>",
            "<p><strong>Confidential - Internal preview</strong></p>",
            f"<h2>{company_name}</h2>",
            f"<p>Approved demo domain: {domain}</p>",
            "<h3>Executive summary</h3>",
            f"<p>{scan_summary}</p>",
            "<h3>Methodology and limitations</h3>",
            "<p>This synthetic report is based on approved demo snapshot evidence. "
            "It is not a penetration test or confirmation of compromise.</p>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )
