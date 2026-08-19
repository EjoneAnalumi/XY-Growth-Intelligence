# Week 4 Day 16 Backend Hardening Evidence

Date: 19-08-2026
Branch: `feature/day16-backend-hardening`
Owner: Intern 1 - Backend and Data

## Scope

Add permission and API regression coverage, structured backend request logging, consistent API
errors, and a review of tracked database migrations. This task does not add optional product
features or modify Intern 2 frontend work.

## Implemented

- Added a common FastAPI error handler with stable `detail` and machine-readable `error.code`
  fields. Validation failures preserve field details in `error.details`; unhandled failures return
  a safe generic message.
- Added JSON request-completion logs with event name, HTTP method, path, status code, and duration.
  Request bodies, authorisation tokens, and credentials are not logged.
- Added API regression tests for authentication, permission denial, not-found, validation,
  structured logs, and error-envelope formatting.
- Updated existing backend tests to assert the published error contract.
- Reviewed migration mirrors. Both migration directories now have identical SQL, and a regression
  test verifies that report and snapshot tables enable RLS.
- Bounded the local Supabase RLS test connection attempt to five seconds so absent local services
  result in a documented skip rather than an indefinitely hanging quality gate.

## Security notes

- The tests use local synthetic demo identities only.
- Error responses do not expose exception details for unexpected server failures.
- Request logs contain operational metadata only and exclude request payloads and bearer tokens.
- RLS probe tests remain in place; they require a running local Supabase database to execute.

## Verification

Run from `backend/`:

```text
python -m pytest
76 passed, 10 skipped in 8.08s

python -m ruff check .
All checks passed!
```

The 10 skipped tests are Supabase-backed report persistence and RLS probes because no local
Supabase database or persistence environment was configured for this run. The non-database
critical-path API, permissions, scanning, report-workflow fallback, and regression tests passed.

## Remaining TODOs

- Start local Supabase and rerun the skipped RLS and persistence tests before final acceptance.
- Perform the remaining Week 4 clean-install, synthetic-data, CSV import/export, and handover
  tasks on their assigned days.
