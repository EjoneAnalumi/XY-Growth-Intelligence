import logging
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from datetime import UTC, datetime
from http.client import HTTPException, HTTPSConnection
from typing import Any

import dns.exception
import dns.resolver

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
                    method="server-side allowlist",
                    error_classification="target_not_allowlisted",
                    details={"domain": normalized_domain},
                )
            ]
        else:
            dns_result, addresses = self._check_dns(normalized_domain, timeout_seconds)
            results = [
                self._check_domain_approval(normalized_domain),
                dns_result,
                self._check_tls(normalized_domain, addresses, timeout_seconds),
                self._check_http_headers(normalized_domain, addresses, timeout_seconds),
                self._check_spf(normalized_domain, timeout_seconds),
                self._check_dmarc(normalized_domain, timeout_seconds),
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
                method="server-side allowlist",
                evidence=["demo target matched server-side allowlist"],
                details={"domain": domain, "mode": "mock"},
            ),
            SnapshotCheckResult(
                check="dns",
                status="pass",
                summary="Synthetic DNS result returned for demo safety.",
                method="deterministic mock",
                evidence=["A 203.0.113.10"],
                details={"addresses": ["203.0.113.10"], "record_type": "A"},
            ),
            SnapshotCheckResult(
                check="tls",
                status="pass",
                summary="Synthetic TLS result returned for demo safety.",
                method="deterministic mock",
                evidence=["TLSv1.3", "expires in 90 days"],
                details={
                    "issuer": "XY CYBER Demo CA",
                    "expires_in_days": 90,
                    "protocol": "TLSv1.3",
                },
            ),
            SnapshotCheckResult(
                check="http_headers",
                status="observation",
                summary="Potential risk: synthetic response is missing Content-Security-Policy.",
                finding=True,
                severity="medium",
                method="deterministic mock",
                evidence=[
                    "strict-transport-security: max-age=31536000",
                    "x-content-type-options: nosniff",
                ],
                details={
                    "missing_headers": ["content-security-policy"],
                    "observed_headers": [
                        "strict-transport-security",
                        "x-content-type-options",
                        "x-frame-options",
                        "referrer-policy",
                    ],
                },
            ),
            SnapshotCheckResult(
                check="spf",
                status="pass",
                summary="Synthetic SPF record was found.",
                method="deterministic mock",
                evidence=["v=spf1 include:_spf.xy-cyber.example -all"],
                details={"record_count": 1},
            ),
            SnapshotCheckResult(
                check="dmarc",
                status="observation",
                summary="Potential risk: synthetic DMARC policy is monitoring-only (p=none).",
                finding=True,
                severity="low",
                method="deterministic mock",
                evidence=["v=DMARC1; p=none; rua=mailto:reports@xy-cyber.example"],
                details={"policy": "none", "record_count": 1},
            ),
        ]

    def _check_domain_approval(self, domain: str) -> SnapshotCheckResult:
        if domain in APPROVED_DEMO_DOMAINS or domain in APPROVED_LIVE_DOMAINS:
            return SnapshotCheckResult(
                check="approval",
                status="pass",
                summary="Domain is in the server-side approved allowlist.",
                method="server-side allowlist",
                evidence=["target matched server-side allowlist"],
                details={"domain": domain},
            )

        return SnapshotCheckResult(
            check="approval",
            status="fail",
            summary="Domain is not in the server-side approved allowlist.",
            method="server-side allowlist",
            error_classification="target_not_allowlisted",
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
                        method="socket.getaddrinfo",
                        error_classification="non_public_address",
                        details={"classification": "non_public_address"},
                    ),
                    [],
                )

            return SnapshotCheckResult(
                check="dns",
                status="pass",
                summary="DNS resolution returned public addresses.",
                method="socket.getaddrinfo",
                evidence=[f"A/AAAA {address}" for address in public_addresses],
                details={"addresses": public_addresses},
            ), public_addresses
        except TimeoutError:
            return self._timeout_result("dns", timeout_seconds), []
        except socket.gaierror as exc:
            return SnapshotCheckResult(
                check="dns",
                status="fail",
                summary="DNS resolution failed.",
                method="socket.getaddrinfo",
                error_classification="dns_resolution_failed",
                details={"error": str(exc)},
            ), []

    def _resolve_addresses(self, domain: str, timeout_seconds: float) -> list[str]:
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(socket.getaddrinfo, domain, 443)
            try:
                results = future.result(timeout=timeout_seconds)
            except FutureTimeoutError as exc:
                future.cancel()
                raise TimeoutError from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

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
                method="TLS handshake",
                error_classification="dependency_failed",
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
                        method="TLS handshake",
                        evidence=[f"protocol: {tls_sock.version()}", f"address: {address}"],
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
                method="TLS handshake",
                error_classification="tls_handshake_failed",
                details={"error": str(exc)},
            )

    def _check_http_headers(
        self, domain: str, addresses: list[str], timeout_seconds: float
    ) -> SnapshotCheckResult:
        if not addresses:
            return self._skipped_result("http_headers", "HTTPS request", "dependency_failed")

        required_headers = {
            "content-security-policy": "medium",
            "strict-transport-security": "medium",
            "x-content-type-options": "low",
            "x-frame-options": "low",
            "referrer-policy": "low",
        }
        try:
            response_status, headers = self._fetch_https_headers(
                domain, addresses[0], timeout_seconds
            )
        except TimeoutError:
            return self._timeout_result("http_headers", timeout_seconds)
        except (OSError, HTTPException, ssl.SSLError) as exc:
            return SnapshotCheckResult(
                check="http_headers",
                status="error",
                summary="HTTP header check could not be completed.",
                method="bounded HTTPS HEAD request",
                error_classification="http_request_failed",
                details={"error": str(exc)},
            )

        observed_headers = sorted(headers)
        if response_status >= 300:
            return SnapshotCheckResult(
                check="http_headers",
                status="error",
                summary="HTTP header check did not receive a final successful response.",
                method="bounded HTTPS HEAD request",
                evidence=[f"HTTP {response_status}"],
                error_classification="http_response_not_final",
                details={"response_status": response_status},
            )
        missing_headers = [header for header in required_headers if header not in headers]
        if not missing_headers:
            return SnapshotCheckResult(
                check="http_headers",
                status="pass",
                summary="Required HTTP security headers were observed.",
                method="bounded HTTPS HEAD request",
                evidence=[f"HTTP {response_status}", *observed_headers],
                details={"response_status": response_status, "observed_headers": observed_headers},
            )

        severity = (
            "medium"
            if any(required_headers[header] == "medium" for header in missing_headers)
            else "low"
        )
        return SnapshotCheckResult(
            check="http_headers",
            status="observation",
            summary="Potential risk: one or more HTTP security headers were not observed.",
            finding=True,
            severity=severity,
            method="bounded HTTPS HEAD request",
            evidence=[f"HTTP {response_status}", *observed_headers],
            details={
                "response_status": response_status,
                "missing_headers": missing_headers,
                "observed_headers": observed_headers,
            },
        )

    def _fetch_https_headers(
        self, domain: str, address: str, timeout_seconds: float
    ) -> tuple[int, dict[str, str]]:
        context = ssl.create_default_context()
        connection = HTTPSConnection(domain, timeout=timeout_seconds, context=context)
        try:
            raw_socket = socket.create_connection((address, 443), timeout=timeout_seconds)
            connection.sock = context.wrap_socket(raw_socket, server_hostname=domain)
            connection.request(
                "HEAD",
                "/",
                headers={"Host": domain, "User-Agent": "XY-CYBER-Snapshot/1.0"},
            )
            response = connection.getresponse()
            return response.status, {name.lower(): value for name, value in response.getheaders()}
        finally:
            connection.close()

    def _check_spf(self, domain: str, timeout_seconds: float) -> SnapshotCheckResult:
        return self._check_email_record("spf", domain, domain, timeout_seconds)

    def _check_dmarc(self, domain: str, timeout_seconds: float) -> SnapshotCheckResult:
        return self._check_email_record("dmarc", domain, f"_dmarc.{domain}", timeout_seconds)

    def _check_email_record(
        self, check: str, domain: str, query_name: str, timeout_seconds: float
    ) -> SnapshotCheckResult:
        try:
            records = self._resolve_txt_records(query_name, timeout_seconds)
        except TimeoutError:
            return self._timeout_result(check, timeout_seconds)
        except dns.resolver.LifetimeTimeout:
            return self._timeout_result(check, timeout_seconds)
        except dns.resolver.NXDOMAIN:
            records = []
        except dns.resolver.NoAnswer:
            records = []
        except dns.exception.DNSException as exc:
            return SnapshotCheckResult(
                check=check,
                status="error",
                summary=f"{check.upper()} record lookup could not be completed.",
                method="DNS TXT lookup",
                error_classification="dns_lookup_failed",
                details={"error": str(exc), "query_name": query_name},
            )
        except Exception:
            logger.exception(
                "snapshot_email_record_check_failed",
                extra={"event": "snapshot_email_record_check_failed"},
            )
            return SnapshotCheckResult(
                check=check,
                status="error",
                summary=f"{check.upper()} record lookup could not be completed.",
                method="DNS TXT lookup",
                error_classification="unexpected_check_error",
                details={"query_name": query_name},
            )

        prefix = "v=spf1" if check == "spf" else "v=dmarc1"
        matching_records = [record for record in records if record.lower().startswith(prefix)]
        if not matching_records:
            return SnapshotCheckResult(
                check=check,
                status="observation",
                summary=f"Potential risk: no {check.upper()} record was observed.",
                finding=True,
                severity="medium" if check == "dmarc" else "low",
                method="DNS TXT lookup",
                evidence=records,
                details={"query_name": query_name, "record_count": 0},
            )

        if check == "spf" and len(matching_records) > 1:
            return SnapshotCheckResult(
                check="spf",
                status="observation",
                summary="Potential risk: multiple SPF records were observed.",
                finding=True,
                severity="medium",
                method="DNS TXT lookup",
                evidence=matching_records,
                details={"query_name": domain, "record_count": len(matching_records)},
            )

        details: dict[str, Any] = {"query_name": query_name, "record_count": len(matching_records)}
        if check == "dmarc":
            policy = self._dmarc_policy(matching_records[0])
            details["policy"] = policy
            if policy == "none":
                return SnapshotCheckResult(
                    check="dmarc",
                    status="observation",
                    summary="Potential risk: DMARC policy is monitoring-only (p=none).",
                    finding=True,
                    severity="low",
                    method="DNS TXT lookup",
                    evidence=matching_records,
                    details=details,
                )

        return SnapshotCheckResult(
            check=check,
            status="pass",
            summary=f"{check.upper()} record was observed.",
            method="DNS TXT lookup",
            evidence=matching_records,
            details=details,
        )

    def _resolve_txt_records(self, query_name: str, timeout_seconds: float) -> list[str]:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout_seconds
        resolver.lifetime = timeout_seconds
        response = resolver.resolve(query_name, "TXT")
        return [b"".join(record.strings).decode("utf-8") for record in response]

    def _dmarc_policy(self, record: str) -> str | None:
        for component in record.split(";"):
            name, separator, value = component.strip().partition("=")
            if separator and name.lower() == "p":
                return value.lower()
        return None

    def _skipped_result(self, check: str, method: str, classification: str) -> SnapshotCheckResult:
        return SnapshotCheckResult(
            check=check,
            status="skipped",
            summary=f"{check.replace('_', ' ').capitalize()} check was skipped.",
            method=method,
            error_classification=classification,
        )

    def _timeout_result(self, check: str, timeout_seconds: float) -> SnapshotCheckResult:
        return SnapshotCheckResult(
            check=check,
            status="timeout",
            summary=f"{check.upper()} check exceeded the configured timeout.",
            method="bounded network operation",
            error_classification="timeout",
            details={"timeout_seconds": timeout_seconds},
        )


snapshot_scanner = SnapshotScanner()
