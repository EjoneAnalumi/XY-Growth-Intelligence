import pytest
from app.main import app
from app.scanning.domain import normalize_domain
from app.scanning.snapshot import SnapshotScanner
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


def test_non_demo_domain_requires_server_side_allowlist() -> None:
    response = client.post(
        "/security-scans/snapshot",
        headers=analyst_headers,
        json={
            "domain": "example.com",
            "approved": True,
            "approval_note": "Approved in request only.",
            "timeout_seconds": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["results"] == [
        {
            "check": "approval",
            "status": "fail",
            "summary": "Domain is not in the server-side approved live scan allowlist.",
            "details": {"domain": "example.com"},
        }
    ]


def test_dns_check_rejects_non_public_resolved_addresses() -> None:
    scanner = SnapshotScanner()

    scanner._resolve_addresses = lambda domain, timeout_seconds: ["127.0.0.1", "10.0.0.1"]
    dns_result, addresses = scanner._check_dns("internal.example.test", timeout_seconds=1)

    assert addresses == []
    assert dns_result.status == "fail"
    assert dns_result.details["classification"] == "non_public_address"


def test_dns_timeout_is_classified_without_global_socket_timeout() -> None:
    scanner = SnapshotScanner()

    def raise_timeout(domain: str, timeout_seconds: float) -> list[str]:
        raise TimeoutError

    scanner._resolve_addresses = raise_timeout
    dns_result, addresses = scanner._check_dns("slow.example.test", timeout_seconds=0.5)

    assert addresses == []
    assert dns_result.status == "timeout"
    assert dns_result.details["timeout_seconds"] == 0.5


def test_openapi_documents_snapshot_endpoint() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/security-scans/snapshot" in response.json()["paths"]
