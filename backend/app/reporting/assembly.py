from html import escape
from typing import Any

REPORT_STYLES = [
    ":root{color:#17202a;background:#f5f7fb;font-family:Inter,Arial,sans-serif;}",
    "body{margin:0;background:#f5f7fb;color:#17202a;}",
    "main{max-width:960px;margin:0 auto;background:#fff;"
    "box-shadow:0 18px 50px rgba(15,23,42,.12);}",
    ".cover{background:#111827;color:#fff;padding:42px 48px;}",
    ".brand{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#9dd7c8;}",
    ".confidential{display:inline-block;margin-top:28px;"
    "border:1px solid rgba(255,255,255,.24);"
    "border-radius:999px;padding:7px 12px;font-size:12px;color:#d1d5db;}",
    "h1{margin:18px 0 10px;font-size:40px;line-height:1.08;}",
    ".subtitle{max-width:680px;color:#d1d5db;font-size:16px;line-height:1.7;}",
    ".meta{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:22px 48px;"
    "background:#eef7f4;border-bottom:1px solid #d8e6e1;}",
    ".meta div{background:#fff;border:1px solid #dbe5e1;border-radius:8px;padding:13px;}",
    ".meta span,.eyebrow{display:block;color:#64748b;font-size:12px;"
    "text-transform:uppercase;letter-spacing:.06em;font-weight:700;}",
    ".meta strong{display:block;margin-top:5px;font-size:14px;}",
    ".section{padding:32px 48px;border-bottom:1px solid #e5e7eb;}",
    "h2{margin:0 0 14px;font-size:22px;}",
    "h3{margin:0 0 12px;font-size:18px;}",
    "p{line-height:1.65;}",
    ".summary{font-size:16px;color:#334155;}",
    ".finding{border:1px solid #e5e7eb;border-radius:8px;padding:18px;margin-top:14px;"
    "background:#fbfcfe;}",
    ".finding-heading{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;}",
    "h4{margin:0;font-size:16px;text-transform:capitalize;}",
    ".badge{border-radius:999px;padding:5px 10px;font-size:12px;font-weight:700;"
    "text-transform:uppercase;}",
    ".severity-info{background:#e5e7eb;color:#374151;}",
    ".severity-low{background:#fef3c7;color:#92400e;}",
    ".severity-medium{background:#ffedd5;color:#9a3412;}",
    ".severity-high{background:#fee2e2;color:#991b1b;}",
    ".method{font-size:13px;color:#475569;}",
    ".evidence{border-left:3px solid #0f766e;margin-top:12px;padding-left:12px;color:#334155;}",
    ".evidence p{margin:0 0 6px;font-weight:700;}",
    "ul{margin:0;padding-left:18px;}",
    ".disclaimer{background:#fffbeb;color:#713f12;}",
    ".footer{padding:18px 48px;color:#64748b;font-size:12px;background:#f8fafc;}",
    "@media(max-width:720px){.cover,.section,.meta,.footer{padding-left:24px;"
    "padding-right:24px;}.meta{grid-template-columns:1fr;}h1{font-size:32px;}}",
]


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

    observations = [
        item for item in findings if item["finding"] and item["status"] not in {"error", "timeout"}
    ]
    weights = {"info": 0, "low": 5, "medium": 15, "high": 30}
    exposure_score = min(100, sum(weights.get(item["severity"], 0) for item in observations))
    findings = sorted(findings, key=lambda item: weights.get(item["severity"], 0), reverse=True)

    def posture(checks: set[str]) -> str:
        items = [item for item in findings if item["check_name"] in checks]
        return (
            "".join(
                f"<li>{escape(item['check_name'])}: {escape(item['summary'])} "
                f"({escape(item['status'])})</li>"
                for item in items
            )
            or "<li>Not assessed in this snapshot; no assurance is implied.</li>"
        )

    actions = (
        "".join(
            f"<li>Validate the {escape(item['check_name'])} observation with the system owner, "
            "confirm business relevance, and agree a remediation and retest date.</li>"
            for item in observations
        )
        or "<li>Review scope and incomplete checks with the system owner "
        "before drawing conclusions.</li>"
    )
    has_email_observation = any(item["check_name"] in {"spf", "dmarc"} for item in observations)
    primary_service = (
        "Email security review" if has_email_observation else "External exposure review"
    )
    secondary_service = "Cloud and application security assessment"
    finding_sections = []
    for finding in findings:
        evidence = finding["evidence"]
        evidence_list = "".join(f"<li>{escape(item)}</li>" for item in evidence)
        potential_risk = "Potential risk" if finding["finding"] else "Check outcome"
        severity = escape(finding["severity"])
        finding_sections.extend(
            [
                '<article class="finding">',
                '<div class="finding-heading">',
                f"<h4>{escape(finding['check_name'])}</h4>",
                f'<span class="badge severity-{severity}">{severity}</span>',
                "</div>",
                f'<p class="eyebrow">{potential_risk} - {escape(finding["status"])}</p>',
                f"<p>{escape(finding['summary'])}</p>",
                f'<p class="method">Method: {escape(finding["method"])}</p>',
                (
                    f'<div class="evidence"><p>Evidence</p><ul>{evidence_list}</ul></div>'
                    if evidence_list
                    else '<div class="evidence"><p>Evidence: none recorded.</p></div>'
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
            '<meta name="viewport" content="width=device-width, initial-scale=1" />',
            "<title>XY CYBER Risk Snapshot</title>",
            "<style>",
            *REPORT_STYLES,
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            '<section class="cover">',
            '<div class="brand">XY CYBER Growth Intelligence</div>',
            '<span class="confidential">Confidential - internal preview</span>',
            "<h1>Cyber Risk Snapshot</h1>",
            (
                '<p class="subtitle">A concise, evidence-led view of externally observable '
                f"security posture for {company_name}.</p>"
            ),
            "</section>",
            '<section class="meta">',
            f"<div><span>Prepared for</span><strong>{company_name}</strong></div>",
            f"<div><span>Approved target</span><strong>{domain}</strong></div>",
            f"<div><span>Snapshot completed</span><strong>{completed_at}</strong></div>",
            "</section>",
            '<section class="section">',
            "<h2>Executive Summary</h2>",
            f'<p class="summary">{scan_summary}</p>',
            f"<p>Overall exposure indicator: {exposure_score}/100 "
            "(synthetic triage heuristic).</p>",
            "<p>Weights: low 5, medium 15, high 30 per observation; capped at 100. "
            "Errors and timeouts contribute zero and indicate unknown coverage, not safety. "
            "This is not a validated risk rating or a probability of compromise.</p>",
            "</section>",
            '<section class="section">',
            "<h2>Snapshot Findings And Evidence</h2>",
            "<p>Findings are ordered by severity, highest first; check errors remain explicit.</p>",
            *finding_sections,
            "</section>",
            '<section class="section">',
            "<h2>Email security posture</h2>",
            f"<ul>{posture({'spf', 'dmarc'})}</ul>",
            "<h2>Web and TLS posture</h2>",
            f"<ul>{posture({'tls', 'https', 'http_headers'})}</ul>",
            "<h2>Public asset overview</h2>",
            f"<p>Approved target: {domain}. Only this target is in scope; "
            "no asset discovery was performed.</p>",
            f"<ul>{posture({'dns'})}</ul>",
            "<h2>Business impact</h2>",
            "<p>Email authentication observations may affect trust in outbound mail. Web and TLS "
            "observations may affect service trust and availability. Actual impact depends on "
            "business context and requires validation; no breach or compromise is established.</p>",
            "<h2>Recommended actions</h2>",
            f"<ul>{actions}</ul>",
            "<h2>Recommended XY CYBER services and next engagement</h2>",
            f"<p>Primary: {primary_service}. Secondary: {secondary_service}.</p>",
            "<p>The primary recommendation follows observed email findings when present, otherwise "
            "the external target scope. Confirm service fit in a scoped discovery meeting with "
            "Business Development and a Technical Analyst before commissioning work.</p>",
            "</section>",
            '<section class="section disclaimer">',
            "<h2>Methodology and limitations</h2>",
            "<p>Scope was limited to approved synthetic demo evidence. This report is not a "
            "penetration test, assurance statement, or confirmation of compromise. Observations "
            "require technical validation before external use.</p>",
            "</section>",
            (
                '<footer class="footer">XY CYBER Growth Intelligence - Synthetic report '
                "preview only.</footer>"
            ),
            "</main>",
            "</body>",
            "</html>",
        ]
    )
