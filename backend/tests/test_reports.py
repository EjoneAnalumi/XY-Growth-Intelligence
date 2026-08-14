from base64 import b64decode

from app.main import app
from app.services.report_repository import report_repository
from fastapi.testclient import TestClient

client = TestClient(app)

analyst_headers = {"Authorization": "Bearer dev-technical-analyst"}
management_headers = {"Authorization": "Bearer dev-management"}
writer_headers = {"Authorization": "Bearer dev-business-development"}


def setup_function() -> None:
    report_repository.reset()


def _report_payload() -> dict:
    return {
        "company_id": "10000000-0000-4000-8000-000000000001",
        "company_name": "Northstar Commerce Group",
        "domain": "demo.xy-cyber.example",
        "scan_summary": "Approved demo snapshot with SPF pass, DMARC monitoring, and missing CSP.",
    }


def test_generate_review_approve_and_download_report_pdf() -> None:
    generated = client.post("/reports/generate", headers=analyst_headers, json=_report_payload())

    assert generated.status_code == 201
    report = generated.json()
    assert report["status"] == "draft"
    assert report["storage_bucket"] == "reports"
    assert report["storage_path"].endswith(".pdf")
    assert report["download_url"] is None
    assert "Northstar Commerce Group" in report["html_preview"]

    reviewed = client.post(
        f"/reports/{report['id']}/review",
        headers=analyst_headers,
        json={"note": "Ready for management approval."},
    )

    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "review"

    approved = client.post(
        f"/reports/{report['id']}/approve",
        headers=management_headers,
        json={"note": "Approved for internal demo."},
    )

    assert approved.status_code == 200
    approved_report = approved.json()
    assert approved_report["status"] == "approved"
    assert approved_report["download_url"] == f"/reports/{report['id']}/download"

    download = client.get(f"/reports/{report['id']}/download", headers=management_headers)

    assert download.status_code == 200
    body = download.json()
    assert body["content_type"] == "application/pdf"
    assert body["storage_path"] == report["storage_path"]
    assert b64decode(body["content_base64"]).startswith(b"%PDF-")


def test_business_development_cannot_approve_or_download_report() -> None:
    generated = client.post("/reports/generate", headers=analyst_headers, json=_report_payload())
    report_id = generated.json()["id"]
    client.post(f"/reports/{report_id}/review", headers=analyst_headers, json={})

    approve = client.post(f"/reports/{report_id}/approve", headers=writer_headers, json={})
    download = client.get(f"/reports/{report_id}/download", headers=writer_headers)

    assert approve.status_code == 403
    assert download.status_code == 403


def test_download_requires_approved_report_status() -> None:
    generated = client.post("/reports/generate", headers=analyst_headers, json=_report_payload())
    report_id = generated.json()["id"]

    response = client.get(f"/reports/{report_id}/download", headers=management_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Approved report PDF was not found."}


def test_openapi_documents_report_endpoints() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/reports/generate" in paths
    assert "/reports/{report_id}/approve" in paths
    assert "/reports/{report_id}/download" in paths
