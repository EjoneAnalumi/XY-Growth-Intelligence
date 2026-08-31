"""Local Supabase seed acceptance checks for the brief's deterministic demo dataset."""

from __future__ import annotations

import socket
from urllib.parse import urlparse

import psycopg
import pytest

DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def _connection():
    parsed = urlparse(DATABASE_URL)
    try:
        with socket.create_connection((parsed.hostname, parsed.port or 5432), timeout=5):
            pass
    except OSError as exc:  # pragma: no cover - local environment dependent
        pytest.skip(f"Local Supabase database is unavailable: {exc}")
    return psycopg.connect(DATABASE_URL, connect_timeout=5)


def test_seed_dataset_includes_brief_required_reports_and_scans() -> None:
    with _connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                (SELECT count(*) FROM public.companies
                 WHERE id::text LIKE '10000000-0000-4000-8000-%'),
                (SELECT count(*) FROM public.contacts
                 WHERE id::text LIKE '20000000-0000-4000-8000-%'),
                (SELECT count(*) FROM public.opportunities
                 WHERE id::text LIKE '60000000-0000-4000-8000-%'),
                (SELECT count(*) FROM public.activities
                 WHERE id::text LIKE '40000000-0000-4000-8000-%'),
                (SELECT count(*) FROM public.tasks
                 WHERE id::text LIKE '70000000-0000-4000-8000-%'),
                (SELECT count(*) FROM public.reports
                 WHERE id::text LIKE '90000000-0000-4000-8000-%'),
                (SELECT count(*) FROM public.security_scans
                 WHERE id::text LIKE '80000000-0000-4000-8000-%'),
                (SELECT count(*) FROM public.reports r
                 JOIN public.security_scans s ON s.id = r.security_scan_id
                 WHERE r.id::text LIKE '90000000-0000-4000-8000-%'),
                (SELECT count(DISTINCT status) FROM public.reports
                 WHERE id::text LIKE '90000000-0000-4000-8000-%'),
                (SELECT count(DISTINCT f.status) FROM public.security_findings f
                 JOIN public.security_scans s ON s.id = f.security_scan_id
                 WHERE s.id::text LIKE '80000000-0000-4000-8000-%')
            """
        )
        counts = cursor.fetchone()

    assert counts == (30, 50, 20, 40, 25, 5, 5, 5, 5, 5)
