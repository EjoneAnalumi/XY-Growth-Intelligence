# Week 1 Day 5 Demo Script

Date: 05-08-2026

Scope: Week 1 gate only.

## Prerequisites

- Backend terminal running FastAPI.
- Frontend terminal running Next.js.
- No real secrets or customer/prospect data.
- Use fictional `.example` company/contact data.

## Commands

Backend:

```powershell
cd C:\Users\LENOVO\Documents\GitHub\XY-Growth-Intelligence\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd C:\Users\LENOVO\Documents\GitHub\XY-Growth-Intelligence\frontend
npm.cmd run dev
```

Open:

```text
http://localhost:3000/login
```

## Demo Flow

1. Show the repository structure briefly.
2. Show `.env.example` and mention that it contains placeholders only.
3. Open `http://localhost:8000/docs`.
4. Confirm Swagger shows:
   - `GET /health`
   - `GET /users/me`
   - `GET/POST /companies`
   - `GET/POST /contacts`
5. Open `http://localhost:3000/login`.
6. Sign in with the default local demo values.
7. Confirm the protected app layout appears.
8. Open Companies.
9. Create a company:

```text
Name: Demo Compliance Labs
Domain: demo-compliance.example
Industry: Healthcare
Country: Germany
```

10. Open Contacts.
11. Create a contact linked to the company:

```text
Company: Demo Compliance Labs
First name: Mira
Last name: Vale
Email: mira.vale@demo-compliance.example
Role: CISO
```

12. Refresh the browser.
13. Confirm the company/contact are still listed while the same backend process is running.
14. Show test output:

```text
python -m pytest -> 19 passed
python -m ruff check . -> All checks passed!
npm.cmd run typecheck -> passed
npm.cmd run lint -> passed
npm.cmd run build -> passed
```

## What To Say

Week 1 proves the first vertical slice: local login, protected layout, company creation, contact creation, and refresh persistence against FastAPI. Supabase schema and RLS are tracked in migrations, but runtime persistence still uses an in-memory backend repository until Supabase integration is connected.

## Known Limitations

- Data persists after browser refresh, but not after backend restart.
- Supabase Auth JWT verification is still TODO.
- Supabase RLS needs manual test evidence in a Supabase test project.
