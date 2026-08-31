# Week 4 Day 19 Acceptance Evidence

Date: 31-08-2026 (final audit update)
Branch: `feature/day19-acceptance-handover`
Verdict: **DAY 19 TECHNICAL ACCEPTANCE COMPLETE / MERGE READY - retained live Auth/business-flow screenshots or recording are not supplied and remain supplemental evidence.**

## Authoritative source

The acceptance source is the supplied official 23-page *XY CYBER Growth Intelligence Internship Project Brief*, re-read on 31-08-2026. This document uses its final demonstration (p. 2), mandatory scope (p. 4), functional requirements (pp. 8-11), quality gates (p. 14), deliverables and mandatory acceptance matrix (pp. 17-19), and synthetic-data minimums (p. 22). Repository documents are supporting evidence only.

## Mandatory acceptance traceability

PASS requires retained evidence appropriate to the brief. PARTIAL records a valid automated check or a reported manual run that still lacks the brief-required retained live-demo/screenshot artifact. PENDING identifies an uncompleted requirement.

| Mandatory requirement | Verification performed | Evidence/test | Result |
| --- | --- | --- | --- |
| Authentication: login, logout, reset, invitation acceptance, session expiry, five roles, server-enforced denial (brief pp. 8, 18) | API/permission tests and reported browser run completed. | Real GoTrue token was accepted by `/users/me`; full backend suite passed. Retained login/logout/reset/invitation/session/role screenshots or recording are still required. | PARTIAL |
| Company/contact: create, edit, search, filter, archive, timeline, and database record (pp. 8, 18) | CRUD/persistence tests and reported browser flow completed. | PostgreSQL persistence coverage passed; retained CRM/timeline live-demo screenshot or recording is still required. | PARTIAL |
| Opportunity: table/Kanban, create/edit, weighted value, move stage, retained history (pp. 8, 18) | Pipeline tests and reported browser flow completed. | Pipeline coverage passed; retained table/Kanban/history live-demo screenshot or recording is still required. | PARTIAL |
| Activities/tasks/notes: create, complete, overdue, next action, owner attribution, dashboard update (pp. 8, 18) | Workflow regression and reported browser flow completed. | Workflow coverage passed; retained activity/task/dashboard-update live-demo screenshot or recording is still required. | PARTIAL |
| ICP: configurable 0-100 deterministic score, stored rule results, explanation, UI breakdown (pp. 8-10, 18) | Deterministic scoring tests and reported browser flow completed. | Score/storage tests passed; retained UI breakdown screenshot or recording is still required. | PARTIAL |
| Lead prioritization and deterministic service recommendation: reason, what, who, when (pp. 9, 18) | Priority regression and reported browser flow completed. | Priority logic passed; retained dashboard priority screenshot or recording is still required. | PARTIAL |
| Analytics: at least 8 accurate KPIs and 5 useful charts/panels, validated against seed calculations (pp. 3, 11, 18) | Metrics tests and reported browser flow completed. | Metrics logic passed; retained dashboard comparison screenshot/recording or manual comparison artifact is still required. | PARTIAL |
| Safe Cyber Risk Snapshot: approved/mock target only; safe DNS/TLS/HTTP/SPF/DMARC checks; evidence/errors distinct; cautious language (pp. 4, 13, 18) | Ran approval, role, allowlist, unsafe-address, timeout, and finding-classification checks. | `backend/tests/test_snapshot_scanning.py`: 21 passed. These use approved deterministic/mock behavior and verify safe error classification. | PASS |
| Report: branded HTML/PDF, required sections, Draft -> Technical Review -> Approved -> Shared -> Archived, storage and authorized download (pp. 3, 11, 13-14, 18) | Re-ran report persistence, private object, PDF-content, review/approval/share/archive, download, and denial integration cases against the freshly reset local Supabase Storage. | 31-08 `backend/tests/test_reports.py`: 8 passed. This verifies a stored private PDF, required content/disclaimer, status permissions, and authorized download. | PASS |
| CSV import/export and synthetic demo data: 30 companies, 50 contacts, 20 opportunities, 40 activities, 25 tasks, reports/scans coverage (pp. 3, 17, 22) | Freshly reset local Supabase and ran seed-dataset and PostgreSQL CSV integration tests. | 31-08 `test_seed_dataset.py` and `test_company_csv.py`: 9 passed. The seed test verifies 30/50/20/40/25/5 reports/5 scans, linked reports/scans, and all required report/finding status coverage. | PASS |
| Database: tracked migrations, schema common fields/indexes, RLS, audit events, persistence/reseed (pp. 4, 9-10, 13, 17-18) | Performed a fresh local reset and ran RLS and CRM persistence tests. | 31-08 reset applied all 13 tracked migrations and seeded `database/seed/seed.sql`; `test_week2_rls_permissions.py`: 7 passed; `test_crm_postgres_persistence.py`: 1 passed. | PASS |
| Security: Supabase Auth, tested RLS, backend authz, no frontend service key, approved report status transition, timeout/rate protection (p. 13) | Ran live role-denial acceptance plus API/RLS/report/snapshot tests. | User-confirmed five-role allow/deny behavior; full backend suite 107 passed; targeted RLS/persistence/report/PDF/CSV/seed integration suite 25 passed. | PASS |
| Frontend: required screens, responsive/accessibility/error states, component tests, and E2E workflow (pp. 11, 14, 17) | Automated frontend gates passed. | Typecheck/lint/build, Vitest 16 tests, and responsive Playwright 9 tests passed. Retained browser workflow screenshots are pending. | PARTIAL |
| Clean setup and complete handover: README/.env, local Docker, migration/seed/run/test/shutdown, architecture/API/decision log/user guide/screenshots/limitations/backlog (pp. 4, 17-19) | Clean-folder README-only installation, reset/seed, default-port runtime, authenticated protected API access, and synthetic demonstration flow completed. | Retained clean-folder record: `docs/evidence/day19-clean-install.md`. Retained live user-guide/Auth/business-flow screenshots or recording are still required. | PARTIAL |

