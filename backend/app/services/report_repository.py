from __future__ import annotations

from base64 import b64encode
from contextlib import closing
from typing import Any
from uuid import uuid4

import httpx
import psycopg
from psycopg.rows import dict_row

from app.core.config import Settings, get_settings
from app.reporting.assembly import assemble_report_html
from app.reporting.pdf import render_pdf_bytes
from app.schemas.reports import ReportGenerateRequest
from app.schemas.users import CurrentUser

REPORT_STORAGE_BUCKET = "reports"


class ReportPersistenceError(RuntimeError):
    """Safe operational error for unavailable report persistence services."""


class ReportScanNotFoundError(RuntimeError):
    """The referenced snapshot does not exist."""


class ReportScanIneligibleError(RuntimeError):
    """The referenced snapshot is not approved and complete."""


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
        self, payload: ReportGenerateRequest, current_user: CurrentUser
    ) -> dict[str, Any]:
        self._require_role(current_user, {"admin", "management", "technical_analyst"})
        report_id = uuid4()
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


def get_report_repository() -> SupabaseReportRepository:
    return SupabaseReportRepository(get_settings())
