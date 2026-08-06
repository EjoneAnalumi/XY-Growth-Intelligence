# Week 2 Day 7 Kanban Activity Task Evidence

Date: 07-08-2026

Branch: `feature/kanban-icp-components`

## Scope

Intern 2 Day 7 requires:

- Build Kanban stage movement.
- Build activity and task interfaces.
- Stage movement and new task work from UI.

## Implemented

- Added a Kanban pipeline view on `/opportunities`.
- Added explicit stage movement from Kanban using `PATCH /opportunities/{opportunity_id}/move-stage`.
- Added movement notes and frontend error handling for same-stage or failed moves.
- Kept the existing opportunity table and added a Kanban/Table view switch.
- Added opportunity detail activity and task forms using the published `/activities` and `/tasks` contracts.
- Added recent activity and task lists filtered to the current opportunity.

## API Contract Used

- `GET /opportunities`
- `PATCH /opportunities/{opportunity_id}/move-stage`
- `GET /opportunities/{opportunity_id}/stage-history`
- `GET /activities`
- `POST /activities`
- `GET /tasks`
- `POST /tasks`

## Security Notes

- No secrets, credentials, customer data, prospect data, or API keys were added.
- Frontend uses the existing authenticated API client and bearer-token flow.
- Stage movement, activity creation, and task creation still depend on backend role enforcement.

## Verification

Commands run:

```powershell
cd frontend
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build

cd ..\backend
python -m pytest
python -m ruff check .
```

Result:

```text
TypeScript passed.
ESLint passed with no warnings or errors.
Next.js production build passed.
Backend pytest: 38 passed, 1 pytest cache warning because the sandbox could not write `.pytest_cache`.
Backend Ruff: all checks passed.
```

Build note:

```text
The first sandboxed `npm.cmd run build` attempt failed with `spawn EPERM`.
The approved rerun outside the sandbox completed successfully.
```

## Remaining TODO

- Browser click-through should be verified with both backend and frontend dev servers running.
- Replace in-memory API backing stores with Supabase runtime persistence when Intern 1 completes that integration.
