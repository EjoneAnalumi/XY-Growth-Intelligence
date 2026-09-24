from io import BytesIO

from app.reporting.assembly import assemble_report_html
from app.reporting.pdf import render_pdf_bytes
from pypdf import PdfReader


def test_required_report_sections_and_unknown_coverage_survive_pdf_conversion() -> None:
    html = assemble_report_html(
        company_name="Synthetic <Company>",
        domain="demo.example",
        scan_summary="Mock only",
        completed_at="24-09-2026",
        findings=[
            {
                "check_name": "tls",
                "status": "timeout",
                "severity": "high",
                "finding": False,
                "summary": "TLS check timed out",
                "method": "deterministic mock",
                "evidence": [],
            }
        ],
    )
    assert "Synthetic &lt;Company&gt;" in html
    assert "0/100" in html
    assert "unknown coverage, not safety" in html
    pdf = PdfReader(BytesIO(render_pdf_bytes("Synthetic report", html)))
    text = " ".join(" ".join(p.extract_text() or "" for p in pdf.pages).split())
    for section in (
        "Executive Summary",
        "Email security posture",
        "Web and TLS posture",
        "Public asset overview",
        "Business impact",
        "Recommended actions",
        "Recommended XY CYBER services and next engagement",
        "Methodology and limitations",
    ):
        assert section in text
    assert "TLS check timed out" in text


def test_exposure_indicator_uses_only_observations_and_explains_email_recommendation() -> None:
    html = assemble_report_html(
        company_name="Demo",
        domain="demo.example",
        scan_summary="Mock only",
        completed_at="24-09-2026",
        findings=[
            {
                "check_name": "dmarc",
                "status": "observation",
                "severity": "medium",
                "finding": True,
                "summary": "Monitoring policy",
                "method": "deterministic mock",
                "evidence": ["<script>not executable</script>"],
            }
        ],
    )
    assert "15/100" in html
    assert "Primary: Email security review" in html
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
