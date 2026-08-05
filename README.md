# XY CYBER Growth Intelligence

Internal Growth Intelligence MVP for the XY CYBER one-month internship project.

The goal is to build a secure internal platform that helps XY CYBER manage prospects, score opportunities, track follow-ups, analyze pipeline performance, and generate approved executive Cyber Risk Snapshot reports.

## Stack

- Backend: Python 3.12, FastAPI, Pydantic, pytest, Ruff, structured logging
- Database: Supabase PostgreSQL, migrations, Row Level Security, seed data
- Frontend: Next.js, TypeScript, Tailwind CSS, shadcn/ui
- Local development: Docker Compose

## Current Status

This repository currently contains the Week 1 foundation and first vertical slice:

- Minimal FastAPI backend with `GET /health`
- Local bearer-token auth verification with `GET /users/me`
- Company/contact FastAPI endpoints with validation and role checks
- Basic pytest coverage for health, auth, company/contact APIs, CORS, and OpenAPI exposure
- Next.js protected app shell with login, navigation, company page, and contact page
- Frontend API client connected to FastAPI for company/contact create and list behavior
- Supabase migration for `profiles`, `companies`, and `contacts`, ready to apply through the local Supabase CLI workflow (`supabase start` and `supabase db reset`)
- First RLS policies using the brief roles: Admin, Management, Business Development, Technical Analyst, and Read Only
- Synthetic seed data with 30 fictional companies and 50 fictional contacts, configured for local Supabase reset through `database/seed/seed.sql`
- Project documentation, evidence logs, API contract, and Week 1 status report
- Docker Compose and environment template placeholders
- CI placeholder for backend lint and tests

The Week 1 gate works locally with the current FastAPI in-memory repository: a user can log in with the local demo session, create a company, add a contact, and see that data after browser refresh while the backend process remains running.

Durable Supabase-backed runtime persistence is still TODO. Do not start optional AI summaries, advanced charts, public deployment, or live third-party scanning until the required MVP flow remains stable.

## Local Setup Placeholder

Prerequisites:

- Python 3.12
- Node.js LTS
- Docker Desktop for the local Supabase stack
- Supabase CLI (`npm install -g supabase`)

Backend skeleton check:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest
python -m ruff check .
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://localhost:8000/health
```

Frontend check in a second terminal:

```bash
cd frontend
npm.cmd install
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
npm.cmd run dev
```

Then open:

```text
http://localhost:3000/login
```

Use the local demo login defaults shown on the login screen.

Docker Compose placeholder:

```bash
docker compose up --build
```

Local Supabase schema and seed check:

```bash
supabase start
supabase db reset
```

`supabase/config.toml` applies migrations from `database/migrations/**/*.sql` and seed data from `database/seed/seed.sql`.

Remote or hosted Supabase changes are not the default Week 1 path. Treat remote database pushes as a coordinated decision and use only approved synthetic data.

## Security Rules

- Use synthetic data only.
- Never commit real secrets, API keys, customer data, prospect data, or Supabase service role keys.
- Keep real environment values in local `.env` files only.
- Commit only placeholder values in `.env.example`.
- Do not build optional features before the required MVP flow works end to end.
- Use Row Level Security for Supabase tables when database work begins.
- Use Supabase Auth; do not store passwords in application tables.
- Backend authorization must protect sensitive writes and privileged actions.
- Cyber Risk Snapshot checks must be safe, scoped, and approved or mocked.
- Reports must not be automatically emailed or externally shared.

## Week 1 Gate

A user must be able to log in, create a company, add a contact, and see the data after refresh.

Current Week 1 local gate status:

- Login: implemented with local demo session and backend `/users/me` verification.
- Create company: implemented through FastAPI.
- Add contact: implemented through FastAPI.
- Browser refresh: data remains visible while the same backend process is running.

Remaining Week 1 limitations:

- Supabase Auth JWT verification is not connected yet.
- Runtime company/contact persistence is in memory, not Supabase PostgreSQL.
- Manual RLS allow/deny checks still need to be performed in a Supabase test project.

## Repository Structure

```text
xy-growth-intelligence/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- scoring/
|   |   |-- scanning/
|   |   `-- reporting/
|   |-- tests/
|   `-- Dockerfile
|-- frontend/
|   |-- app/
|   |-- components/
|   |-- lib/
|   |-- hooks/
|   `-- tests/
|-- database/
|   |-- migrations/
|   |-- policies/
|   `-- seed/
|-- docs/
|-- sample-data/
|-- docker-compose.yml
|-- .env.example
|-- .gitignore
`-- README.md
```
