# Week 3 Day 11 Snapshot Validation Evidence

Date: 12-08-2026

Branch: `feature/snapshot-domain-checks`

## Scope

Day 11 Intern 1 requires:

- Snapshot request validation.
- Domain normalization.
- DNS checks.
- TLS checks.
- Timeout handling.
- Approved demo checks returning structured results.

## Implemented

- Added `POST /security-scans/snapshot`.
- Added request and response schemas for snapshot checks.
- Added domain normalization:
  - strips scheme
  - strips path/query
  - lowercases hostnames
  - rejects IP addresses
  - rejects localhost and malformed hostnames
- Added explicit approval validation.
- Added role protection:
  - Admin, Management, and Technical Analyst can run snapshot checks.
  - Business Development and Read Only cannot run snapshot checks.
- Added deterministic `.example` demo results for safe evidence.
- Added bounded DNS and TLS checks for non-demo domains with timeout handling.
- Added server-side live domain allowlist enforcement.
- Added public-IP validation after DNS resolution.
- Added TLS connection to a validated public IP while preserving hostname verification.
- Added structured security/audit logs for scan start and completion.

## Demo Result

Request:

```json
{
  "domain": "https://demo.xy-cyber.example/snapshot",
  "approved": true,
  "approval_note": "Approved internal demo target.",
  "timeout_seconds": 1
}
```

Expected structured checks:

- approval: pass
- dns: pass
- tls: pass

The `.example` path intentionally returns mock results so tests and demos do not scan real systems.

## Security Notes

- No real customer/prospect domains were added.
- No credentials, API keys, or secrets were added.
- Snapshot checks require explicit approval.
- Demo `.example` domains use mock results.
- Live DNS/TLS checks are bounded by a request timeout.
- Request approval alone is not enough for live checks; live domains must be in the server-side allowlist.
- Private, local, link-local, reserved, multicast, and unspecified resolved IPs are rejected before TLS connection.
- DNS/TLS failures are classified as structured failure/timeout results.

## Verification

Commands:

```powershell
cd backend
python -m pytest
python -m ruff check .
```

Expected:

- Snapshot validation tests pass.
- Full backend test suite passes.
- Ruff reports no issues.

Latest local result:

```text
python -m pytest backend -q -p no:cacheprovider
55 passed, 1 skipped

python -m ruff check backend
All checks passed!
```

## Remaining TODO

- Persist scan records and findings in Supabase.
- Add HTTP header, SPF, and DMARC checks.
- Add report linkage after the report workflow starts.
- Add frontend snapshot request UI in the Intern 2 task.
