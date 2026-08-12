import socket
import ssl
from datetime import UTC, datetime

from app.scanning.domain import normalize_domain
from app.schemas.security_scans import SnapshotCheckResult, SnapshotResponse

APPROVED_DEMO_DOMAINS = {
    "demo.xy-cyber.example",
    "northstar-robotics.example",
    "blueharbor-finance.example",
    "day-ten-finance.example",
}


class SnapshotScanner:
    def run(self, domain: str, approved: bool, timeout_seconds: float) -> SnapshotResponse:
        if not approved:
            raise ValueError("Snapshot checks require explicit approval.")

        normalized_domain = normalize_domain(domain)
        started_at = datetime.now(UTC)

        if normalized_domain.endswith(".example"):
            results = self._mock_demo_results(normalized_domain)
        else:
            results = [
                self._check_domain_approval(normalized_domain),
                self._check_dns(normalized_domain, timeout_seconds),
                self._check_tls(normalized_domain, timeout_seconds),
            ]

        completed_at = datetime.now(UTC)
        return SnapshotResponse(
            domain=normalized_domain,
            approved=True,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=int((completed_at - started_at).total_seconds() * 1000),
            results=results,
        )

    def _mock_demo_results(self, domain: str) -> list[SnapshotCheckResult]:
        return [
            SnapshotCheckResult(
                check="approval",
                status="pass",
                summary="Domain is an approved synthetic demo target.",
                details={"domain": domain, "mode": "mock"},
            ),
            SnapshotCheckResult(
                check="dns",
                status="pass",
                summary="Synthetic DNS result returned for demo safety.",
                details={"addresses": ["203.0.113.10"], "record_type": "A"},
            ),
            SnapshotCheckResult(
                check="tls",
                status="pass",
                summary="Synthetic TLS result returned for demo safety.",
                details={
                    "issuer": "XY CYBER Demo CA",
                    "expires_in_days": 90,
                    "protocol": "TLSv1.3",
                },
            ),
        ]

    def _check_domain_approval(self, domain: str) -> SnapshotCheckResult:
        if domain in APPROVED_DEMO_DOMAINS:
            return SnapshotCheckResult(
                check="approval",
                status="pass",
                summary="Domain is in the approved demo allowlist.",
                details={"domain": domain},
            )

        return SnapshotCheckResult(
            check="approval",
            status="warning",
            summary="Domain was approved in the request but is not a built-in demo domain.",
            details={"domain": domain},
        )

    def _check_dns(self, domain: str, timeout_seconds: float) -> SnapshotCheckResult:
        previous_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout_seconds)
        try:
            addresses = sorted({result[4][0] for result in socket.getaddrinfo(domain, 443)})
            return SnapshotCheckResult(
                check="dns",
                status="pass",
                summary="DNS resolution returned one or more addresses.",
                details={"addresses": addresses},
            )
        except TimeoutError:
            return self._timeout_result("dns", timeout_seconds)
        except socket.gaierror as exc:
            return SnapshotCheckResult(
                check="dns",
                status="fail",
                summary="DNS resolution failed.",
                details={"error": str(exc)},
            )
        finally:
            socket.setdefaulttimeout(previous_timeout)

    def _check_tls(self, domain: str, timeout_seconds: float) -> SnapshotCheckResult:
        context = ssl.create_default_context()
        try:
            with socket.create_connection((domain, 443), timeout=timeout_seconds) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as tls_sock:
                    certificate = tls_sock.getpeercert()
                    return SnapshotCheckResult(
                        check="tls",
                        status="pass",
                        summary="TLS handshake completed successfully.",
                        details={
                            "protocol": tls_sock.version(),
                            "not_after": certificate.get("notAfter"),
                        },
                    )
        except TimeoutError:
            return self._timeout_result("tls", timeout_seconds)
        except (OSError, ssl.SSLError) as exc:
            return SnapshotCheckResult(
                check="tls",
                status="fail",
                summary="TLS handshake failed.",
                details={"error": str(exc)},
            )

    def _timeout_result(self, check: str, timeout_seconds: float) -> SnapshotCheckResult:
        return SnapshotCheckResult(
            check=check,
            status="timeout",
            summary=f"{check.upper()} check exceeded the configured timeout.",
            details={"timeout_seconds": timeout_seconds},
        )


snapshot_scanner = SnapshotScanner()
