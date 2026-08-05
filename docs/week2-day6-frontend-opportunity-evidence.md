# Week 2 Day 6 Frontend Opportunity Evidence

Date: 05-08-2026

Branch: `feature/opportunity-table-detail-view`

## Scope

Day 6 Intern 2 requires:

- Opportunity table against the published API contract.
- Opportunity detail view against the published API contract.
- Opportunity fields display and edit correctly.

## Implemented

- Added `Opportunities` navigation.
- Added `/opportunities` protected route.
- Added opportunity create form.
- Added opportunity table with company, stage, value, probability, weighted value, and next action.
- Added `/opportunities/[id]` protected detail route.
- Added opportunity detail field display.
- Added edit form for opportunity fields.
- Added stage history display on the detail page.
- Added frontend API mapping between backend snake_case and UI camelCase.
- Added loading, empty, validation, permission/server error states through the existing API client pattern.

## API Contract Used

Frontend uses the contract documented in `docs/api-contract.md`:

- `GET /pipeline-stages`
- `GET /opportunities`
- `POST /opportunities`
- `GET /opportunities/{opportunity_id}`
- `PATCH /opportunities/{opportunity_id}`
- `GET /opportunities/{opportunity_id}/stage-history`

## Verification

Commands run:

```powershell
cd frontend
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
```

Result:

```text
TypeScript passed
ESLint passed
Next.js production build passed
```

## Notes

- Browser click-through should be done with both backend and frontend dev servers running.
- Opportunity data is still backed by the current FastAPI in-memory repository until Supabase runtime persistence is connected.
