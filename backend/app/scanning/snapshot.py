import logging
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from datetime import UTC, datetime

from app.scanning.domain import is_public_ip_address, normalize_domain
from app.schemas.security_scans import SnapshotCheckResult, SnapshotResponse

APPROVED_DEMO_DOMAINS = {
    "demo.xy-cyber.example",
    "northstar-robotics.example",
    "blueharbor-finance.example",
    "day-ten-finance.example",
}
APPROVED_LIVE_DOMAINS: set[str] = set()
logger = logging.getLogger(__name__)


class SnapshotScanner:
    def run(self, domain: str, approved: bool, timeout_seconds: float) -> SnapshotResponse:
        if not approved:
            raise ValueError("Snapshot checks require explicit approval.")

        normalized_domain = normalize_domain(domain)
        started_at = datetime.now(UTC)
        logger.info(
            "snapshot_scan_started",
            extra={
                "event": "snapshot_scan_started",
                "domain": normalized_domain,
                "approved": approved,
                "demo_mode": normalized_domain.endswith(".example"),
            },
        )

        if normalized_domain.endswith(".example"):
            results = self._mock_demo_results(normalized_domain)
        elif normalized_domain not in APPROVED_LIVE_DOMAINS:
            results = [
                SnapshotCheckResult(
                    check="approval",
                    status="fail",
                    summary="Domain is not in the server-side approved live scan allowlist.",
                    details={"domain": normalized_domain},
                )
            ]
        else:
            dns_result, addresses = self._check_dns(normalized_domain, timeout_seconds)
            results = [
                self._check_domain_approval(normalized_domain),
                dns_result,
                self._check_tls(normalized_domain, addresses, timeout_seconds),
            ]

        completed_at = datetime.now(UTC)
        logger.info(
            "snapshot_scan_completed",
            extra={
                "event": "snapshot_scan_completed",
                "domain": normalized_domain,
                "result_statuses": [result.status for result in results],
                "duration_ms": int((completed_at - started_at).total_seconds() * 1000),
            },
        )
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
        if domain in APPROVED_DEMO_DOMAINS or domain in APPROVED_LIVE_DOMAINS:
            return SnapshotCheckResult(
                check="approval",
                status="pass",
                summary="Domain is in the server-side approved allowlist.",
                details={"domain": domain},
            )

        return SnapshotCheckResult(
            check="approval",
            status="fail",
            summary="Domain is not in the server-side approved allowlist.",
            details={"domain": domain},
        )

    def _check_dns(
        self,
        domain: str,
        timeout_seconds: float,
    ) -> tuple[SnapshotCheckResult, list[str]]:
        try:
            addresses = self._resolve_addresses(domain, timeout_seconds)
            public_addresses = [
                address for address in addresses if is_public_ip_address(address)
            ]

            if not public_addresses:
                return (
                    SnapshotCheckResult(
                        check="dns",
                        status="fail",
                        summary="DNS resolved only to non-public addresses.",
                        details={"classification": "non_public_address"},
                    ),
                    [],
                )

            return SnapshotCheckResult(
                check="dns",
                status="pass",
                summary="DNS resolution returned public addresses.",
                details={"addresses": public_addresses},
            ), public_addresses
        except TimeoutError:
            return self._timeout_result("dns", timeout_seconds), []
        except socket.gaierror as exc:
            return SnapshotCheckResult(
                check="dns",
                status="fail",
                summary="DNS resolution failed.",
                details={"classification": "dns_resolution_failed", "error": str(exc)},
            ), []

    def _resolve_addresses(self, domain: str, timeout_seconds: float) -> list[str]:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(socket.getaddrinfo, domain, 443)
            try:
                results = future.result(timeout=timeout_seconds)
            except FutureTimeoutError as exc:
                future.cancel()
                raise TimeoutError from exc

        return sorted({result[4][0] for result in results})

    def _check_tls(
        self,
        domain: str,
        addresses: list[str],
        timeout_seconds: float,
    ) -> SnapshotCheckResult:
        if not addresses:
            return SnapshotCheckResult(
                check="tls",
                status="fail",
                summary="TLS check skipped because no public DNS address was available.",
                details={"classification": "dependency_failed"},
            )

        context = ssl.create_default_context()
        address = addresses[0]
        try:
            with socket.create_connection((address, 443), timeout=timeout_seconds) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as tls_sock:
                    certificate = tls_sock.getpeercert()
                    return SnapshotCheckResult(
                        check="tls",
                        status="pass",
                        summary="TLS handshake completed successfully.",
                        details={
                            "address": address,
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
                details={"classification": "tls_handshake_failed", "error": str(exc)},
            )

    def _timeout_result(self, check: str, timeout_seconds: float) -> SnapshotCheckResult:
        return SnapshotCheckResult(
            check=check,
            status="timeout",
            summary=f"{check.upper()} check exceeded the configured timeout.",
            details={"timeout_seconds": timeout_seconds},
        )


snapshot_scanner = SnapshotScanner()
