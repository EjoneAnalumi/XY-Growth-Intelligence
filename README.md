# XY CYBER Growth Intelligence

Internal Growth Intelligence MVP for the XY CYBER one-month internship project. The monorepo contains a FastAPI backend, a Next.js frontend, Supabase PostgreSQL migrations and synthetic seed data, and local Docker configuration.

## Current MVP status

Implemented flows include company/contact management, opportunity pipeline views, activities and tasks, ICP scoring, dashboard metrics, safe snapshot checks, report workflow, and company CSV import/export.

Important current limitations:

- Staff authentication uses invitation-only Supabase Auth sessions. Public registration is disabled; Admin users invite staff and assign roles.
- When `DATABASE_URL` is configured, companies, contacts, opportunities, activities, tasks, and notes use the Supabase PostgreSQL database and survive browser logout and backend restart. Unit tests without a database URL retain an isolated in-memory repository.
- CSV, snapshot, and report paths also use PostgreSQL persistence.
- Docker Compose starts the backend only. Run the frontend separately with npm.
- Use synthetic data only. Never place hosted credentials, production keys, or real customer/prospect data in this repository.

Local Supabase provides seeded synthetic accounts for development. Production must configure its own invited users, redirect URLs, SMTP provider, and scoped secrets.

See [`docs/week4-day18-website-change-handoff.md`](docs/week4-day18-website-change-handoff.md) for the consolidated implementation, security, verification, and remaining-work record.

## Prerequisites

Install these before cloning:

- Git
- Python 3.12
- Node.js LTS with npm
- Docker Desktop configured for Linux containers

The commands below are tested with Windows PowerShell. Use `npm.cmd` and `npx.cmd` because PowerShell may block the `npm.ps1` and `npx.ps1` shims.

Verify the tools:

```powershell
git --version
python --version
node --version
npm.cmd --version
docker --version
docker compose version
docker info
```

`docker info` must show a running server. If it cannot connect to `dockerDesktopLinuxEngine`, start Docker Desktop and wait until the engine is ready.

## Clean installation

### 1. Clone and create the local environment file

```powershell
git clone https://github.com/EjoneAnalumi/XY-Growth-Intelligence.git
Set-Location XY-Growth-Intelligence
Copy-Item .env.example .env
```

`.env` is ignored by Git. Keep all generated local values and any hosted secrets out of commits, screenshots, documentation, and chat messages.

### 2. Start local Supabase

This project pins the tested CLI version in each command, so a global Supabase CLI installation is not required. The first start downloads several Docker images and can take multiple minutes.

```powershell
npx.cmd --yes supabase@2.115.0 start
```

On Windows, Docker can report Auth and Mailpit as unhealthy even when their processes are serving. If the command times out after migrations and seed data complete, use the CLI-supported workaround and then inspect status:

```powershell
npx.cmd --yes supabase@2.115.0 start --ignore-health-check
npx.cmd --yes supabase@2.115.0 status
```

Copy only these generated **local** values from `supabase status` into the matching placeholders in the ignored `.env` file:

- `ANON_KEY` -> `SUPABASE_ANON_KEY` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SERVICE_ROLE_KEY` -> `SUPABASE_SERVICE_ROLE_KEY`

Do not place `SERVICE_ROLE_KEY` in any `NEXT_PUBLIC_*` variable. Never use hosted or production keys for local development.

For the first clean installation only, apply every tracked migration and recreate the synthetic dataset:

```powershell
npx.cmd --yes supabase@2.115.0 db reset
```

The configuration reads migrations from `database/migrations/**/*.sql` and seed data from `database/seed/seed.sql`.

> **Warning:** `supabase db reset` deletes locally created notes, users, and CRM changes. Do not run it during normal startup or after restarting the laptop.

For normal daily use, run this single command from the repository root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start-local.ps1
```

It starts the existing Supabase database without resetting it and launches both the backend and frontend with persistent PostgreSQL storage enabled.

Local service URLs:

- Supabase API: http://127.0.0.1:54321
- Supabase Studio: http://127.0.0.1:54323
- Mailpit: http://127.0.0.1:54324
- PostgreSQL: `127.0.0.1:54322`

