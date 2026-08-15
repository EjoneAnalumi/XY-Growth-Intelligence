# Week 3 Day 14 Snapshot-to-Report Integration Evidence

Date: 15-08-2026

Branch: `feature/snapshot-report-integration`

## Scope

Complete the safe synthetic snapshot-to-report flow: persist approved snapshot evidence, produce reports from that evidence, and review report wording, disclaimers, and role access.

## Implemented

- Added durable `security_scans` and `security_findings` tables, indexes, RLS, and report foreign-key linkage in matching Supabase and database migrations.
- `POST /security-scans/snapshot` records the approved scope note, timestamps, and every structured result before returning a snapshot ID.
- `POST /reports/generate` accepts only `security_scan_id`; it derives company, domain, findings, and completion date from the completed approved snapshot instead of trusting browser-supplied text.
- Report HTML and paginated PDF include every persisted check's name, status, severity, method, summary, and escaped synthetic evidence. Error and timeout outcomes remain neutral check outcomes rather than vulnerability claims.
- The report HTML uses cautious observation language and includes scope, limitations, and a disclaimer that it is neither a penetration test nor confirmation of compromise.
- The scan page creates a report from the persisted snapshot ID. The reports page enables generation only with that ID.
- The reports page previews the selected server-generated report HTML in a sandboxed iframe; it no longer contains static company or finding data.
- Unknown snapshot IDs return `404`; snapshots that are not approved and completed return `409`. Storage and database operational failures continue to return `503`.

## Security Notes

- The demonstrated path uses approved synthetic `.example` targets only.
- Stored snapshot evidence prevents report inputs from being forged in the browser.
- Technical Analyst, Management, and Admin may scan and generate/submit reports. Only Management and Admin may approve, download approved reports, share internally, or archive them.
- No automatic external sharing, credentials, service-role keys, real customer data, or real prospect data were added.

## Verification

Commands run:

```powershell
cd backend
python -m pytest tests\test_snapshot_scanning.py -q -p no:cacheprovider
python -m pytest tests\test_reports.py -q -p no:cacheprovider
python -m pytest tests\test_snapshot_scanning.py tests\test_reports.py -q -p no:cacheprovider
python -m pytest . -q -p no:cacheprovider
python -m ruff check app tests
cd ..\frontend
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
```

Results:

- Targeted Day 14 snapshot/report tests with local Supabase integration: `29 passed`.
- Full backend suite with local Supabase integration: `79 passed`.
- Ruff: passed.
- Frontend typecheck, lint, and production build: passed.

## Remaining TODO

- No Day 14 MVP TODOs remain. Future scope should remain limited to the planned CSV and handover work.