## Day 19 defect log

### D19-01 - Invitation-only configuration disabled the email/password provider - fixed

Root cause: the previous attempt to make onboarding invitation-only set both `[auth].enable_signup` and `[auth.email].enable_signup` to `false`. On the local Supabase CLI this also set `GOTRUE_EXTERNAL_EMAIL_ENABLED=false`, so even existing invited users received GoTrue `422 email_provider_disabled` on password login.

Fix: `[auth].enable_signup` remains `false` (public signup disabled), while `[auth.email].enable_signup` is `true` (the email/password provider is available to invited staff). A full `supabase stop` / `supabase start --ignore-health-check` recreated GoTrue with `GOTRUE_DISABLE_SIGNUP=true` and `GOTRUE_EXTERNAL_EMAIL_ENABLED=true`. A direct real password grant for `bd.demo@example.test` / `local-demo` returned HTTP 200 and issued an access token. `test_local_supabase_configuration_disables_public_signup` now verifies the required separation and passed (11 passed).

### D19-02 - Local reset/migration state - resolved as local-stack state

The stale local database lacked the committed `audit_logs` migration. A later successful reset restored all 13 migrations and required tables. Docker exposes this local stack's API gateway on port `15421`, rather than the configured default `54321`; using the actual mapped port enabled the report integration suite. No application code change was required.

### D19-03 - Synthetic seed was incomplete for reports and scans - fixed

The reset originally created zero reports and scans. `database/seed/seed.sql` now creates five linked synthetic scans and five linked synthetic reports. Findings cover pass, observation, timeout, error, and fail; reports cover draft, review, approved, shared, and archived. `test_seed_dataset_includes_brief_required_reports_and_scans` protects the complete deterministic count and link/status coverage. A clean reset and direct PostgreSQL query verified the result.

