# Week 3 Day 15 Status Report

Date: 17-08-2026

Branch: `feature/week3-demo-gate`

## Completed Outcomes

- Safe snapshot request validation, DNS/TLS timeout handling, HTTP headers, SPF, DMARC, severity, and error classification are implemented.
- Snapshot UI can initiate approved synthetic scans and inspect status, findings, evidence, and severity filters.
- Report workflow can generate, review, approve, download, share internally, and archive a Cyber Risk Snapshot report.
- Snapshot-to-report integration derives report content from stored structured evidence instead of browser-supplied report text.
- Report output has been polished for a more customer-ready HTML preview with XY CYBER branding, metadata, findings, evidence, and disclaimer sections.
- Backend role permissions enforce:
  - Technical Analyst, Management, and Admin can scan/generate/review.
  - Management and Admin can approve/download/share/archive.
  - Business Development and Read Only cannot approve or download.

## Working Demonstration

Start at:

```text
http://localhost:3000/security-scans
```

Test roles:

- Technical Analyst
- Management

Flow demonstrated:

```text
Login -> run approved synthetic snapshot -> create report -> review -> approve -> download PDF -> share internally -> archive
```

## Test Result

Latest local fallback verification:

- Targeted snapshot/report tests: `26 passed, 3 skipped`.
- Full backend tests: `69 passed, 10 skipped`.
- Backend Ruff: passed.
- Frontend typecheck: passed.
- Frontend lint: passed.
- Frontend build: passed.

Skipped tests are Supabase-backed integration checks that require local Supabase database and Storage environment variables.

## Decisions Made

- Kept a safe in-memory local fallback for snapshot/report flow when Supabase runtime credentials are not configured.
- Kept the Supabase-backed path active when `DATABASE_URL`, `SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY` are present.
- Improved the report HTML template without adding external rendering services.

## Security And Privacy

- Synthetic data only.
- Approved `.example` targets only.
- No automatic external sharing.
- No real customer, prospect, personal data, credentials, API keys, or service-role keys were added.
- Report wording remains cautious and avoids presenting observations as confirmed vulnerabilities.

## Blockers And Risks

- Medium: Supabase-backed report integration tests require local Supabase runtime variables and were not run in this local fallback pass.
- Medium: Runtime persistence is still split between in-memory fallback and Supabase-backed repositories.
- Low: PDF generation is intentionally simple and dependency-light; future production use should replace it with a stronger HTML-to-PDF renderer after MVP flow is stable.

## Supervisor Decisions Requested

1. Confirm whether the Week 3 demo should use the local in-memory fallback or local Supabase-backed flow.
2. Confirm whether internal sharing status is enough for MVP, since external report sending is out of scope.
3. Confirm whether Week 4 should prioritize Supabase runtime persistence cleanup before CSV import/export polish.

## Next Outcomes

- Week 4 permission tests and API regression hardening.
- Empty/error/loading responsive fixes and accessibility pass.
- CSV import/export and 30-company synthetic dataset.
- Clean-install handover verification.
