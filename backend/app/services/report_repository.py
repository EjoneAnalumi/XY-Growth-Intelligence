from __future__ import annotations

from base64 import b64encode
from contextlib import closing
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import httpx
import psycopg
from psycopg.rows import dict_row

from app.core.config import Settings, get_settings
from app.reporting.assembly import assemble_report_html
from app.reporting.pdf import render_pdf_bytes
from app.schemas.reports import ReportGenerateRequest
from app.schemas.users import CurrentUser
from app.services.snapshot_repository import in_memory_snapshot_repository

REPORT_STORAGE_BUCKET = "reports"


class ReportPersistenceError(RuntimeError):
    """Safe operational error for unavailable report persistence services."""


class ReportScanNotFoundError(RuntimeError):
    """The referenced snapshot does not exist."""


class ReportScanIneligibleError(RuntimeError):
    """The referenced snapshot is not approved and complete."""


class InMemoryReportRepository:
    def __init__(self) -> None:
        self._reports: dict[str, dict[str, Any]] = {}
        self._files: dict[str, bytes] = {}

    def reset(self) -> None:
        self._reports.clear()
        self._files.clear()

    def list_reports(self) -> list[dict[str, Any]]:
        return sorted(self._reports.values(), key=lambda report: report["created_at"])

    def generate_report(
        self, payload: ReportGenerateRequest, current_user: CurrentUser
    ) -> dict[str, Any]:
        self._require_role(current_user, {"admin", "management", "technical_analyst"})
        context = in_memory_snapshot_repository.scan_context(str(payload.security_scan_id))
        if context is None:
            raise ReportScanNotFoundError("Snapshot was not found.")
        if context["status"] != "completed" or not context["approved"]:
            raise ReportScanIneligibleError("Snapshot is not approved and complete.")

        report_id = str(uuid4())
        findings = in_memory_snapshot_repository.scan_findings(str(payload.security_scan_id))
        title = f"Cyber Risk Snapshot - {context['company_name']}"
        completed_at = context["completed_at"].strftime("%d-%m-%Y %H:%M UTC")
        html = assemble_report_html(
            company_name=context["company_name"],
            domain=context["domain"],
            scan_summary=context["scan_summary"],
            completed_at=completed_at,
            findings=findings,
        )
        pdf = render_pdf_bytes(title, html)
        object_path = f"{report_id}/{uuid4()}.pdf"
        self._files[object_path] = pdf
        now = datetime.now(UTC)
        report = {
            "id": report_id,
            "company_id": context["company_id"],
            "security_scan_id": str(payload.security_scan_id),
            "is_legacy": False,
            "company_name": context["company_name"],
            "domain": context["domain"],
            "title": title,
            "status": "draft",
            "storage_bucket": REPORT_STORAGE_BUCKET,
            "storage_path": object_path,
            "download_url": None,
            "html_preview": html,
            "created_by": current_user.id,
            "reviewed_by": None,
            "approved_by": None,
            "shared_by": None,
            "archived_by": None,
            "created_at": now,
            "updated_at": now,
            "reviewed_at": None,
            "approved_at": None,
            "shared_at": None,
            "archived_at": None,
        }
        self._reports[report_id] = report
        return report

    def submit_for_review(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        return self._transition(
            report_id,
            "review",
            current_user,
            {"admin", "management", "technical_analyst"},
            {"draft": "review"},
        )

    def approve_report(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        return self._transition(
            report_id,
            "approved",
            current_user,
            {"admin", "management"},
            {"review": "approved"},
        )

    def share_report(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        return self._transition(
            report_id,
            "shared",
            current_user,
            {"admin", "management"},
            {"approved": "shared"},
        )

    def archive_report(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        return self._transition(
            report_id,
            "archived",
            current_user,
            {"admin", "management"},
            {"shared": "archived"},
        )

    def download_report(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        self._require_role(current_user, {"admin", "management"})
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

    def _transition(
        self,
        report_id: str,
        target_status: str,
        current_user: CurrentUser,
        allowed_roles: set[str],
        allowed_transition: dict[str, str],
    ) -> dict[str, Any] | None:
        self._require_role(current_user, allowed_roles)
        report = self._reports.get(report_id)
        if report is None or allowed_transition.get(report["status"]) != target_status:
            return None

        now = datetime.now(UTC)
        report["status"] = target_status
        report["updated_at"] = now
        if target_status == "review":
            report["reviewed_by"] = current_user.id
            report["reviewed_at"] = now
        elif target_status == "approved":
            report["approved_by"] = current_user.id
            report["approved_at"] = now
            report["download_url"] = f"/reports/{report_id}/download"
        elif target_status == "shared":
            report["shared_by"] = current_user.id
            report["shared_at"] = now
            report["download_url"] = None
        elif target_status == "archived":
            report["archived_by"] = current_user.id
            report["archived_at"] = now
            report["download_url"] = None

        return report

    @staticmethod
    def _require_role(current_user: CurrentUser, allowed_roles: set[str]) -> None:
        if current_user.role not in allowed_roles:
            raise PermissionError("User does not have permission to perform this action.")


class SupabaseReportRepository:
    def __init__(self, settings: Settings) -> None:
        if not settings.database_url:
            raise ReportPersistenceError("Report database is not configured.")
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise ReportPersistenceError("Report storage is not configured.")
        self.database_url = settings.database_url
        self.storage_url = settings.supabase_url.rstrip("/") + "/storage/v1"
        self.service_key = settings.supabase_service_role_key

    def list_reports(self) -> list[dict[str, Any]]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(self._report_select() + " ORDER BY r.created_at")
            return [self._serialize(row) for row in cursor.fetchall()]

    def generate_report(
        self,
        payload: ReportGenerateRequest,
        current_user: CurrentUser,
        *,
        report_id: UUID | None = None,
    ) -> dict[str, Any]:
        self._require_role(current_user, {"admin", "management", "technical_analyst"})
        report_id = report_id or uuid4()
        context = self._scan_context(str(payload.security_scan_id))
        findings = self._scan_findings(str(payload.security_scan_id))
        title = f"Cyber Risk Snapshot - {context['company_name']}"
        html = assemble_report_html(
            company_name=context["company_name"],
            domain=context["domain"],
            scan_summary=context["scan_summary"],
            completed_at=context["completed_at"].strftime("%d-%m-%Y %H:%M UTC"),
            findings=findings,
        )
        pdf = render_pdf_bytes(title, html)
        object_path = f"{report_id}/{uuid4()}.pdf"
        self._upload(object_path, pdf)

        try:
            with (
                self._connection() as connection,
                connection.cursor(row_factory=dict_row) as cursor,
            ):
                self._set_actor(cursor, current_user)
                cursor.execute(
                    """
                    INSERT INTO public.reports (
                        id, company_id, security_scan_id, title, status, storage_bucket,
                        storage_path,
                        html_preview, created_by
                    ) VALUES (%s, %s, %s, %s, 'draft', %s, %s, %s, %s)
                    """,
                    (
                        report_id,
                        context["company_id"],
                        payload.security_scan_id,
                        title,
                        REPORT_STORAGE_BUCKET,
                        object_path,
                        html,
                        current_user.id,
                    ),
                )
                cursor.execute(
                    """
                    INSERT INTO public.report_files (
                        report_id, storage_bucket, storage_path, content_type, size_bytes,
                        created_by
                    ) VALUES (%s, %s, %s, 'application/pdf', %s, %s)
                    """,
                    (report_id, REPORT_STORAGE_BUCKET, object_path, len(pdf), current_user.id),
                )
                cursor.execute(self._report_select(" WHERE r.id = %s"), (report_id,))
                row = cursor.fetchone()
                connection.commit()
                return self._serialize(row)
        except Exception:
            self._delete_object(object_path)
            raise

    def submit_for_review(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        return self._transition(
            report_id, "review", current_user, {"admin", "management", "technical_analyst"}
        )

    def approve_report(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        return self._transition(report_id, "approved", current_user, {"admin", "management"})

    def share_report(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        return self._transition(report_id, "shared", current_user, {"admin", "management"})

    def archive_report(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        return self._transition(report_id, "archived", current_user, {"admin", "management"})

    def download_report(self, report_id: str, current_user: CurrentUser) -> dict[str, Any] | None:
        self._require_role(current_user, {"admin", "management"})
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                self._report_select(" WHERE r.id = %s AND r.status = 'approved'"), (report_id,)
            )
            row = cursor.fetchone()
        if row is None or row["file_path"] is None:
            return None
        pdf = self._download(row["file_path"])
        return {
            "id": row["id"],
            "filename": f"{row['title'].replace(' ', '_')}.pdf",
            "content_type": row["content_type"],
            "storage_bucket": row["file_bucket"],
            "storage_path": row["file_path"],
            "size_bytes": len(pdf),
            "content_base64": b64encode(pdf).decode("ascii"),
        }

    def _transition(
        self, report_id: str, target_status: str, current_user: CurrentUser, allowed_roles: set[str]
    ) -> dict[str, Any] | None:
        self._require_role(current_user, allowed_roles)
        try:
            with (
                self._connection() as connection,
                connection.cursor(row_factory=dict_row) as cursor,
            ):
                self._set_actor(cursor, current_user)
                cursor.execute(
                    "UPDATE public.reports SET status = %s WHERE id = %s RETURNING id",
                    (target_status, report_id),
                )
                if cursor.fetchone() is None:
                    connection.rollback()
                    return None
                cursor.execute(self._report_select(" WHERE r.id = %s"), (report_id,))
                row = cursor.fetchone()
                connection.commit()
                return self._serialize(row)
        except psycopg.Error:
            return None

    def _connection(self):
        try:
            return closing(psycopg.connect(self.database_url))
        except psycopg.Error as exc:
            raise ReportPersistenceError("Report database is unavailable.") from exc

    def _scan_context(self, scan_id: str) -> dict[str, Any]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT s.id, s.company_id, s.domain, s.approved, s.status, s.completed_at,
                    c.name AS company_name,
                    COALESCE(
                        string_agg(f.summary, '; ' ORDER BY f.severity DESC, f.check_name)
                            FILTER (WHERE f.finding),
                        'No potential risks were observed in this snapshot.'
                    )
                        AS scan_summary
                FROM public.security_scans s
                JOIN public.companies c ON c.id = s.company_id
                LEFT JOIN public.security_findings f ON f.security_scan_id = s.id
                WHERE s.id = %s
                GROUP BY s.id, c.name
                """,
                (scan_id,),
            )
            context = cursor.fetchone()
        if context is None:
            raise ReportScanNotFoundError("Snapshot was not found.")
        if context["status"] != "completed" or not context["approved"]:
            raise ReportScanIneligibleError("Snapshot is not approved and complete.")
        return context

    def _scan_findings(self, scan_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT check_name, status, severity, method, summary, finding, evidence
                FROM public.security_findings
                WHERE security_scan_id = %s
                ORDER BY check_name
                """,
                (scan_id,),
            )
            return cursor.fetchall()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.service_key}", "apikey": self.service_key}

    def _upload(self, object_path: str, pdf: bytes) -> None:
        try:
            response = httpx.post(
                f"{self.storage_url}/object/{REPORT_STORAGE_BUCKET}/{object_path}",
                content=pdf,
                headers={**self._headers(), "Content-Type": "application/pdf", "x-upsert": "false"},
                timeout=15,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ReportPersistenceError("Report PDF upload failed.") from exc

    def _download(self, object_path: str) -> bytes:
        try:
            response = httpx.get(
                f"{self.storage_url}/object/{REPORT_STORAGE_BUCKET}/{object_path}",
                headers=self._headers(),
                timeout=15,
            )
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as exc:
            raise ReportPersistenceError("Report PDF download failed.") from exc

    def _delete_object(self, object_path: str) -> None:
        try:
            httpx.delete(
                f"{self.storage_url}/object/{REPORT_STORAGE_BUCKET}/{object_path}",
                headers=self._headers(),
                timeout=15,
            )
        except httpx.HTTPError:
            pass

    @staticmethod
    def _set_actor(cursor: Any, current_user: CurrentUser) -> None:
        cursor.execute(
            "SELECT set_config('app.report_actor_id', %s, true)", (str(current_user.id),)
        )
        cursor.execute("SELECT set_config('app.report_actor_role', %s, true)", (current_user.role,))

    @staticmethod
    def _require_role(current_user: CurrentUser, allowed_roles: set[str]) -> None:
        if current_user.role not in allowed_roles:
            raise PermissionError("User does not have permission to perform this action.")

    @staticmethod
    def _report_select(where: str = "") -> str:
        return (
            """
            SELECT r.*, c.name AS company_name, c.domain,
                   f.storage_bucket AS file_bucket, f.storage_path AS file_path,
                   f.content_type, f.size_bytes
            FROM public.reports r
            JOIN public.companies c ON c.id = r.company_id
            LEFT JOIN public.report_files f ON f.report_id = r.id
        """
            + where
        )

    @staticmethod
    def _serialize(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "company_id": row["company_id"],
            "security_scan_id": row["security_scan_id"],
            "is_legacy": row["security_scan_id"] is None,
            "company_name": row["company_name"],
            "domain": row["domain"] or "",
            "title": row["title"],
            "status": row["status"],
            "storage_bucket": row["file_bucket"],
            "storage_path": row["file_path"],
            "download_url": f"/reports/{row['id']}/download"
            if row["status"] == "approved"
            else None,
            "html_preview": row["html_preview"],
            "created_by": row["created_by"],
            "reviewed_by": row["reviewed_by"],
            "approved_by": row["approved_by"],
            "shared_by": row["shared_by"],
            "archived_by": row["archived_by"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "reviewed_at": row["reviewed_at"],
            "approved_at": row["approved_at"],
            "shared_at": row["shared_at"],
            "archived_at": row["archived_at"],
        }


in_memory_report_repository = InMemoryReportRepository()


def get_report_repository() -> SupabaseReportRepository | InMemoryReportRepository:
    settings = get_settings()
    if settings.database_url and settings.supabase_url and settings.supabase_service_role_key:
        return SupabaseReportRepository(settings)

    return in_memory_report_repository