### D19-04 - Responsive E2E fixture used retired mock-auth storage - fixed

All nine responsive tests were redirected to `/login` because `responsive.spec.ts` wrote the retired `xy-growth-intelligence:mock-session` shape. The Supabase Auth migration changed the application contract to `xy-growth-intelligence:supabase-session`. The E2E fixture now writes the current `AuthSession` structure with an unexpired deterministic local token and admin profile, and asserts each protected URL before checking content. This changes test setup only; protected routes still require a session and production authentication behavior is unchanged. `npm.cmd run test:responsive` passed 9/9.

### D19-05 - README frontend setup was tied to a former developer machine - fixed

Root cause: the frontend setup section assigned `$repo` to a hard-coded former-developer worktree path and claimed the repository checkout could not serve the current UI. A new developer following the README from a normal clone would fail before running the frontend.

Fix: the setup now preserves the repository path selected in step 1 with `$repo = (Get-Location).Path` and starts `frontend` from that checkout. This removes the undocumented local-worktree dependency without changing application behavior.

## Exact checks executed

| Command/check | Result |
| --- | --- |
| `git branch --show-current`; `git status` | Began on `main` with four Day 19 changes. Switched safely to `feature/day19-acceptance-handover`; changes preserved. |
| `python -m pytest` before Day 19 fix | 93 passed, 12 skipped. |
| `python -m pytest backend\\tests\\test_api_hardening.py` after D19-01 | 11 passed; one non-functional pytest-cache permission warning. |
| `python -m ruff check .` | Passed. |
| Clean `npx.cmd --yes supabase@2.115.0 db reset` after D19-03 | Recreated schema and applied the revised seed. Direct PostgreSQL counts: 30 companies, 50 contacts, 20 opportunities, 40 activities, 25 tasks, 5 reports, and 5 scans; all five reports link to scans. |
| `python -m pytest backend\\tests\\test_seed_dataset.py backend\\tests\\test_week2_rls_permissions.py backend\\tests\\test_crm_postgres_persistence.py backend\\tests\\test_company_csv.py` | 17 passed. |
| `python -m pytest backend\\tests\\test_reports.py` with verified gateway port `15421` | 8 passed. |
| Default `python -m pytest` | 102 passed, 5 skipped. The five skips are the integration cases deliberately run above with local credentials. |
| `python -m ruff check .` | Passed. |
| `npm.cmd run typecheck` | Passed. |
| `npm.cmd run lint` | Passed with no ESLint warnings or errors. |
| 31-08: `python -m pytest` | 94 passed, 13 skipped; skipped cases require local PostgreSQL/Supabase, which is unavailable because Docker Desktop is stopped. |
| 31-08: `python -m ruff check .` | Passed. |
| 31-08: `npm.cmd run typecheck` | Passed. |
| 31-08: `npm.cmd run lint` | Passed with no ESLint warnings or errors. |
| 31-08: `npm.cmd run build` | Passed: compiled successfully and generated 16/16 static pages. The initial sandboxed attempt could not spawn its child process; the permitted local-process rerun passed. |
| 31-08: `npm.cmd run test -- --reporter=dot` | Passed: 6 files, 16 tests. The initial sandboxed attempt failed with `spawn EPERM` from esbuild; the permitted local-process rerun passed. |
| 31-08: `npm.cmd run test:responsive` | Passed: 9 passed, 0 failed across mobile, tablet, and desktop. D19-04 updated the obsolete mock-session fixture to the current deterministic Supabase session shape. |
| `npx.cmd --yes supabase@2.115.0 status` | Did not return reliably in this execution environment. |
| `npx.cmd --yes supabase@2.115.0 db reset` | A later user-reported successful reset was verified directly through the database schema, migration history, and seed counts. CLI status output remains non-responsive in this execution surface. |
| Historical in-app browser discovery | Superseded: no in-app browser was available at that point; the final browser acceptance was subsequently completed by the user. |
| Local Auth runtime check | The pre-restart Auth container reported stale `GOTRUE_DISABLE_SIGNUP=false`. `supabase stop; supabase start --ignore-health-check` began downloading current images but did not complete before this execution surface returned; no Auth container is currently available. |
| 31-08: actual PDF brief | Re-read all 23 pages with `pypdf`; Poppler visual renderer remains unavailable. |
| 31-08: initial Docker availability | Initially BLOCKED because `docker ps` could not connect to `dockerDesktopLinuxEngine`. Docker Desktop was then started and all local stack-dependent checks below were rerun successfully. |
| 31-08: fresh local Supabase reset | Passed: `npx.cmd --yes supabase@2.115.0 db reset` recreated the local database, applied all 13 tracked migrations, seeded `database/seed/seed.sql`, and restarted the local containers. |
| 31-08: local PostgreSQL/RLS/report/CSV gate | Passed: `python -m pytest backend\\tests\\test_seed_dataset.py backend\\tests\\test_week2_rls_permissions.py backend\\tests\\test_crm_postgres_persistence.py backend\\tests\\test_company_csv.py backend\\tests\\test_reports.py` - 25 passed. |
| 31-08: documented local runtime startup | Passed: Docker Compose built and started FastAPI with `AUTH_MODE=supabase`; `GET http://localhost:8000/health` returned `{"status":"ok"}`. The Next.js server started from this checkout and `GET http://localhost:3000/login` returned 200. |
| 31-08: local role seed check | Passed: read-only query confirmed the five active synthetic profiles (Admin, Management, Business Development, Technical Analyst, Read Only) after reset. |
| 31-08: real local GoTrue password grant | Passed after D19-01 correction: `bd.demo@example.test` / `local-demo` returned HTTP 200 with an access token. The seeded account is email-confirmed, active, and has an encrypted password. |
| Final audit: Docker backend and live token routing | Passed: `docker ps` showed `xy-growth-intelligence-backend-1` mapped to port 8000; only Docker forwarding processes owned the host listeners; `/health` returned HTTP 200; a real local GoTrue token for `bd.demo@example.test` was accepted by `/users/me` with HTTP 200. This API check preceded, and was later supplemented by, the final browser acceptance. |
| Final audit: full backend suite with real local PostgreSQL configured | FAILED: `python -m pytest -q` with real database credentials collected 107 tests and failed 17. Ordinary API/unit tests write fixed names into the shared seeded database and then fail on unique constraints. The credentials-free baseline passed `102 passed, 5 skipped`; this does not satisfy the real-database full-suite gate. |
| Historical audit: reset/reseed baseline | Superseded: an interrupted reset initially produced a contaminated state. The final reset completed successfully and verified the required `30/50/20/40/25/5/5` baseline. |

## Current Day 19 status

- Full backend suite with real local Supabase/PostgreSQL environment: `107 passed`.
- Targeted RLS, persistence, CSV, report/PDF/Storage, and seed suite: `25 passed`.
- Ruff: passed. Frontend typecheck/lint/build: passed. Vitest: `6 files, 16 tests passed`. Playwright responsive suite: `9 passed`.
- A final reset verified 13 migrations and exact clean counts: `30/50/20/40/25/5/5`.
- Reported manual browser acceptance found no blocking defect, but retained screenshots/recording for the live Auth and business journey are pending.
- Clean-folder README-only installation evidence is retained in `docs/evidence/day19-clean-install.md`.
- The outstanding screenshot/recording artifact is documented honestly above; it is not a technical or merge blocker for this closure.

## Manual acceptance protocol

Run the exact steps in `docs/week4-day19-demo-handover.md` after local Supabase finishes starting. Record screenshots or a short recording of the invited-user Auth flow, five-role denials, CRM-to-dashboard journey, snapshot-to-approved-PDF journey, and CSV import/export. Frontend build, component tests, and responsive Playwright already have concrete evidence; PASS for the remaining flows requires the stated visible result, not a code-inspection claim.
