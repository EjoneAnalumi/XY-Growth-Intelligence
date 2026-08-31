from __future__ import annotations

import json
import logging
import tomllib
from pathlib import Path

import pytest
from app.core.errors import register_error_handlers
from app.core.logging import JsonFormatter, register_request_logging
from app.main import app
from fastapi import FastAPI
from fastapi.testclient import TestClient

client = TestClient(app)
READER = {"Authorization": "Bearer dev-read-only"}


@pytest.mark.parametrize(
    ("response", "status_code", "code", "detail"),
    [
        (lambda: client.get("/companies"), 401, "unauthorized", "Missing bearer token."),
        (
            lambda: client.post("/companies", headers=READER, json={"name": "Denied"}),
            403,
            "forbidden",
            "User does not have permission to perform this action.",
        ),
        (
            lambda: client.get(
                "/companies/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", headers=READER
            ),
            404,
            "not_found",
            "Company not found.",
        ),
    ],
)
def test_api_errors_use_a_stable_envelope(
    response, status_code: int, code: str, detail: str
) -> None:
    result = response()

    assert result.status_code == status_code
    assert result.json() == {"detail": detail, "error": {"code": code, "message": detail}}


@pytest.mark.parametrize(
    ("method", "path", "status_code", "detail"),
    [
        ("GET", "/does-not-exist", 404, "Not Found"),
        ("POST", "/health", 405, "Method Not Allowed"),
    ],
)
def test_framework_http_errors_use_the_stable_envelope(
    method: str, path: str, status_code: int, detail: str
) -> None:
    response = client.request(method, path)

    assert response.status_code == status_code
    assert response.json() == {
        "detail": detail,
        "error": {"code": "not_found" if status_code == 404 else "http_error", "message": detail},
    }


def test_validation_errors_keep_machine_readable_details() -> None:
    response = client.post("/companies", headers=READER, json={})

    assert response.status_code == 403

    response = client.post(
        "/companies",
        headers={"Authorization": "Bearer dev-business-development"},
        json={"name": "", "employee_count": -1},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Request failed."
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"][0]["loc"] == ["body", "name"]


def test_request_completion_logs_structured_metadata(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        response = client.get("/health")

    assert response.status_code == 200
    record = next(record for record in caplog.records if record.message == "request_completed")
    assert record.event == "request_completed"
    assert record.method == "GET"
    assert record.path == "/health"
    assert record.status_code == 200
    assert isinstance(record.duration_ms, float)


def test_unexpected_errors_are_sanitized_and_logged_without_sensitive_data(
    caplog: pytest.LogCaptureFixture,
) -> None:
    error_app = FastAPI()
    register_request_logging(error_app)
    register_error_handlers(error_app)

    def raise_unexpected_error() -> None:
        raise RuntimeError("database password: sensitive-value")

    error_app.add_api_route("/_test/unexpected-error", raise_unexpected_error, methods=["GET"])
    error_client = TestClient(error_app, raise_server_exceptions=False)
    with caplog.at_level(logging.INFO):
        response = error_client.get(
            "/_test/unexpected-error", headers={"Authorization": "Bearer sensitive-token"}
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error.",
        "error": {"code": "http_error", "message": "Internal server error."},
    }
    unhandled = next(
        record for record in caplog.records if record.message == "unhandled_request_exception"
    )
    completion = next(record for record in caplog.records if record.message == "request_completed")
    assert unhandled.event == "unhandled_request_exception"
    assert unhandled.status_code == 500
    assert completion.event == "request_completed"
    assert completion.status_code == 500
    assert "sensitive-value" not in caplog.text
    assert "sensitive-token" not in caplog.text


def test_json_log_formatter_keeps_request_fields() -> None:
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.event = "request_completed"
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200

    payload = json.loads(JsonFormatter().format(record))

    assert payload["event"] == "request_completed"
    assert payload["method"] == "GET"
    assert payload["path"] == "/health"
    assert payload["status_code"] == 200


def test_migration_mirrors_are_complete_and_security_tables_have_rls() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    database_migrations = repository_root / "database" / "migrations"
    supabase_migrations = repository_root / "supabase" / "migrations"

    database_files = sorted(path.name for path in database_migrations.glob("*.sql"))
    supabase_files = sorted(path.name for path in supabase_migrations.glob("*.sql"))

    assert database_files == supabase_files
    for name in database_files:
        assert (database_migrations / name).read_text(encoding="utf-8") == (
            supabase_migrations / name
        ).read_text(encoding="utf-8")

    migration_sql = "\n".join(
        (database_migrations / name).read_text(encoding="utf-8").lower() for name in database_files
    )
    for table in ("reports", "report_files", "security_scans", "security_findings"):
        assert f"alter table public.{table} enable row level security" in migration_sql


def test_local_supabase_configuration_disables_public_signup() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    with (repository_root / "supabase" / "config.toml").open("rb") as config_file:
        config = tomllib.load(config_file)

    assert config["auth"]["enable_signup"] is False
    assert config["auth"]["email"]["enable_signup"] is True
