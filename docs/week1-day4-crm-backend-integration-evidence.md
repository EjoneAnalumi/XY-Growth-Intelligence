# Week 1 Day 4 CRM Backend Integration Evidence

Date: 31-07-2026

Branch: `feature/backend-connected-crm-slice`

## Scope

This change connects the existing protected company/contact frontend screens to the FastAPI
company/contact endpoints.

The goal is the first vertical slice:

1. Sign in with the local demo account.
2. Load protected company/contact data from FastAPI.
3. Create a company through the frontend API client.
4. Create a contact linked to an existing company.
5. Refresh/reload the frontend route and read the same data from the backend again.

## Implemented

- Added local CORS configuration for the Next.js dev origin.
- Added a frontend API client that reads `NEXT_PUBLIC_API_BASE_URL`.
- Stored the local development bearer token in the mock session.
- Verified login against `GET /users/me` before entering the protected area.
- Replaced mock-only company/contact hooks with FastAPI GET calls.
- Replaced local-only create behavior with FastAPI POST calls.
- Kept Supabase out of this slice because Supabase integration is not ready yet.

## Persistence Boundary

Persistence currently means persistence inside the running FastAPI process.

That is enough for the Week 1 vertical slice after browser refresh because refreshing the browser
re-runs GET requests against the same backend process. Data will reset when the backend process
restarts because the repository is still in memory.

Long-term durable persistence remains a Supabase integration task.

## Verification

Commands run:

```powershell
cd backend
python -m pytest
```

Result:

```text
19 passed
```

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

Manual backend smoke test:

```text
CreatedCompany         : Refresh Persistence Labs
CreatedContact         : Lena Stone
CompanyTotalFirstRead  : 1
CompanyTotalSecondRead : 1
ContactTotalSecondRead : 1
```

Browser automation note:

The in-app browser connector was unavailable in this session, so the responsive browser flow was not
clicked visually by Codex. The frontend build and HTTP smoke test verify the implementation paths.

## Remaining TODO

- Replace local demo tokens with Supabase Auth JWT verification.
- Replace the in-memory backend repository with Supabase PostgreSQL persistence.
- Add frontend automated tests once the team chooses the test runner.
- Manually click through login, company creation, contact creation, and route refresh in the browser.
