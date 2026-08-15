from html import escape
from typing import Any


def assemble_report_html(
    *,
    company_name: str,
    domain: str,
    scan_summary: str,
    completed_at: str,
    findings: list[dict[str, Any]],
) -> str:
    company_name = escape(company_name)
    domain = escape(domain)
    scan_summary = escape(scan_summary)
    completed_at = escape(completed_at)

    finding_sections = []
    for finding in findings:
        evidence = finding["evidence"]
        evidence_list = "".join(f"<li>{escape(item)}</li>" for item in evidence)
        potential_risk = "Potential risk" if finding["finding"] else "Check outcome"
        finding_sections.extend(
            [
                "<article>",
                f"<h4>{escape(finding['check_name'])} - {potential_risk}</h4>",
                (
                    f"<p>Status: {escape(finding['status'])}; "
                    f"Severity: {escape(finding['severity'])}</p>"
                ),
                f"<p>Method: {escape(finding['method'])}</p>",
                f"<p>{escape(finding['summary'])}</p>",
                (
                    f"<p>Evidence:</p><ul>{evidence_list}</ul>"
                    if evidence_list
                    else "<p>Evidence: none recorded.</p>"
                ),
                "</article>",
            ]
        )

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
            f"<p>Snapshot completed: {completed_at}</p>",
            "<h3>Executive summary</h3>",
            f"<p>{scan_summary}</p>",
            "<h3>Methodology and limitations</h3>",
            "<p>Scope was limited to approved synthetic demo evidence. This is not a penetration "
            "test, assurance statement, or confirmation of compromise. Observations require "
            "technical validation before external use.</p>",
            "<h3>Snapshot findings and evidence</h3>",
            *finding_sections,
            "</main>",
            "</body>",
            "</html>",
        ]
    )
