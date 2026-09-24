"""Keep unit tests isolated when a local Supabase environment is configured.

The production repository switches to PostgreSQL when ``DATABASE_URL`` is set.
Most API tests intentionally exercise the in-memory repository, whereas the
named integration modules connect to PostgreSQL directly.  Exporting local
Supabase variables for the whole test run must not make unit tests mutate the
seeded demonstration dataset.
"""

from __future__ import annotations

import pytest

POSTGRES_INTEGRATION_MODULES = {
    "test_company_csv.py",
    "test_crm_postgres_persistence.py",
    "test_reports.py",
    "test_seed_dataset.py",
    "test_seed_reports.py",
    "test_week2_rls_permissions.py",
}


@pytest.fixture(autouse=True)
def isolate_unit_repositories(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> None:
    """Prevent in-memory unit cases from writing fixed fixtures to local seed data."""
    if request.fspath.basename not in POSTGRES_INTEGRATION_MODULES:
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
