# Week 4 Day 18 Clean-Install Evidence

Date: 24-08-2026  
Branch: `feature/day18-clean-install`  
Owner: Both interns (shared task)

## Exact task scope

Run a clean installation using the README, identify and document every required setup step, and demonstrate that a new environment can start without undocumented team knowledge. This task does not implement the separate durable-persistence or Supabase Auth backlog.

## Clean environment method

The test used a new Git worktree created from the fetched `origin/main` commit `031f191`. Ignored dependencies and environment files were recreated in that worktree. Existing uncommitted Day 17 changes in the original worktree were not stashed, changed, or discarded.

## Implemented changes

- Replaced the stale Week 1 placeholder setup with an ordered Windows PowerShell clean-install guide.
- Documented prerequisite/version checks, `.env` creation, pinned Supabase CLI use, migrations, seed reset, backend/frontend installation, service URLs, and shutdown.
- Documented that Docker Compose starts only FastAPI and that the frontend and Supabase stack are started separately.
- Corrected backend-container Supabase addresses to use `host.docker.internal` while host commands use `127.0.0.1`.
- Increased the local database cold-start health timeout from two to five minutes.
- Added troubleshooting for Docker Desktop startup, PowerShell command shims, missing `.env`, port conflicts, corrupt Supabase images, and Windows Auth/Mailpit health metadata.
- Updated backend and frontend setup notes to match current implementation and limitations.
- Documented current in-memory core CRM persistence and mock authentication honestly.

## Verification evidence

### Backend clean install without Supabase variables

Commands:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check backend
```

Result:

- Python 3.12.6
- 96 tests collected
- 86 passed, 10 environment-dependent tests skipped
- Ruff passed

Final rerun after the local database was available: 93 passed, 3 report-storage cases skipped, with one non-functional pytest cache-permission warning. Ruff passed again.

### Frontend clean install

Commands:

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
```

Result:

- Dependency installation passed
- TypeScript typecheck passed
- ESLint passed with no warnings or errors
- Next.js production build passed and generated all expected routes
- npm audit reported 15 dependency findings: 3 moderate, 11 high, and 1 critical

The audit findings require a scoped dependency review. `npm audit fix --force` was not used because it can introduce breaking, unrelated changes.

### Docker Compose

Commands:

```powershell
Copy-Item .env.example .env
docker compose up --build --detach
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/health
```

Result:

- Backend image built from a clean Docker cache
- Backend container started on port 8000
- Health response was `{"status":"ok"}`
- Supabase Auth health endpoint returned HTTP 200
- Mailpit returned HTTP 200 despite Docker retaining unhealthy health metadata for those containers
- The initial attempt correctly exposed the previously undocumented requirement to create `.env` and start Docker Desktop first

### Supabase migrations and seed reset

Commands:

```powershell
npx.cmd --yes supabase@2.115.0 start
npx.cmd --yes supabase@2.115.0 start --ignore-health-check
npx.cmd --yes supabase@2.115.0 status
npx.cmd --yes supabase@2.115.0 db reset
```

Result:

- All nine tracked migrations applied successfully
- `database/seed/seed.sql` completed successfully
- Verified counts: 30 companies, 50 contacts, 20 opportunities, 25 activities, and 15 tasks
- Companies, contacts, and opportunities meet the brief minimums
- Activities and tasks do not meet the final brief minimums of 40 and 25

On the test Windows/Docker environment, Auth and Mailpit processes started but Docker retained unhealthy health metadata. The standard start therefore timed out. The CLI-supported `--ignore-health-check` option left the local stack available for status/reset verification. This workaround is local-only and does not waive hosted acceptance checks.

The first image pull also exposed cached wrong-architecture/corrupt Mailpit and PostgREST images. Only the two image names reported by the CLI were removed and downloaded again; no volumes or project data were broadly deleted.

### Supabase-enabled backend verification

Local generated credentials were loaded into process memory and were not written to tracked files.

Result from the full suite with `DATABASE_URL` enabled:

- 92 passed
- 4 CSV tests failed because they assume an empty companies table while the clean reset correctly starts with 30 seeded companies
- Ruff passed

Targeted integration command:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_reports.py backend\tests\test_week2_rls_permissions.py
```

Result: 15 passed in 5.89 seconds. The report-storage and RLS integration groups therefore pass when run against the clean local Supabase database without the unrelated CSV test-state collision.

## Security notes

- Only fictional synthetic data was used.
- No hosted project, production environment, real prospect/customer record, API key, password, or service-role key was committed.
- Generated local Supabase values remained ignored or process-local and are intentionally omitted from this document.
- The README explicitly prohibits placing a service-role key in a `NEXT_PUBLIC_*` variable.
- Database reset was limited to the disposable local Supabase database.

## Remaining TODOs and risks

- High: expand synthetic seed data from 25 to at least 40 activities and from 15 to at least 25 tasks.
- High: replace in-memory core CRM/pipeline repositories with authorized Supabase PostgreSQL persistence so records survive restart/logout and are correctly isolated for different users.
- High: replace the local mock session with Supabase Auth and verify role-aware login, logout, reset, and backend JWT authorization.
- Medium: isolate PostgreSQL-backed CSV tests from the normal seeded dataset so the entire test suite can run with `DATABASE_URL` enabled.
- Medium: investigate the 15 npm dependency audit findings through a separate, reviewed dependency-hardening task.
- Medium: resolve or upstream the Windows Docker Auth/Mailpit health-check incompatibility rather than relying permanently on `--ignore-health-check`.

## Completion status

Day 18 documentation and clean-start work is complete when the final commands below pass and the branch is pushed. Final MVP acceptance remains incomplete because the persistence/auth work and two synthetic-data minimums are outstanding.
