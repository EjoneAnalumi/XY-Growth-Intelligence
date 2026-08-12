import pytest
from app.main import app
from app.scanning.domain import normalize_domain
from fastapi.testclient import TestClient

client = TestClient(app)

analyst_headers = {"Authorization": "Bearer dev-technical-analyst"}
writer_headers = {"Authorization": "Bearer dev-business-development"}


def test_normalize_domain_strips_scheme_path_and_case() -> None:
    assert normalize_domain(" HTTPS://Demo.XY-Cyber.Example/path?q=1 ") == (
        "demo.xy-cyber.example"
    )


@pytest.mark.parametrize(
    "domain",
    ["127.0.0.1", "localhost", "bad_domain", "https://"],
)
def test_normalize_domain_rejects_unsafe_or_invalid_targets(domain: str) -> None:
    with pytest.raises(ValueError):
        normalize_domain(domain)


def test_snapshot_requires_explicit_approval() -> None:
    response = client.post(
        "/security-scans/snapshot",
        headers=analyst_headers,
        json={
            "domain": "demo.xy-cyber.example",
            "approved": False,
            "approval_note": "Missing approval.",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Snapshot checks require explicit approval."}


def test_snapshot_rejects_business_development_role() -> None:
    response = client.post(
        "/security-scans/snapshot",
        headers=writer_headers,
        json={
            "domain": "demo.xy-cyber.example",
            "approved": True,
            "approval_note": "Approved internal demo target.",
        },
    )

    assert response.status_code == 403


def test_approved_demo_snapshot_returns_structured_results() -> None:
    response = client.post(
        "/security-scans/snapshot",
        headers=analyst_headers,
        json={
            "domain": "https://Demo.XY-Cyber.Example/snapshot",
            "approved": True,
            "approval_note": "Approved internal demo target.",
            "timeout_seconds": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "demo.xy-cyber.example"
    assert body["approved"] is True
    assert body["duration_ms"] >= 0
    assert [result["check"] for result in body["results"]] == ["approval", "dns", "tls"]
    assert {result["status"] for result in body["results"]} == {"pass"}
    assert body["results"][1]["details"]["addresses"] == ["203.0.113.10"]


def test_openapi_documents_snapshot_endpoint() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/security-scans/snapshot" in response.json()["paths"]
