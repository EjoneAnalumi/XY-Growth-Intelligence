from __future__ import annotations

from contextlib import closing
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from app.core.config import Settings, get_settings
from app.schemas.security_scans import SnapshotResponse
from app.schemas.users import CurrentUser


class SnapshotPersistenceError(RuntimeError):
    """Safe operational error for unavailable snapshot persistence."""


LOCAL_COMPANY_NAMES = {
    "10000000-0000-4000-8000-000000000001": "Northstar Robotics Labs",
}


class InMemorySnapshotRepository:
    def __init__(self) -> None:
        self._scans: dict[str, dict[str, Any]] = {}
        self._findings: dict[str, list[dict[str, Any]]] = {}

    def reset(self) -> None:
        self._scans.clear()
        self._findings.clear()

    def persist(
        self, company_id: str, approval_note: str, scan: SnapshotResponse, current_user: CurrentUser
    ) -> dict[str, Any]:
        scan_id = str(uuid4())
        scan_record = {
            "id": scan_id,
            "company_id": company_id,
            "company_name": LOCAL_COMPANY_NAMES.get(company_id, "Northstar Robotics Labs"),
            "initiated_by": current_user.id,
            "domain": scan.domain,
            "approval_note": approval_note,
            "approved": True,
            "status": "completed",
            "started_at": scan.started_at,
            "completed_at": scan.completed_at,
            "duration_ms": scan.duration_ms,
            "created_at": datetime.now(UTC),
        }
        findings = [
            {
                "check_name": result.check,
                "status": result.status,
                "summary": result.summary,
                "finding": result.finding,
                "severity": result.severity,
                "method": result.method,
                "evidence": list(result.evidence),
                "error_classification": result.error_classification,
                "details": dict(result.details),
            }
            for result in scan.results
        ]
        self._scans[scan_id] = scan_record
        self._findings[scan_id] = findings
        return {**scan.model_dump(), "id": scan_id}

    def add_ineligible_scan(self, scan_id: str, company_id: str) -> None:
        self._scans[scan_id] = {
            "id": scan_id,
            "company_id": company_id,
            "company_name": LOCAL_COMPANY_NAMES.get(company_id, "Northstar Robotics Labs"),
            "domain": "northstar-robotics.example",
            "approved": False,
            "status": "running",
            "completed_at": datetime.now(UTC),
        }
        self._findings[scan_id] = []

    def scan_context(self, scan_id: str) -> dict[str, Any] | None:
        scan = self._scans.get(scan_id)
        if scan is None:
            return None

        finding_summaries = [
            finding["summary"] for finding in self._findings.get(scan_id, []) if finding["finding"]
        ]
        return {
            **scan,
            "scan_summary": "; ".join(finding_summaries)
            or "No potential risks were observed in this snapshot.",
        }

    def scan_findings(self, scan_id: str) -> list[dict[str, Any]]:
        return list(self._findings.get(scan_id, []))


class SupabaseSnapshotRepository:
    def __init__(self, settings: Settings) -> None:
        if not settings.database_url:
            raise SnapshotPersistenceError("Snapshot database is not configured.")
        self.database_url = settings.database_url

    def persist(
        self, company_id: str, approval_note: str, scan: SnapshotResponse, current_user: CurrentUser
    ) -> dict[str, Any]:
        scan_id = uuid4()
        try:
            with self._connection() as connection, connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.security_scans (
                        id, company_id, initiated_by, domain, approval_note, approved, status,
                        started_at, completed_at, duration_ms
                    ) VALUES (%s, %s, %s, %s, %s, true, 'completed', %s, %s, %s)
                    """,
                    (scan_id, company_id, current_user.id, scan.domain, approval_note,
                     scan.started_at, scan.completed_at, scan.duration_ms),
                )
                for result in scan.results:
                    cursor.execute(
                        """
                        INSERT INTO public.security_findings (
                            security_scan_id, check_name, status, summary, finding, severity,
                            method, evidence, error_classification, details
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb)
                        """,
                        (scan_id, result.check, result.status, result.summary, result.finding,
                         result.severity, result.method, Jsonb(result.evidence),
                         result.error_classification, Jsonb(result.details)),
                    )
                connection.commit()
        except psycopg.Error as exc:
            raise SnapshotPersistenceError("Snapshot evidence could not be saved.") from exc
        return {**scan.model_dump(), "id": scan_id}

    def _connection(self):
        try:
            return closing(psycopg.connect(self.database_url))
        except psycopg.Error as exc:
            raise SnapshotPersistenceError("Snapshot database is unavailable.") from exc


in_memory_snapshot_repository = InMemorySnapshotRepository()


def get_snapshot_repository() -> SupabaseSnapshotRepository | InMemorySnapshotRepository:
    settings = get_settings()
    if settings.database_url and settings.supabase_url and settings.supabase_service_role_key:
        return SupabaseSnapshotRepository(settings)

    return in_memory_snapshot_repository
