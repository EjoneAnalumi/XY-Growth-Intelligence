from __future__ import annotations

import os
from base64 import b64decode
from io import BytesIO

import httpx
import psycopg
import pytest
from app.core.config import get_settings
from app.main import app
from app.services.report_repository import in_memory_report_repository
from app.services.snapshot_repository import in_memory_snapshot_repository
from fastapi.testclient import TestClient
from pypdf import PdfReader

SUPABASE_CONFIGURED = all(
    os.getenv(name) for name in ("DATABASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
)
requires_supabase = pytest.mark.skipif(
    not SUPABASE_CONFIGURED,
    reason="Report persistence integration requires local Supabase environment variables.",
)

client = TestClient(app)
ANALYST = {"Authorization": "Bearer dev-technical-analyst"}
MANAGEMENT = {"Authorization": "Bearer dev-management"}
ADMIN = {"Authorization": "Bearer dev-admin"}
BD = {"Authorization": "Bearer dev-business-development"}
READ_ONLY = {"Authorization": "Bearer dev-read-only"}


def setup_function() -> None:
    if not SUPABASE_CONFIGURED:
        in_memory_snapshot_repository.reset()
        in_memory_report_repository.reset()


def _payload() -> dict:
    scan = client.post(
        "/security-scans/snapshot",
        headers=ANALYST,
        json={
            "company_id": "10000000-0000-4000-8000-000000000001",
            "domain": "northstar-robotics.example",
            "approved": True,
            "approval_note": "Approved internal synthetic demo target.",
        },
    )
    assert scan.status_code == 200, scan.text
    return {"security_scan_id": scan.json()["id"]}


def _generate() -> dict:
    response = client.post("/reports/generate", headers=ANALYST, json=_payload())
    assert response.status_code == 201, response.text
    return response.json()


@requires_supabase
def test_persists_report_file_and_private_pdf_object() -> None:
    report = _generate()
    with psycopg.connect(os.environ["DATABASE_URL"]) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, company_id, security_scan_id, created_by, status, created_at "
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
    assert str(persisted_report[2]) == report["security_scan_id"]
    assert str(persisted_report[3]) == "00000000-0000-4000-8000-000000000004"
    assert persisted_report[4] == "draft"
    assert persisted_report[5].tzinfo is not None
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
    pdf_text = "".join(
        page.extract_text() or "" for page in PdfReader(BytesIO(object_response.content)).pages
    )
    assert "Northstar Robotics Labs" in pdf_text
    assert "northstar-robotics.example" in pdf_text
    assert "Method: deterministic mock" in pdf_text
    assert "v=DMARC1; p=none" in pdf_text
    assert "Methodology and limitations" in pdf_text
    assert "not a penetration test" in pdf_text.lower()
    anonymous_response = httpx.get(
        f"{os.environ['SUPABASE_URL']}/storage/v1/object/reports/{report['storage_path']}"
    )
    assert anonymous_response.status_code in {400, 401, 403}


def test_workflow_download_and_role_denials() -> None:
    report = _generate()
    report_id = report["id"]
    assert "XY CYBER Growth Intelligence" in report["html_preview"]
    assert 'class="cover"' in report["html_preview"]
    assert "penetration test" in report["html_preview"]
    for headers in (BD, READ_ONLY):
        assert (
            client.post("/reports/generate", headers=headers, json=_payload()).status_code
            == 403
        )
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
    pdf_text = "".join(page.extract_text() or "" for page in reader.pages)
    assert len(reader.pages) >= 1
    assert "Northstar Robotics Labs" in pdf_text
    assert "box-shadow" not in pdf_text
    for check in ("approval", "dns", "tls", "http_headers", "spf", "dmarc"):
        assert check in pdf_text

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


@requires_supabase
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


def test_report_generation_rejects_unknown_or_ineligible_snapshot() -> None:
    unknown = client.post(
        "/reports/generate",
        headers=ANALYST,
        json={"security_scan_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"},
    )
    assert unknown.status_code == 404
    assert unknown.json() == {"detail": "Snapshot was not found."}

    ineligible_scan_id = "30000000-0000-4000-8000-000000000099"
    if SUPABASE_CONFIGURED:
        with (
            psycopg.connect(os.environ["DATABASE_URL"]) as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(
                """
                INSERT INTO public.security_scans (
                    id, company_id, initiated_by, domain, approval_note, approved, status,
                    started_at, completed_at, duration_ms
                ) VALUES (%s, %s, %s, %s, %s, false, 'running', now(), now(), 0)
                ON CONFLICT (id) DO UPDATE SET approved = false, status = 'running'
                """,
                (
                    ineligible_scan_id,
                    "10000000-0000-4000-8000-000000000001",
                    "00000000-0000-4000-8000-000000000004",
                    "northstar-robotics.example",
                    "Synthetic scan is not ready for reporting.",
                ),
            )
            connection.commit()
    else:
        in_memory_snapshot_repository.add_ineligible_scan(
            ineligible_scan_id,
            "10000000-0000-4000-8000-000000000001",
        )
    ineligible = client.post(
        "/reports/generate", headers=ANALYST, json={"security_scan_id": ineligible_scan_id}
    )
    assert ineligible.status_code == 409
    assert ineligible.json() == {"detail": "Snapshot is not approved and complete."}


@requires_supabase
def test_list_reports_returns_legacy_report_without_snapshot_link() -> None:
    legacy_report_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1"
    with psycopg.connect(os.environ["DATABASE_URL"]) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT set_config('app.report_actor_id', %s, true)",
            ("00000000-0000-4000-8000-000000000004",),
        )
        cursor.execute(
            "SELECT set_config('app.report_actor_role', %s, true)", ("technical_analyst",)
        )
        cursor.execute(
            """
            INSERT INTO public.reports (
                id, company_id, security_scan_id, title, status, html_preview, created_by
            ) VALUES (%s, %s, NULL, %s, 'draft', %s, %s)
            """,
            (
                legacy_report_id,
                "10000000-0000-4000-8000-000000000001",
                "Legacy Day 13 report",
                "<p>Legacy report</p>",
                "00000000-0000-4000-8000-000000000004",
            ),
        )
        connection.commit()

    try:
        response = client.get("/reports", headers=ANALYST)
        assert response.status_code == 200, response.text
        legacy = next(item for item in response.json()["items"] if item["id"] == legacy_report_id)
        assert legacy["security_scan_id"] is None
        assert legacy["is_legacy"] is True
    finally:
        with (
            psycopg.connect(os.environ["DATABASE_URL"]) as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute("DELETE FROM public.reports WHERE id = %s", (legacy_report_id,))
            connection.commit()


def test_report_generation_requires_security_scan_id() -> None:
    response = client.post("/reports/generate", headers=ANALYST, json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "security_scan_id"]


def test_list_reports_uses_safe_local_fallback_when_report_service_is_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    get_settings.cache_clear()
    try:
        response = client.get("/reports", headers=ANALYST)
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


def test_openapi_documents_report_endpoints() -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert "/reports/generate" in paths
    assert "/reports/{report_id}/approve" in paths
    assert "/reports/{report_id}/share" in paths
    assert "/reports/{report_id}/download" in paths
