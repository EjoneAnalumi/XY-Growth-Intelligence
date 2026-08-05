# Week 1 Day 5 Status Report

Date: 05-08-2026

Scope: Week 1 gate only. Day 6 and later opportunity/pipeline work is intentionally excluded from this report.

## Completed Outcomes

- Repository foundation - PR/evidence: initial foundation commit `5422e79`.
- Supabase schema v1 for profiles, companies, contacts, RLS, and seed data - PR #1:
  `https://github.com/EjoneAnalumi/XY-Growth-Intelligence/pull/1`
- Frontend app shell, login, navigation, protected layout - PR #2:
  `https://github.com/EjoneAnalumi/XY-Growth-Intelligence/pull/2`
- FastAPI config, auth verification, health, company/contact APIs - PR #4:
  `https://github.com/EjoneAnalumi/XY-Growth-Intelligence/pull/4`
- Company/contact frontend mock UI cleanup and merge evidence - main merge commit `a07bf98`.
- Company/contact frontend-backend integration - PR #6:
  `https://github.com/EjoneAnalumi/XY-Growth-Intelligence/pull/6`

## Working Demonstration

Start backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start frontend in a second terminal:

```powershell
cd frontend
npm.cmd run dev
```

Start at:

```text
http://localhost:3000/login
```

Test user and role:

- Role: Business Development
- Local demo token is stored by the mock login helper; no real credentials are used.

Flow demonstrated:

1. Open `/login`.
2. Sign in with the default demo values.
3. Confirm protected layout loads.
4. Open `/companies`.
5. Create a fictional company with a `.example` domain.
6. Open `/contacts`.
7. Create a fictional contact linked to that company.
8. Refresh the browser.
9. Confirm company/contact data is still visible while backend remains running.

## Test Result

Backend:

```text
python -m pytest
19 passed
```

Backend lint:

```text
python -m ruff check .
All checks passed!
```

Frontend:

```text
npm.cmd run typecheck
passed

npm.cmd run lint
passed

npm.cmd run build
passed
```

Build note:

- Next.js emitted a non-blocking webpack cache warning during build.
- Build exit code was `0`, and all Week 1 routes were generated.

## Defects Fixed During Week 1

- Company/contact API routers were created but not visible in Swagger until included in `main.py`.
- Git line-ending warnings were handled as Windows checkout behavior, not source defects.
- Frontend mock data was changed to clearly synthetic `.example` domains.
- Company/contact frontend was connected to FastAPI instead of local-only state.
- Stale `.next` cache was cleared when switching between later branches and Week 1 branch checks.
- README status was updated to match the actual Week 1 gate state.

## Decisions Made

- Keep local demo bearer tokens until Supabase Auth JWT verification is ready.
- Keep runtime company/contact persistence in memory for Week 1 vertical slice.
- Keep Supabase schema/RLS work as migration contract until local Supabase runtime integration is completed.
- Keep private learning notes out of Git and public handover docs in `docs/`.

## Blockers And Risks

- Medium: Supabase Auth is not connected to FastAPI yet.
- Medium: Runtime persistence is in memory, so records disappear after backend restart.
- Medium: RLS policies still need manual allow/deny verification in a Supabase test project.
- Low: Browser automation connector was unavailable during Codex testing, so visual proof should be captured manually.

## Supervisor Decisions Requested

1. Confirm whether Week 2 should prioritize Supabase-backed runtime persistence before additional UI workflows.
2. Confirm when Supabase Auth JWT verification should replace local demo tokens.
3. Confirm whether screenshots or a short screen recording are preferred for weekly evidence.

## Next Week Outcomes

- Opportunity, pipeline stage, activity, task, and note APIs.
- Opportunity table/detail UI against the published API contract.
- Stage movement history.
- Weighted value and dashboard summary groundwork.
