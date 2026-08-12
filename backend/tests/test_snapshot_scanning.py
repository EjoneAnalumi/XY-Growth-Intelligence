import time

import dns.exception
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
    assert [result["check"] for result in body["results"]] == [
        "approval",
        "dns",
        "tls",
        "http_headers",
        "spf",
        "dmarc",
    ]
    assert body["results"][3]["severity"] == "medium"
    assert body["results"][3]["finding"] is True
    assert body["results"][4]["finding"] is False
    assert body["results"][5]["severity"] == "low"
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
    assert len(body["results"]) == 1
    result = body["results"][0]
    assert result["check"] == "approval"
    assert result["status"] == "fail"
    assert result["finding"] is False
    assert result["severity"] == "info"
    assert result["error_classification"] == "target_not_allowlisted"
    assert result["details"] == {"domain": "example.com"}


def test_dns_check_rejects_non_public_resolved_addresses() -> None:
    scanner = SnapshotScanner()

    scanner._resolve_addresses = lambda domain, timeout_seconds: ["127.0.0.1", "10.0.0.1"]
    dns_result, addresses = scanner._check_dns("internal.example.test", timeout_seconds=1)

    assert addresses == []
    assert dns_result.status == "fail"
    assert dns_result.error_classification == "non_public_address"
    assert dns_result.finding is False


def test_dns_check_rejects_cgnat_resolved_address() -> None:
    scanner = SnapshotScanner()

    scanner._resolve_addresses = lambda domain, timeout_seconds: ["100.64.0.1"]
    dns_result, addresses = scanner._check_dns("cgnat.example.test", timeout_seconds=1)

    assert addresses == []
    assert dns_result.status == "fail"
    assert dns_result.error_classification == "non_public_address"


def test_dns_timeout_is_classified_without_global_socket_timeout() -> None:
    scanner = SnapshotScanner()

    def raise_timeout(domain: str, timeout_seconds: float) -> list[str]:
        raise TimeoutError

    scanner._resolve_addresses = raise_timeout
    dns_result, addresses = scanner._check_dns("slow.example.test", timeout_seconds=0.5)

    assert addresses == []
    assert dns_result.status == "timeout"
    assert dns_result.details["timeout_seconds"] == 0.5


def test_dns_resolution_returns_promptly_after_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    scanner = SnapshotScanner()

    def slow_getaddrinfo(*args: object, **kwargs: object) -> list[object]:
        time.sleep(0.3)
        return []

    monkeypatch.setattr("app.scanning.snapshot.socket.getaddrinfo", slow_getaddrinfo)
    started_at = time.monotonic()
    dns_result, addresses = scanner._check_dns("slow.example.test", timeout_seconds=0.05)

    assert time.monotonic() - started_at < 0.15
    assert addresses == []
    assert dns_result.status == "timeout"


def test_missing_http_headers_is_a_severity_rated_observation() -> None:
    scanner = SnapshotScanner()
    scanner._fetch_https_headers = lambda domain, address, timeout_seconds: (
        200,
        {"x-content-type-options": "nosniff"},
    )

    result = scanner._check_http_headers("approved.example", ["203.0.113.10"], 1)

    assert result.status == "observation"
    assert result.finding is True
    assert result.severity == "medium"
    assert result.details["missing_headers"] == [
        "content-security-policy",
        "strict-transport-security",
        "x-frame-options",
        "referrer-policy",
    ]


def test_http_failure_is_classified_without_creating_a_finding() -> None:
    scanner = SnapshotScanner()

    def raise_connection_error(*args: object, **kwargs: object) -> tuple[int, dict[str, str]]:
        raise OSError("connection refused")

    scanner._fetch_https_headers = raise_connection_error
    result = scanner._check_http_headers("approved.example", ["203.0.113.10"], 1)

    assert result.status == "error"
    assert result.finding is False
    assert result.severity == "info"
    assert result.error_classification == "http_request_failed"


def test_multiple_spf_records_are_a_structured_observation() -> None:
    scanner = SnapshotScanner()
    scanner._resolve_txt_records = lambda query_name, timeout_seconds: [
        "v=spf1 include:mail.example -all",
        "v=spf1 include:other.example -all",
    ]

    result = scanner._check_spf("approved.example", 1)

    assert result.status == "observation"
    assert result.finding is True
    assert result.severity == "medium"
    assert result.details["record_count"] == 2


def test_dmarc_monitoring_policy_is_a_low_severity_observation() -> None:
    scanner = SnapshotScanner()
    scanner._resolve_txt_records = lambda query_name, timeout_seconds: [
        "v=DMARC1; p=none; rua=mailto:reports@example.test"
    ]

    result = scanner._check_dmarc("approved.example", 1)

    assert result.status == "observation"
    assert result.finding is True
    assert result.severity == "low"
    assert result.details["policy"] == "none"


def test_dmarc_record_without_policy_is_not_a_pass() -> None:
    scanner = SnapshotScanner()
    scanner._resolve_txt_records = lambda query_name, timeout_seconds: [
        "v=DMARC1; rua=mailto:reports@example.test"
    ]

    result = scanner._check_dmarc("approved.example", 1)

    assert result.status == "observation"
    assert result.finding is True
    assert result.severity == "medium"
    assert result.details["policy"] is None
    assert result.details["policy_valid"] is False


def test_dmarc_record_with_invalid_policy_is_not_a_pass() -> None:
    scanner = SnapshotScanner()
    scanner._resolve_txt_records = lambda query_name, timeout_seconds: [
        "v=DMARC1; p=monitor; rua=mailto:reports@example.test"
    ]

    result = scanner._check_dmarc("approved.example", 1)

    assert result.status == "observation"
    assert result.finding is True
    assert result.severity == "medium"
    assert result.details["policy"] == "monitor"
    assert result.details["policy_valid"] is False


def test_spf_lookup_error_is_classified_without_creating_a_finding() -> None:
    scanner = SnapshotScanner()

    def raise_dns_error(*args: object, **kwargs: object) -> list[str]:
        raise dns.exception.DNSException("resolver unavailable")

    scanner._resolve_txt_records = raise_dns_error
    result = scanner._check_spf("approved.example", 1)

    assert result.status == "error"
    assert result.finding is False
    assert result.severity == "info"
    assert result.error_classification == "dns_lookup_failed"


def test_openapi_documents_snapshot_endpoint() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/security-scans/snapshot" in response.json()["paths"]
