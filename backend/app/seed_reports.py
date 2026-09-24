"""Complete local synthetic seed data with real report PDFs in private Storage."""

from urllib.parse import urlparse
from uuid import UUID

from app.core.config import Settings
from app.schemas.reports import ReportGenerateRequest
from app.schemas.users import CurrentUser
from app.services.report_repository import SupabaseReportRepository

STATUSES = ("draft", "review", "approved", "shared", "archived")
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
ANALYST = CurrentUser(
    id="00000000-0000-4000-8000-000000000004",
    email="analyst.demo@example.test",
    full_name="Synthetic Analyst",
    role="technical_analyst",
)
MANAGEMENT = CurrentUser(
    id="00000000-0000-4000-8000-000000000002",
    email="management.demo@example.test",
    full_name="Synthetic Management",
    role="management",
)


def seed_reports(settings: Settings) -> list[str]:
    """Create missing fixed-ID reports; never reset or rewind a finished report."""
    if settings.app_env != "local" or any(
        urlparse(url or "").hostname not in LOCAL_HOSTS
        for url in (settings.database_url, settings.supabase_url)
    ):
        raise ValueError(
            "Report seeding requires APP_ENV=local and loopback database/Storage URLs."
        )
    repository = SupabaseReportRepository(settings)
    # Upgrade only Day 19's exact synthetic placeholders, never genuine report content.
    with repository._connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """DELETE FROM public.reports r
               WHERE r.id = ANY(%s::uuid[]) AND r.storage_path IS NULL
               AND r.html_preview = ANY(%s::text[])
               AND NOT EXISTS (SELECT 1 FROM public.report_files f WHERE f.report_id = r.id)""",
            (
                [f"90000000-0000-4000-8000-{i:012d}" for i in range(1, 6)],
                [
                    f"<html><body>Synthetic {status} report. Methodology and limitations "
                    "included.</body></html>"
                    for status in STATUSES
                ],
            ),
        )
        connection.commit()
    existing = {str(row["id"]): row for row in repository.list_reports()}
    report_ids = []
    for index, target in enumerate(STATUSES, 1):
        report_id = f"90000000-0000-4000-8000-{index:012d}"
        report = existing.get(report_id)
        if report is None:
            report = repository.generate_report(
                ReportGenerateRequest(
                    security_scan_id=UUID(f"80000000-0000-4000-8000-{index:012d}")
                ),
                ANALYST,
                report_id=UUID(report_id),
            )
        if not report["storage_path"]:
            raise RuntimeError("A seeded report has no file; inspect it before reseeding.")
        # Also verifies the stored object exists on a repeated run; no false success.
        if not repository._download(report["storage_path"]).startswith(b"%PDF-"):
            raise RuntimeError("A seeded report object is not a PDF.")
        while STATUSES.index(report["status"]) < STATUSES.index(target):
            transition, actor = {
                "draft": (repository.submit_for_review, ANALYST),
                "review": (repository.approve_report, MANAGEMENT),
                "approved": (repository.share_report, MANAGEMENT),
                "shared": (repository.archive_report, MANAGEMENT),
            }[report["status"]]
            report = transition(report_id, actor)
            if report is None:
                raise RuntimeError("Synthetic report workflow transition failed.")
        report_ids.append(report_id)
    return report_ids


if __name__ == "__main__":
    seed_reports(Settings())
    print("Verified 5 synthetic reports with private PDF objects; existing states preserved.")
