# Week 2 Status Report

Date: 2026-08-10

Branch: `week2-regression-gate`

## Completed Outcomes

- Opportunity pipeline CRUD API and stage history.
- Opportunity table/detail/edit frontend flow.
- Kanban stage movement, activity capture, and task capture.
- Dashboard summary with pipeline value, weighted value, task metrics, priority opportunities, and inactive opportunity metrics.
- Deterministic ICP scoring and company `fit_score` integration.
- Week 2 Day 10 regression gate, API permission review, and local Supabase RLS allow/deny verification.

## Working Demonstration

Demo script: `docs/week2-day10-demo-script.md`

Start backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start frontend:

```powershell
cd frontend
npm.cmd run dev
```

Start at:

```text
http://localhost:3000/login
```

Test role:

- Business Development for create/edit/demo flow.
- Read Only or Technical Analyst for permission denial checks.

Flow demonstrated:

1. Sign in locally.
2. Create or select a fictional company.
3. Calculate ICP score.
4. Create an opportunity.
5. Open the opportunity detail page and edit fields.
6. Move the opportunity stage from the opportunity workflow / Kanban.
7. Add an activity and follow-up task.
8. Open the dashboard and confirm updated pipeline, task, and priority metrics.

## Test Result

Backend:

```text
python -m pytest backend -q -p no:cacheprovider
50 passed
```

Backend lint:

```text
python -m ruff check backend
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

Database:

```text
supabase db reset
passed

supabase db lint --local --schema public --fail-on error
No schema errors found

python -m pytest backend/tests/test_week2_rls_permissions.py -q -p no:cacheprovider
7 passed
```

## Decisions Made

- Kept the established priority score formula and existing Day 9 score expectation.
- Clarified high-priority dashboard counting as either the high score band or the combined signals of meaningful weighted value, strong ICP fit, and urgent/inactive workflow risk.
- Corrected opportunity frontend currency display to USD, including Kanban, because the API contract uses `value_usd` and `weighted_value_usd`.
- Aligned Week 2 seed counts to the brief shared requirement: 20 opportunities, 25 activities, 15 tasks.
- Kept matching migration copies under `supabase/migrations` and `database/migrations`, including the ICP migration required after clean reset.

## Permission/Security Status

- PASS: Sales workflow mutation endpoints are denied to Read Only and Technical Analyst roles.
- PASS: Business Development cannot create admin-only pipeline stages.
- PASS: Dashboard requires authenticated bearer auth.
- PASS: Local Supabase RLS allow/deny probes cover anon deny, read-only/analyst deny, BD allow, and admin stage allow paths.
- PASS: No real customer/prospect data, credentials, or API keys were added.
- Remaining auth backlog: replace local demo bearer tokens with Supabase JWT verification when runtime persistence moves to Supabase.

## Backlog

Documented remaining backlog:

- Replace local in-memory runtime repositories with Supabase-backed persistence. Effort: large.
- Replace local demo bearer token auth with Supabase JWT verification. Effort: medium.
- Implement remaining brief API groups:
  - company timeline (medium)
  - company recommendations (medium)
  - security scans and findings (large)
  - report generation, approval, and download (large)
  - dashboard pipeline, forecast, and follow-ups (medium)
- Add browser-based visual screenshots or screen recording for supervisor demo preference. Effort: small.

## Defect Status

Critical/high defects: 0

Medium follow-up risks:

- Runtime API data is still in memory and therefore independent from SQL seed rows until persistence is wired.
- Supabase Auth JWT verification is not configured in FastAPI.

## Supervisor Decisions Requested

1. Confirm whether Week 3 should prioritize Supabase-backed runtime persistence before new brief API groups.
2. Confirm whether Supabase Auth JWT verification should be completed before report/scanning workflows.
3. Confirm preferred demo artifact format: screenshots or short screen recording.

## Next Week Outcomes

- Supabase-backed runtime persistence or next supervisor-prioritized brief API group.
- Supabase JWT verification plan/implementation if approved.
- Week 3 Risk Snapshot foundation after the Week 2 gate demo.
