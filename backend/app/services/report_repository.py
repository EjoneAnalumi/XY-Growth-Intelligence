from base64 import b64encode
from datetime import UTC, datetime
from uuid import uuid4

from app.reporting.assembly import assemble_report_html
from app.reporting.pdf import render_pdf_bytes
from app.schemas.reports import ReportGenerateRequest
from app.schemas.users import CurrentUser

REPORT_STORAGE_BUCKET = "reports"


class InMemoryReportRepository:
    def __init__(self) -> None:
        self._reports: dict[str, dict] = {}
        self._files: dict[str, bytes] = {}

    def reset(self) -> None:
        self._reports.clear()
        self._files.clear()

    def list_reports(self) -> list[dict]:
        return sorted(self._reports.values(), key=lambda report: report["created_at"])

    def get_report(self, report_id: str) -> dict | None:
        return self._reports.get(report_id)

    def generate_report(self, payload: ReportGenerateRequest, current_user: CurrentUser) -> dict:
        now = datetime.now(UTC)
        report_id = str(uuid4())
        title = f"Cyber Risk Snapshot - {payload.company_name}"
        html = assemble_report_html(payload)
        pdf = render_pdf_bytes(title, html)
        storage_path = f"reports/{report_id}.pdf"
        self._files[storage_path] = pdf

        report = {
            "id": report_id,
            "company_id": str(payload.company_id),
            "company_name": payload.company_name,
            "domain": payload.domain,
            "title": title,
            "status": "draft",
            "storage_bucket": REPORT_STORAGE_BUCKET,
            "storage_path": storage_path,
            "download_url": None,
            "html_preview": html,
            "created_by": current_user.id,
            "reviewed_by": None,
            "approved_by": None,
            "archived_by": None,
            "created_at": now,
            "updated_at": now,
            "reviewed_at": None,
            "approved_at": None,
            "archived_at": None,
        }
        self._reports[report_id] = report
        return report

    def submit_for_review(self, report_id: str, current_user: CurrentUser) -> dict | None:
        report = self._reports.get(report_id)
        if report is None or report["status"] != "draft":
            return None

        now = datetime.now(UTC)
        report["status"] = "review"
        report["reviewed_by"] = current_user.id
        report["reviewed_at"] = now
        report["updated_at"] = now
        return report

    def approve_report(self, report_id: str, current_user: CurrentUser) -> dict | None:
        report = self._reports.get(report_id)
        if report is None or report["status"] != "review":
            return None

        now = datetime.now(UTC)
        report["status"] = "approved"
        report["approved_by"] = current_user.id
        report["approved_at"] = now
        report["updated_at"] = now
        report["download_url"] = f"/reports/{report_id}/download"
        return report

    def archive_report(self, report_id: str, current_user: CurrentUser) -> dict | None:
        report = self._reports.get(report_id)
        if report is None or report["status"] == "archived":
            return None

        now = datetime.now(UTC)
        report["status"] = "archived"
        report["archived_by"] = current_user.id
        report["archived_at"] = now
        report["updated_at"] = now
        report["download_url"] = None
        return report

    def download_report(self, report_id: str) -> dict | None:
        report = self._reports.get(report_id)
        if report is None or report["status"] != "approved":
            return None

        pdf = self._files.get(report["storage_path"])
        if pdf is None:
            return None

        return {
            "id": report_id,
            "filename": f"{report['title'].replace(' ', '_')}.pdf",
            "content_type": "application/pdf",
            "storage_bucket": report["storage_bucket"],
            "storage_path": report["storage_path"],
            "size_bytes": len(pdf),
            "content_base64": b64encode(pdf).decode("ascii"),
        }


report_repository = InMemoryReportRepository()


def get_report_repository() -> InMemoryReportRepository:
    return report_repository
