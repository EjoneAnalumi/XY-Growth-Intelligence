# XY CYBER Growth Intelligence

Internal Growth Intelligence MVP for the XY CYBER one-month internship project.

The goal is to build a secure internal platform that helps XY CYBER manage prospects, score opportunities, track follow-ups, analyze pipeline performance, and generate approved executive Cyber Risk Snapshot reports.

## Stack

- Backend: Python 3.12, FastAPI, Pydantic, pytest, Ruff, structured logging
- Database: Supabase PostgreSQL, migrations, Row Level Security, seed data
- Frontend: Next.js, TypeScript, Tailwind CSS, shadcn/ui
- Local development: Docker Compose

## Current Status

This repository currently contains the initial monorepo foundation plus the Week 1 Day 2 database baseline:

- Minimal FastAPI backend with `GET /health`
- Basic pytest coverage for the health endpoint
- Placeholder frontend directory structure
- Supabase migration for `profiles`, `companies`, and `contacts`, applied to the live Supabase project via the Supabase CLI (`supabase db push`)
- First RLS policies using the brief roles: Admin, Management, Business Development, Technical Analyst, and Read Only
- Synthetic seed data with 10 fictional companies and fictional contacts, applied via the Supabase CLI (`supabase db query --file supabase/seed.sql --linked`)
- Project documentation placeholders
- Docker Compose and environment template placeholders
- CI placeholder for backend lint and tests

The full Week 1 vertical slice is still TODO because Supabase auth integration, company/contact APIs, and the Next.js login/company/contact screens are not implemented yet. Do not start optional AI summaries, advanced charts, public deployment, or live third-party scanning until the required MVP flow works end to end.

## Local Setup Placeholder

Prerequisites:

- Python 3.12
- Node.js LTS
- Docker Desktop (optional; only needed for local Supabase development via `supabase start`, not required for the current CLI workflow against the remote project)
- Supabase CLI (`npm install -g supabase`), already installed, logged in, and linked to the project via `supabase link --project-ref <project-ref>`

Backend skeleton check:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000/health
```

Docker Compose placeholder:

```bash
docker compose up --build
```

The frontend service is intentionally not wired yet because Next.js has not been initialized.

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

Until this works, prioritize:

1. Apply and manually test the Supabase schema, seed data, and first RLS policies.
2. FastAPI config, health endpoint, auth verification, and company/contact APIs.
3. Next.js app shell, login, protected routes, and company/contact list/forms.
4. Integration evidence, tests, and documentation.

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