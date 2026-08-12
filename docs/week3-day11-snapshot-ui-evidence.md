# Week 3 Day 11 Snapshot UI Evidence

Date: 12-08-2026

Branch: `feature/snapshot-scan-ui`

## Scope

Day 11 Intern 2 requires:

- Scope confirmation.
- Scan status.
- Findings list.
- Evidence display.
- Severity filters.
- User can initiate and inspect a mock or approved scan.

## Implemented

- Added `/security-scans` route.
- Added navigation link for Security Scans.
- Added snapshot API client and TypeScript scan types.
- Added scope confirmation form:
  - domain or URL
  - approval evidence
  - timeout seconds
  - approval checkbox
- Added scan status states:
  - idle
  - validating
  - running
  - complete
  - failed
- Added evidence panel with normalized domain, approval state, timestamps, duration, and check count.
- Added findings list from structured API results.
- Added severity filter for:
  - all
  - info
  - low
  - medium
  - high
- Added demo role selection on login so Technical Analyst can run snapshot checks.

## Demo Flow

1. Start backend and frontend.
2. Sign in as Technical Analyst.
3. Open `/security-scans`.
4. Keep the default approved `.example` demo URL.
5. Run snapshot scan.
6. Confirm status changes and results are displayed.
7. Filter findings by severity.

## Security Notes

- No real customer/prospect domains were added.
- Default scan target is synthetic: `demo.xy-cyber.example`.
- UI requires explicit approval checkbox before calling the API.
- Backend still enforces role permissions and approval validation.

## Verification

Commands:

```powershell
cd frontend
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build

cd ..\backend
python -m pytest backend -q -p no:cacheprovider
python -m ruff check backend
```

## Remaining TODO

- Persist scans and findings after backend storage is implemented.
- Add frontend display for HTTP header, SPF, and DMARC checks after those backend checks exist.
