import csv
from io import StringIO
from pathlib import Path

from app.main import app
from app.services.company_csv import CANONICAL_COLUMNS, parse_company_csv
from app.services.growth_repository import repository
from fastapi.testclient import TestClient

client = TestClient(app)
WRITER = {"Authorization": "Bearer dev-business-development"}
READER = {"Authorization": "Bearer dev-read-only"}


def setup_function() -> None:
    repository.reset()


def test_company_csv_import_and_export_round_trip() -> None:
    payload = (
        b"name,domain,industry,employee_count,cloud_usage,tags\n"
        b"Demo One,demo-one.example,Healthcare,120,AWS|Azure,synthetic|priority\n"
        b"Demo Two,demo-two.example,Energy,80,Azure,synthetic\n"
    )
    imported = client.post(
        "/companies/import", headers={**WRITER, "Content-Type": "text/csv"}, content=payload
    )
    assert imported.status_code == 201
    assert imported.json() == {"created": 2}
    exported = client.get("/companies/export", headers=READER)
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    assert exported.content.startswith(b"\xef\xbb\xbf")
    rows = list(csv.DictReader(StringIO(exported.content.decode("utf-8-sig"))))
    assert [row["name"] for row in rows] == ["Demo One", "Demo Two"]
    assert rows[0]["cloud_usage"] == "AWS|Azure"
    assert parse_company_csv(exported.content) == parse_company_csv(payload)


def test_demo_dataset_imports_all_30_companies() -> None:
    dataset = Path(__file__).resolve().parents[2] / "sample-data" / "companies.csv"
    response = client.post(
        "/companies/import",
        headers={**WRITER, "Content-Type": "text/csv"},
        content=dataset.read_bytes(),
    )
    assert response.status_code == 201
    assert response.json() == {"created": 30}
    assert client.get("/companies", headers=READER).json()["total"] == 30


def test_company_csv_import_rejects_invalid_file_without_creating_rows() -> None:
    response = client.post(
        "/companies/import",
        headers={**WRITER, "Content-Type": "text/csv"},
        content=b"name,employee_count\nValid,5\nInvalid,-1\n",
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["details"] == {
        "code": "invalid_rows",
        "issues": [{"row": 3, "field": "employee_count", "code": "greater_than_equal"}],
    }
    assert "-1" not in response.text
    assert client.get("/companies", headers=READER).json()["total"] == 0


def test_read_only_cannot_import_companies() -> None:
    response = client.post(
        "/companies/import",
        headers={**READER, "Content-Type": "text/csv"},
        content=b"name\nDenied\n",
    )
    assert response.status_code == 403


def test_company_csv_rejects_reimport_without_creating_duplicates() -> None:
    dataset = Path(__file__).resolve().parents[2] / "sample-data" / "companies.csv"
    first = client.post(
        "/companies/import",
        headers={**WRITER, "Content-Type": "text/csv"},
        content=dataset.read_bytes(),
    )
    second = client.post(
        "/companies/import",
        headers={**WRITER, "Content-Type": "text/csv"},
        content=dataset.read_bytes(),
    )
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error"]["details"] == {
        "code": "duplicate_company",
        "fields": ["domain", "name"],
    }
    assert client.get("/companies", headers=READER).json()["total"] == 30


def test_company_csv_rejects_unknown_and_duplicate_headers() -> None:
    unknown = client.post(
        "/companies/import",
        headers={**WRITER, "Content-Type": "text/csv"},
        content=b"name,unexpected\nDemo,ignored\n",
    )
    duplicate = client.post(
        "/companies/import",
        headers={**WRITER, "Content-Type": "text/csv"},
        content=b"name,name\nDemo,Duplicate\n",
    )
    assert unknown.status_code == 422
    assert unknown.json()["error"]["details"] == {
        "code": "invalid_headers",
        "issues": [{"field": "unexpected", "code": "unknown_header"}],
    }
    assert duplicate.status_code == 422
    assert duplicate.json()["error"]["details"] == {
        "code": "invalid_headers",
        "issues": [{"field": "name", "code": "duplicate_header"}],
    }


def test_company_csv_handles_utf8_quoting_nulls_numbers_and_dates() -> None:
    payload = (
        "name,domain,industry,employee_count,annual_revenue_usd,last_activity_at,"
        "next_action_due_at,headquarters_city,lead_source\n"
        'München Systems,muenchen.example,"Research, Development",0,0,'
        '2026-08-19T10:00:00Z,,"Munich, Bavaria",\n'
    ).encode()
    response = client.post(
        "/companies/import",
        headers={**WRITER, "Content-Type": "text/csv"},
        content=payload,
    )
    assert response.status_code == 201
    exported = client.get("/companies/export", headers=READER)
    rows = list(csv.DictReader(StringIO(exported.content.decode("utf-8-sig"))))
    assert tuple(rows[0]) == CANONICAL_COLUMNS
    assert rows[0]["industry"] == "Research, Development"
    assert rows[0]["headquarters_city"] == "Munich, Bavaria"
    assert rows[0]["employee_count"] == "0"
    assert rows[0]["annual_revenue_usd"] == "0.0"
    assert rows[0]["next_action_due_at"] == ""
