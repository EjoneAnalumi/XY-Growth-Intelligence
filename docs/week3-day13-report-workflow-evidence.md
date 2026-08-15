# Week 3 Day 13 Report Workflow Evidence

Date: 13-08-2026

Branch: `feature/report-generation-workflow`

## Scope

Day 13 Intern 1 and Intern 2 tasks:

- Implement report assembly, PDF creation, Supabase Storage, and status permissions.
- Build review, approve, archive, and download interface.

## Implemented

- Added backend report API endpoints:
  - `GET /reports`
  - `POST /reports/generate`
  - `POST /reports/{report_id}/review`
  - `POST /reports/{report_id}/approve`
  - `POST /reports/{report_id}/share`
  - `POST /reports/{report_id}/archive`
  - `GET /reports/{report_id}/download`
- Added deterministic report HTML assembly from synthetic report context.
- Added valid PDF byte generation without external services.
- Added Supabase PostgreSQL report persistence and private Supabase Storage upload using
  server-only service credentials.
- Added linked `report_files` metadata: report id, bucket, real object path, content type, size,
  creator, and timestamp.
- Added Supabase migration contract for:
  - `public.reports`
  - report indexes
  - report and report-file RLS policies
  - private `reports` storage bucket
  - storage object policies
- Added database trigger enforcement for Draft -> Review -> Approved -> Shared -> Archived and
  backend permission rules:
  - Technical Analyst, Management, and Admin can generate and submit reports for review.
  - Only Management and Admin can approve, share, archive, and download approved PDFs.
  - Business Development cannot approve or download report PDFs.
- Added frontend report workflow:
  - report list
  - generate PDF
  - submit for review
  - approve
  - internal share tracking
  - archive
  - download approved PDF and archive confirmation
  - loading, empty, error, and permission states
- Added Management demo role in local login so the approval/download path can be tested.

## Security Notes

- All data remains synthetic.
- No real customer, prospect, personal data, credentials, API keys, or Supabase service role keys were added.
- Report content uses cautious wording and does not describe unverified observations as confirmed vulnerabilities.
- Download is backend-protected and only works for approved reports and authorized roles.
- Supabase service credentials are used only by the backend. The frontend receives neither service
  credentials nor direct Storage write access.

## Verification

Commands run:

```powershell
supabase db reset
$env:DATABASE_URL = (supabase status -o json | ConvertFrom-Json).DB_URL
# Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from the same local status output.
python -m pytest backend/tests/test_reports.py -q -p no:cacheprovider
cd backend
python -m pytest -q -p no:cacheprovider
python -m ruff check .
cd ..\frontend
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
```

Results:

- Local Supabase reset applied the report persistence migration and created the private bucket.
- Report integration tests verified persisted `reports` and linked `report_files` rows, private
  Storage object retrieval, valid PDF parsing, status transition enforcement, API role denials,
  and direct database status-update denial.

## Remaining TODO

- Integrate report generation directly from persisted snapshot records in Day 14.
