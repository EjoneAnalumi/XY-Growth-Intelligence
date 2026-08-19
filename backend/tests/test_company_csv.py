import csv
from io import StringIO
from pathlib import Path

from app.main import app
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
    rows = list(csv.DictReader(StringIO(exported.text)))
    assert [row["name"] for row in rows] == ["Demo One", "Demo Two"]
    assert rows[0]["cloud_usage"] == "AWS|Azure"


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
    assert client.get("/companies", headers=READER).json()["total"] == 0


def test_read_only_cannot_import_companies() -> None:
    response = client.post(
        "/companies/import",
        headers={**READER, "Content-Type": "text/csv"},
        content=b"name\nDenied\n",
    )
    assert response.status_code == 403
