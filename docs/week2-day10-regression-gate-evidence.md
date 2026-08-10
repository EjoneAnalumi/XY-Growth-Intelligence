# Week 2 Day 10 Regression Gate Evidence

Date: 2026-08-10

Branch: `week2-regression-gate`

## Scope

Day 10 requires:

- Week 2 regression test.
- Permission/security review.
- Opportunity table/detail/edit verification against the API contract.
- Demo evidence.
- Backlog cleanup.
- Confirmation that no critical/high defects remain.

## Regression Result

Status: PASS

Added:

- `backend/tests/test_week2_regression_gate.py`
- `backend/tests/test_week2_rls_permissions.py`

Regression coverage:

- Strong-fit ICP calculation for a sales workflow company.
- Opportunity create with weighted value calculation.
- Stage movement with history.
- Activity and due-this-week task creation.
- Dashboard summary updates for pipeline value, weighted value, activity count, open tasks, due-this-week tasks, high-priority opportunities, and priority opportunity identity.
- Non-writer role denial for sales workflow mutations.
- Read access for read-only and technical analyst roles.
- Business Development denial for admin-only pipeline stage creation.

Root cause found:

- `high_priority_opportunities` was derived only from `priority_score >= 70`.
- A strong-fit opportunity with meaningful weighted value and a due-this-week follow-up was present in `priority_opportunities`, but was excluded from `high_priority_opportunities`.

Fix:

- Kept the existing priority score formula and existing Day 9 expected score intact.
- Updated high-priority classification so the count includes either:
  - the existing high score band, or
  - the combined product signals of meaningful weighted value, strong ICP fit, and urgent/inactive workflow risk.
- Updated `docs/api-contract.md` to make that classification explicit.

## Permission/Security Review

Status: PASS (verified)

### Backend API authorization

Verified by automated regression:

- `read_only` cannot create companies, contacts, opportunities, activities, tasks, notes, or calculate ICP.
- `read_only` cannot patch/archive opportunities, activities, tasks, or notes.
- `read_only` cannot move opportunity stages.
- `technical_analyst` has the same sales workflow mutation denials.
- Business Development cannot create pipeline stages (admin/management only).
- Both non-writer roles can read sales workflow list/detail endpoints and dashboard summary.

### Supabase RLS

Verified after `supabase db reset` against local Postgres:

- RLS is enabled on profiles, companies, contacts, pipeline_stages, opportunities, opportunity_stage_history, activities, tasks, notes, icp_rules, and icp_score_results.
- Anon cannot select protected business tables.
- Read-only can select and cannot insert sales workflow rows.
- Technical analyst cannot insert opportunities.
- Business Development can insert companies/opportunities/activities/tasks/notes and cannot insert pipeline stages.
- Admin can insert pipeline stages.
- Authenticated users can read ICP rules; writers can insert ICP score results; read-only cannot.

Automated proof:

```text
python -m pytest backend/tests/test_week2_rls_permissions.py -q -p no:cacheprovider
```

Migration path notes:

- Local Supabase applies versioned files from `supabase/migrations`.
- Matching copies are kept under `database/migrations` for the project's dual-folder convention.
- ICP migration `20260806000001_icp_scoring.sql` is present in both folders.
- Week 2 RLS hardening migration copies are identical.

## Opportunity UI Contract Review

Status: PASS

Reviewed against `docs/api-contract.md`:

- Table uses `GET /opportunities` fields for opportunity, company, stage, `value_usd`, `probability`, `weighted_value_usd`, and next action.
- Detail page uses `GET /opportunities/{opportunity_id}` and stage history, including `current_stage_entered_at` and `days_in_current_stage`.
- Edit form uses `PATCH /opportunities/{opportunity_id}` with contract field names.
- Stage movement remains on the Kanban flow through `PATCH /opportunities/{opportunity_id}/move-stage`.
- Opportunity table, detail, form, and Kanban currency formatting use USD to match `value_usd` / `weighted_value_usd`.

## Demo Evidence

Status: PASS

Demo script: `docs/week2-day10-demo-script.md`

Demo flow verified by regression test and runnable local stack:

1. Create a fictional financial services company and contact.
2. Calculate ICP and confirm `strong_fit`.
3. Create an opportunity and confirm `weighted_value_usd`.
4. Move the opportunity from Identified to Contacted and confirm stage history.
5. Record a meeting activity.
6. Create a high-priority due-this-week task.
7. Load dashboard summary and confirm pipeline, task, activity, and high-priority metrics update.
8. Confirm read-only and technical analyst roles cannot mutate sales workflow records.
9. Confirm Business Development cannot create admin-only pipeline stages.

Runtime note:

- FastAPI still uses in-memory repositories for the demo API path.
- Supabase seed data (20 opportunities / 25 activities / 15 tasks) is applied by `supabase db reset` for schema/RLS verification and seed-count compliance.
- Supervisor demo of the live UI/API path creates synthetic records through the authenticated workflow rather than reading the SQL seed through the API.

## Verification Commands

Backend:

```text
python -m pytest backend -q -p no:cacheprovider
50 passed

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
passed (applies initial, pipeline, ICP, and Week 2 RLS hardening migrations)

supabase db lint --local --schema public --fail-on error
No schema errors found

python -m pytest backend/tests/test_week2_rls_permissions.py -q -p no:cacheprovider
7 passed
```

## Backlog Cleanup

Status: DONE

Remaining backlog documented in the Week 2 status report:

- Supabase-backed runtime persistence for FastAPI repositories.
- Supabase JWT verification in FastAPI.
- Remaining brief API groups for timeline, recommendations, scans, reports, and dashboard subroutes.
- Browser screenshots or screen recording if the supervisor prefers a recorded artifact.

## Critical/High Defects

Critical/high defects found after verification: 0
