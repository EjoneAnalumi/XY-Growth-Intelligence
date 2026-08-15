from __future__ import annotations

import os
from base64 import b64decode
from io import BytesIO

import httpx
import psycopg
import pytest
from app.main import app
from fastapi.testclient import TestClient
from pypdf import PdfReader

pytestmark = pytest.mark.skipif(
    not all(
        os.getenv(name) for name in ("DATABASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
    ),
    reason="Report persistence integration requires local Supabase environment variables.",
)

client = TestClient(app)
ANALYST = {"Authorization": "Bearer dev-technical-analyst"}
MANAGEMENT = {"Authorization": "Bearer dev-management"}
ADMIN = {"Authorization": "Bearer dev-admin"}
BD = {"Authorization": "Bearer dev-business-development"}
READ_ONLY = {"Authorization": "Bearer dev-read-only"}


def _payload() -> dict:
    return {
        "company_id": "10000000-0000-4000-8000-000000000001",
        "company_name": "Northstar Robotics Labs",
        "domain": "northstar-robotics.example",
        "scan_summary": "Approved demo snapshot with SPF pass, DMARC monitoring, and missing CSP.",
    }


def _generate() -> dict:
    response = client.post("/reports/generate", headers=ANALYST, json=_payload())
    assert response.status_code == 201, response.text
    return response.json()


def test_persists_report_file_and_private_pdf_object() -> None:
    report = _generate()
    with psycopg.connect(os.environ["DATABASE_URL"]) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, company_id, created_by, status, created_at "
            "FROM public.reports WHERE id = %s",
            (report["id"],),
        )
        persisted_report = cursor.fetchone()
        cursor.execute(
            "SELECT report_id, storage_bucket, storage_path, content_type, size_bytes "
            "FROM public.report_files WHERE report_id = %s",
            (report["id"],),
        )
        persisted_file = cursor.fetchone()
        cursor.execute("SELECT public FROM storage.buckets WHERE id = 'reports'")
        bucket_is_public = cursor.fetchone()[0]
    assert persisted_report is not None
    assert str(persisted_report[1]) == report["company_id"]
    assert str(persisted_report[2]) == "00000000-0000-4000-8000-000000000004"
    assert persisted_report[3] == "draft"
    assert persisted_report[4].tzinfo is not None
    assert persisted_file is not None
    assert str(persisted_file[0]) == report["id"]
    assert persisted_file[1:4] == ("reports", report["storage_path"], "application/pdf")
    assert bucket_is_public is False

    object_response = httpx.get(
        f"{os.environ['SUPABASE_URL']}/storage/v1/object/reports/{report['storage_path']}",
        headers={
            "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
            "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        },
    )
    assert object_response.status_code == 200
    assert object_response.content.startswith(b"%PDF-")
    anonymous_response = httpx.get(
        f"{os.environ['SUPABASE_URL']}/storage/v1/object/reports/{report['storage_path']}"
    )
    assert anonymous_response.status_code in {400, 401, 403}


def test_workflow_download_and_role_denials() -> None:
    report = _generate()
    report_id = report["id"]
    for headers in (BD, READ_ONLY):
        assert client.post("/reports/generate", headers=headers, json=_payload()).status_code == 403
    assert client.post("/reports/generate", headers=ADMIN, json=_payload()).status_code == 201
    assert (
        client.post(f"/reports/{report_id}/approve", headers=MANAGEMENT, json={}).status_code == 400
    )
    assert client.post(f"/reports/{report_id}/review", headers=ANALYST, json={}).status_code == 200
    assert client.post(f"/reports/{report_id}/approve", headers=ANALYST, json={}).status_code == 403
    assert client.post(f"/reports/{report_id}/approve", headers=BD, json={}).status_code == 403
    assert (
        client.post(f"/reports/{report_id}/approve", headers=READ_ONLY, json={}).status_code == 403
    )
    assert (
        client.post(f"/reports/{report_id}/approve", headers=MANAGEMENT, json={}).status_code == 200
    )
    assert client.post(f"/reports/{report_id}/archive", headers=ANALYST, json={}).status_code == 403

    for headers in (ANALYST, BD, READ_ONLY):
        assert client.get(f"/reports/{report_id}/download", headers=headers).status_code == 403
    download = client.get(f"/reports/{report_id}/download", headers=MANAGEMENT)
    assert download.status_code == 200
    pdf = b64decode(download.json()["content_base64"])
    reader = PdfReader(BytesIO(pdf))
    assert len(reader.pages) == 1
    assert "Northstar Robotics Labs" in (reader.pages[0].extract_text() or "")

    assert (
        client.post(f"/reports/{report_id}/share", headers=MANAGEMENT, json={}).status_code == 200
    )
    assert client.get(f"/reports/{report_id}/download", headers=MANAGEMENT).status_code == 404
    assert (
        client.post(f"/reports/{report_id}/archive", headers=MANAGEMENT, json={}).status_code == 200
    )
    assert (
        client.post(f"/reports/{report_id}/archive", headers=MANAGEMENT, json={}).status_code == 400
    )


def test_direct_database_status_manipulation_is_denied() -> None:
    report = _generate()
    with (
        psycopg.connect(os.environ["DATABASE_URL"], autocommit=False) as connection,
        connection.cursor() as cursor,
    ):
        claims = '{"sub":"00000000-0000-4000-8000-000000000002","role":"authenticated"}'
        cursor.execute(
            "SELECT set_config('request.jwt.claim.sub', %s, true)",
            ("00000000-0000-4000-8000-000000000002",),
        )
        cursor.execute("SELECT set_config('request.jwt.claims', %s, true)", (claims,))
        cursor.execute("SET LOCAL ROLE authenticated")
        with pytest.raises(psycopg.Error):
            cursor.execute(
                "UPDATE public.reports SET status = 'approved' WHERE id = %s", (report["id"],)
            )


def test_openapi_documents_report_endpoints() -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert "/reports/generate" in paths
    assert "/reports/{report_id}/approve" in paths
    assert "/reports/{report_id}/share" in paths
    assert "/reports/{report_id}/download" in paths
