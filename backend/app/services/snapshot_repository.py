from __future__ import annotations

from contextlib import closing
from typing import Any
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from app.core.config import Settings, get_settings
from app.schemas.security_scans import SnapshotResponse
from app.schemas.users import CurrentUser


class SnapshotPersistenceError(RuntimeError):
    """Safe operational error for unavailable snapshot persistence."""


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


def get_snapshot_repository() -> SupabaseSnapshotRepository:
    return SupabaseSnapshotRepository(get_settings())
