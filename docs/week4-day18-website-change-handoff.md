# Week 4 Day 18 Website Change Handoff

Date: 24-08-2026  
Branch: `feature/supabase-auth-attribution`  
Baseline: `main` at merge commit `0b605b9` (CRM workflow/persistence PR #28)

## Purpose and scope

This is the consolidated public handoff for the website changes completed after the Day 18 clean-install task. It is a Day 18 follow-up, not Day 19. It covers the merged CRM usability/persistence baseline and the current Supabase Auth, staff attribution, user administration, CSV/ICP corrections, and local startup work.

## Website behavior delivered

### Dashboard and explainability

- Dashboard metrics are calculated from CRM records rather than typed directly.
- The UI explains that opportunities affect pipeline totals, scheduled/completed tasks affect follow-ups, and activities affect deal recency.
- Opportunity, scan, and report pages include clearer descriptions of what the user is naming, scanning, or reporting.

### Companies and contacts

- Companies and contacts use durable Supabase PostgreSQL storage in the integrated runtime.
- Authorized staff can create, view, edit, and archive/delete company and contact records.
- Company CSV import supports bulk synthetic company creation with validation and duplicate protection.
- Company CSV export produces a reusable UTF-8 template/current-data download.
- RLS test artifacts that produced blank `BD Allowed ...` export rows were removed locally, and test teardown now prevents recurrence.
- ICP calculation now stores its eight-rule explanation breakdown in `icp_score_results`; the PostgreSQL table name and JSON serialization defects were corrected.

### Opportunities, activities, tasks, and notes

- Opportunity detail supports the published fields, stages, contacts, activities, tasks, notes, edit controls, and archive behavior.
- Primary contacts can be selected from persisted contacts instead of being stuck on “No primary contact.”
- Pipeline stage labels are human-readable, and stage changes record the responsible staff member and timestamp.
- Staff Notes provides shared reminders, work notes, and TODO-style context.
- Notes show their writer; activities/tasks show their creator; opportunities show creator/updater; stage history shows who moved the opportunity.

### Authentication and account recovery

- The mock role selector was replaced with invitation-only Supabase Auth.
- Login, logout, access-token refresh, session expiration, invitation acceptance, forgot-password, and reset-password flows are implemented.
- Invitation and recovery redirect URLs are passed to Supabase as query parameters so email links return to `/accept-invite` and `/reset-password`.
- Passwords are selected by staff through invitation/reset flows and are handled only by Supabase Auth.
- The temporary-password option was removed.
- Local Mailpit is development-only; production delivery requires company SMTP and approved HTTPS redirect URLs.

### Admin Users page

- Only Admin sees and can use staff account administration.
- Admin can invite a user, edit full name/email/role, activate/deactivate, and permanently delete an account.
- The list uses compact one-line summary rows. Editing expands only the selected row.
- Edit, Deactivate/Reactivate, and Delete controls remain easy to reach.
- Delete requires confirmation.
- FastAPI rejects Admin self-deactivation, self-demotion, and self-deletion.
- User update/delete events are recorded in `audit_logs`; deletion support was added to the audit constraint.

## Backend and database implementation

- FastAPI verifies bearer sessions through Supabase Auth and loads the active database profile before authorizing the request.
- Backend role checks are authoritative; hiding a frontend control is not treated as authorization.
- A database trigger creates an active Read Only profile for newly invited Auth users before Admin role assignment.
- `audit_logs` records actor, entity type/id, action, and UTC timestamp for important CRM/account writes.
- GoTrue seed-compatibility migrations normalize legacy nullable Auth string fields for the pinned local Auth image.
- Docker Compose injects Supabase Auth settings server-side and uses `host.docker.internal` for host-published Supabase services.
- No service-role value is exposed through `NEXT_PUBLIC_*` variables.

## Local development and port recovery

- Canonical frontend: `http://localhost:3000`.
- Canonical FastAPI backend: `http://localhost:8000`.
- Canonical local Supabase API: port `54321`; Studio: `54323`; Mailpit: `54324`.
- The root README contains the single supported PowerShell startup sequence from the `supabase-auth` worktree.
- Duplicate frontend/backend processes on ports 3000–3002 and 8000–8001 are inspected separately from Supabase ports.
- A Windows orphaned listener whose PID no longer exists requires a Windows restart; repeatedly starting more servers creates old-UI/auth conflicts.

## Verification evidence

- Backend: `python -m pytest backend` → 100 passed, 5 environment-gated skipped.
- Backend lint: `python -m ruff check backend` → passed.
- Frontend typecheck: `npm.cmd run typecheck` → passed.
- Frontend lint: `npm.cmd run lint` → passed with no warnings/errors.
- Frontend build: `npm.cmd run build` → passed, 16 routes generated.
- Frontend tests: `npm.cmd test -- --run` → 6 files passed, 16 tests passed.
- Real local Supabase checks passed for login/profile lookup, invitation redirect, recovery redirect, user create/edit/delete, ICP persistence, and port-3000 CORS.
- Temporary synthetic verification users were deleted after each destructive flow test.

## Security and data notes

- Synthetic `.test` identities and fictional CRM records only.
- No real employee/customer/prospect data, hosted credentials, generated local keys, or service-role values are tracked.
- No public signup endpoint exists; Admin invitation is the onboarding boundary.
- Local Mailpit is not a production shared inbox.
- Secrets must be supplied through the hosted deployment secret manager and Supabase configuration.

## Remaining production work

- Provision the hosted Supabase project and deployment secrets.
- Configure company SMTP, verified sender/domain records, and approved HTTPS invitation/recovery redirects.
- Omit or rotate local demo users/passwords outside local development.
- Review the recorded npm dependency audit findings in a separate dependency-hardening task.
- Complete browser screenshot/accessibility evidence for final internship submission.

## Status

The requested local MVP website changes described above are implemented and documented. Production deployment, real email delivery, and production secret/domain configuration remain environment work and are not committed to this repository.
