# Week 2 Day 6 Backend Pipeline API Evidence

Date: 05-08-2026

Branch: `feature/opportunity-pipeline-crud-api`

## Scope

Day 6 Intern 1 requires backend models and APIs for:

- Opportunities
- Pipeline stages
- Activities
- Tasks
- Notes
- Opportunity stage movement with history

## Implemented

- Protected all new CRM pipeline APIs with FastAPI bearer auth.
- Added role checks for write actions.
- Kept read access authenticated.
- Added in-memory repository support for local development and tests.
- Added default pipeline stages from the project brief.
- Added weighted value calculation for opportunities.
- Added stage movement endpoint that records old stage, new stage, user, timestamp, and note.
- Added endpoint to read opportunity stage history.
- Removed unsafe anonymous RLS migration for stage history.
- Removed startup dependency on Supabase environment variables for local tests.

## Security Notes

- New endpoint writes are denied for `read_only`.
- Pipeline stage configuration writes are limited to `admin` and `management`.
- No real data or secrets were added.
- Supabase migrations remain the database contract, but local API tests use in-memory storage until Supabase runtime integration is ready.

## Verification

Commands run:

```powershell
cd backend
python -m pytest
```

Result:

```text
29 passed
```

```powershell
python -m ruff check .
```

Result:

```text
All checks passed!
```

## Covered By Tests

- Pipeline stages require authentication.
- Default brief pipeline stages are returned.
- Business Development cannot create pipeline stages.
- Management can create pipeline stages.
- Opportunity create/update/archive works.
- Opportunity weighted value is calculated.
- Unknown stage IDs are rejected.
- Read-only users cannot create opportunities.
- Stage movement records stage history.
- Activity, task, and note creation/update work.
- OpenAPI documents the new endpoints.

## Remaining TODO

- Replace in-memory persistence with Supabase-backed runtime repositories.
- Add Supabase RLS allow/deny tests after migrations are applied in a Supabase test project.
- Expand seed data for Week 2 dashboard metrics.
