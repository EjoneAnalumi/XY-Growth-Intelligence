# Week 3 Day 12 Snapshot Email Security Evidence

Date: 12-08-2026

Branch: `feature/snapshot-email-security`

## Scope

Day 12 Intern 1 only:

- HTTP security header checks.
- SPF and DMARC DNS TXT checks.
- Structured finding severity.
- Error classification that does not turn failed checks into findings.

## Implemented

- Extended `POST /security-scans/snapshot` with `http_headers`, `spf`, and `dmarc` results for approved live targets.
- Added deterministic synthetic results for those checks on `.example` demo domains; no network calls are made for demo targets.
- Added structured result fields: `finding`, `severity`, `method`, `evidence`, and optional `error_classification`.
- Added HTTP header observations for Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, and Referrer-Policy.
- Added SPF and DMARC TXT lookups with bounded resolver timeout/lifetime using `dnspython`.
- Added severity-rated observations for missing headers, missing SPF/DMARC records, multiple SPF records, and DMARC `p=none`.
- Classified timeouts, DNS failures, HTTP failures, non-final HTTP responses, and dependency skips as non-findings with `severity: info`.

## Security Notes

- Only existing server-side allowlisted live targets can reach network checks.
- HTTP uses one bounded HTTPS `HEAD` request to a previously validated public DNS address with TLS hostname verification.
- SPF/DMARC checks perform TXT resolution only; no mail delivery, authentication testing, exploitation, or enumeration occurs.
- Findings use the language “Potential risk” and include method/evidence.
- Failed checks are not findings. They return a structured `error`, `timeout`, or `skipped` status with `finding: false`.
- No real domains, credentials, API keys, service-role keys, or customer/prospect data were added.

## Verification

Commands run:

```powershell
cd backend
python -m pytest tests\test_snapshot_scanning.py -q -p no:cacheprovider
python -m ruff check .
```

Output:

```text
19 passed in 1.30s
All checks passed!
```

Required full backend verification:

```powershell
cd backend
python -m pytest -p no:cacheprovider
python -m ruff check .
```

Output:

```text
69 passed in 3.04s
All checks passed!
```

## Remaining TODO

- Persist scans and findings in Supabase after the snapshot storage slice is implemented.
- Update the Intern 2 snapshot adapter to render the backend-provided `finding`, `severity`, and `error_classification` fields rather than deriving severity from status.
- Report assembly and approval workflow remain Day 13 and Day 14 work.
