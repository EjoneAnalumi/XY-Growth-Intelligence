# XY CYBER Growth Intelligence

An internal platform for managing prospects, tracking sales opportunities and follow-ups,
and preparing reviewed Cyber Risk Snapshot reports. Built as a single monorepo for the
XY CYBER internship MVP, using synthetic data.

## Features

- Companies and contacts with editable profiles, search, sorting and activity timelines.
- Opportunity pipeline with Kanban/table views, stage history and EUR values.
- Configurable ICP scoring, service recommendations and management analytics.
- Assigned tasks, deadline reminders, team notes and personal unread indicators.
- Approved mock security snapshots, report previews, review/approval and PDF downloads.
- Role-based access, user administration and CSV import/export.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | Next.js, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | Python 3.12, FastAPI, Pydantic |
| Database and authentication | Supabase PostgreSQL, Auth, Row Level Security |
| Report storage | Supabase Storage |
| Development and testing | Docker, Docker Compose, pytest, Ruff, Vitest, Playwright |

## Run locally

Requires **Python 3.12**, **Node.js 22.12+**, **Git**, and **Docker Desktop** running
Linux containers. Commands below use Windows PowerShell.

### 1. Install dependencies

```powershell
git clone https://github.com/EjoneAnalumi/XY-Growth-Intelligence.git
cd XY-Growth-Intelligence
Copy-Item .env.example .env

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt

cd frontend
npm.cmd ci
cd ..
```

### 2. Start the database and app

```powershell
npx.cmd --yes supabase@2.115.0 start
.\.venv\Scripts\Activate.ps1
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start-local.ps1
```

The startup script reads local Supabase configuration and starts the backend and frontend
in separate terminals. It preserves existing local data. Both services must be running.
For first-time database/report seeding, manual startup, Docker Compose and troubleshooting,
follow the [complete setup guide](docs/week4-day20-local-setup-guide.md).

| Service | Address |
| --- | --- |
| Application | http://localhost:3000/login |
| Backend API docs | http://localhost:8000/docs |
| Supabase Studio | http://localhost:54323 |
| Local test email | http://localhost:54324 |

Sign in with a local synthetic account or an invited staff account. Local demo account
setup is defined in [the seed migration](database/migrations/20260815000001_report_persistence.sql).

After pulling database changes, apply migrations without resetting your records:

```powershell
npx.cmd --yes supabase@2.115.0 migration up --local
```

To stop, press `Ctrl+C` in the backend/frontend terminals, then run:

```powershell
npx.cmd --yes supabase@2.115.0 stop
```

Keep credentials in local environment configuration, never in Git. Use synthetic data only.

## Project structure

```text
backend/       FastAPI application and tests
frontend/      Next.js application and tests
database/      Migrations and synthetic seed data
supabase/      Local Supabase configuration and mirrored migrations
docs/          Setup, architecture, API reference and project evidence
sample-data/   Example CSV files
scripts/       Local startup helper
```

## Documentation

- [Setup, test commands and troubleshooting](docs/week4-day20-local-setup-guide.md)
- [Architecture and operations](docs/week4-day20-architecture-operations.md)
- [API reference](docs/api-contract.md)
- [User guide](docs/week4-day20-demo-user-guide.md)
- [Validation results and remaining work](docs/week4-day20-submission-readiness.md)