### 3. Install and verify the backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check backend
```

Run the integrated Supabase Auth backend container from the repository root. This block reads local-only values into the current PowerShell process without printing or committing them:

```powershell
$lines = npx.cmd --yes supabase@2.115.0 status -o env 2>$null
foreach ($line in $lines) {
    if ($line -match '^([A-Z_]+)="(.*)"$') {
        Set-Item -Path "Env:$($matches[1])" -Value $matches[2]
    }
}
$env:BACKEND_PORT = '8000'
$env:AUTH_MODE = 'supabase'
$env:SUPABASE_URL = $env:API_URL
$env:SUPABASE_ANON_KEY = $env:ANON_KEY
$env:SUPABASE_SERVICE_ROLE_KEY = $env:SERVICE_ROLE_KEY
docker compose up --build --detach
docker compose ps
```

The Compose configuration translates host Supabase addresses to `host.docker.internal` inside the backend container. It does not start the frontend or Supabase.

Verify the backend at http://localhost:8000/health. The expected response is:

```json
{"status":"ok"}
```

API documentation is available at http://localhost:8000/docs.

### 4. Install and verify the frontend

Open another PowerShell terminal only when running the services manually instead of using `scripts/start-local.ps1`:

```powershell
$repo = 'C:\Users\LENOVO\Documents\GitHub\XY-Growth-Intelligence'
Set-Location $repo
$lines = npx.cmd --yes supabase@2.115.0 status -o env 2>$null
foreach ($line in $lines) {
    if ($line -match '^([A-Z_]+)="(.*)"$') {
        Set-Item -Path "Env:$($matches[1])" -Value $matches[2]
    }
}
$env:NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000'
$env:NEXT_PUBLIC_SUPABASE_URL = $env:API_URL
$env:NEXT_PUBLIC_SUPABASE_ANON_KEY = $env:ANON_KEY
Set-Location frontend
npm.cmd ci
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run dev -- --port 3000
```

Open http://localhost:3000/login. Run both services from the current `main` checkout.

### 5. Shut everything down

Stop a directly run backend/frontend with `Ctrl+C`. From the repository root, stop the managed containers:

```powershell
docker compose down
npx.cmd --yes supabase@2.115.0 stop
```

## Supabase-enabled backend checks

The default test command intentionally runs without database credentials and skips environment-dependent report/RLS integration cases. To run the local integration groups, obtain values from `supabase status`, set them only in the current shell, and run:

```powershell
$env:DATABASE_URL='<local DB_URL>'
$env:SUPABASE_DB_URL='<local DB_URL>'
$env:SUPABASE_URL='<local API_URL>'
$env:SUPABASE_SERVICE_ROLE_KEY='<local SERVICE_ROLE_KEY>'
.\.venv\Scripts\python.exe -m pytest backend\tests\test_reports.py backend\tests\test_week2_rls_permissions.py
```

Do not paste the values into tracked scripts. CSV unit cases explicitly use their in-memory repository, while a separate isolated CSV integration case verifies PostgreSQL import/export without deleting or depending on the normal seeded companies.

## Troubleshooting

### Compose says `.env` is missing

```powershell
Copy-Item .env.example .env
```

### Docker cannot connect

Start Docker Desktop, ensure Linux containers are enabled, wait for startup, and rerun `docker info`.

### PowerShell blocks npm, npx, or Codex scripts

Use the Windows command shims: `npm.cmd`, `npx.cmd`, and `codex.cmd`.

### Supabase reports `exec format error`

Use the exact image names printed by the Supabase error. Stop Supabase, remove only those named cached images, and retry. For the two images observed during the Day 18 Windows test:

```powershell
npx.cmd --yes supabase@2.115.0 stop
docker image rm --force public.ecr.aws/supabase/mailpit:v1.30.2 public.ecr.aws/supabase/postgrest:v16.1
npx.cmd --yes supabase@2.115.0 start
```

Do not remove unrelated images or volumes.

### Auth or Mailpit stays unhealthy

Check the container logs first. If they show the services started and the standard command only fails its health gate, use:

```powershell
npx.cmd --yes supabase@2.115.0 start --ignore-health-check
npx.cmd --yes supabase@2.115.0 status
```

This is a local Windows/Docker workaround, not permission to ignore failures in hosted or production environments.

### A port is already occupied

The local stack requires ports `3000`, `8000`, and `54320` through `54329`. Stop the conflicting process or intentionally change all matching configuration references before retrying.

Before starting the app, inspect only its expected ports:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 3000,3001,3002,8000,8001 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

Stop a confirmed stale Node/Python process by its displayed PID, then stop any old Compose backend:

```powershell
Stop-Process -Id <PID> -Force
Set-Location 'C:\Users\LENOVO\Documents\GitHub\XY-Growth-Intelligence\.worktrees\supabase-auth'
docker compose down
```

Do not stop ports `54320` through `54329` when keeping local Supabase available. If `127.0.0.1:8000` still serves a response but its reported PID does not exist in `Get-Process` or `tasklist`, Windows has retained an orphaned listener. Restart Windows before starting Docker Desktop and the commands above; repeated app starts cannot safely clear a nonexistent process.

## Repository structure

```text
backend/             FastAPI application and pytest suite
frontend/            Next.js application and frontend tests
database/migrations/ PostgreSQL migrations
database/seed/       Synthetic seed data
supabase/            Local Supabase configuration
docs/                Architecture, API, decisions, and internship evidence
sample-data/         Synthetic CSV fixtures
docker-compose.yml   Backend container for local development
```

See `docs/architecture.md`, `docs/api-contract.md`, and `docs/decision-log.md` for implementation details and recorded decisions.
