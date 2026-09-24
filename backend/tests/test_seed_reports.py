from base64 import b64decode
from io import BytesIO
from os import getenv
from pathlib import Path

import psycopg
import pytest
from app.core.config import Settings
from app.seed_reports import MANAGEMENT, seed_reports
from app.services.report_repository import SupabaseReportRepository
from pypdf import PdfReader


@pytest.mark.parametrize("field", ["database_url", "supabase_url"])
def test_report_seed_rejects_nonlocal_targets_before_connecting(field: str) -> None:
    settings = Settings()
    settings.database_url = "postgresql://localhost/demo"
    settings.supabase_url = "http://127.0.0.1:54321"
    setattr(settings, field, "https://hosted.example")
    with pytest.raises(ValueError, match="loopback"):
        seed_reports(settings)


@pytest.mark.skipif(
    not all(getenv(key) for key in ("DATABASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")),
    reason="local Supabase database and Storage required",
)
def test_seed_is_repeatable_and_approved_pdf_is_downloadable() -> None:
    settings = Settings()
    first = seed_reports(settings)
    repository = SupabaseReportRepository(settings)
    before = {str(r["id"]): r for r in repository.list_reports() if str(r["id"]) in first}
    assert seed_reports(settings) == first
    after = {str(r["id"]): r for r in repository.list_reports() if str(r["id"]) in first}
    assert before == after
    assert {r["status"] for r in after.values()} == {
        "draft",
        "review",
        "approved",
        "shared",
        "archived",
    }
    download = repository.download_report(first[2], MANAGEMENT)
    assert download is not None
    pdf = PdfReader(BytesIO(b64decode(download["content_base64"])))
    text = " ".join(page.extract_text() or "" for page in pdf.pages)
    assert "XY CYBER" in text
    assert "Methodology and limitations" in text
    assert "deterministic mock" in text
    assert "not a penetration test" in " ".join(text.split())
    # Exercise SQL reseeding twice without committing changes to existing CRM data.
    sql = (Path(__file__).resolve().parents[2] / "database/seed/seed.sql").read_text()
    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, prepare=False)
            cursor.execute(sql, prepare=False)
        connection.rollback()
    assert {str(r["id"]): r for r in repository.list_reports() if str(r["id"]) in first} == after
