# Local setup and troubleshooting

Date: 01-10-2026

Complete setup instructions for the XY CYBER Growth Intelligence monorepo.
Run commands from the repository root unless a step says otherwise.

## Prerequisites

Install these before cloning:

- Git
- Python 3.12
- Node.js 22 LTS (22.12 or newer) with npm
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

The CLI applies versioned migrations from `supabase/migrations/`; matching copies are
maintained in `database/migrations/`. The configuration references the database schema
paths and loads seed data from `database/seed/seed.sql`.
SQL creates the CRM fixtures and five scans. After backend dependencies and local environment
variables are ready in step 3, complete the five report fixtures with `python -m app.seed_reports`.
Reports require actual private Storage uploads, so SQL alone cannot complete them.

> **Warning:** `supabase db reset` deletes locally created notes, users, and CRM changes. Do not run it during normal startup or after restarting the laptop.

For an existing installation after pulling schema changes, apply pending migrations
without resetting local records:

```powershell
npx.cmd --yes supabase@2.115.0 migration up --local
```

After completing dependency installation in steps 3 and 4, the daily startup helper
below starts both application services. It uses `python` from the shell's PATH, so first
activate the project virtual environment; if PowerShell blocks activation, use the manual
Docker/backend and frontend instructions below instead. Do not run the helper alongside
an existing backend on port 8000.

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
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
$env:DATABASE_URL = $env:DB_URL
$env:APP_ENV = 'local'
# Completes the local seed with five real PDFs; preserves existing report states.
Push-Location backend
..\.venv\Scripts\python.exe -m app.seed_reports
Pop-Location
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
# Run this from the repository cloned in step 1; do not use a machine-specific
# worktree path from a previous developer environment.
$repo = (Get-Location).Path
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
npm.cmd test
npm.cmd run build
npm.cmd run dev -- --port 3000
```

Open http://localhost:3000/login. Run both services from this checkout. Local synthetic account identities are documented in `database/migrations/20260815000001_report_persistence.sql`; use those only on the local stack.

### 5. Shut everything down

Stop a directly run backend/frontend with `Ctrl+C`. From the repository root, stop the managed containers:

```powershell
docker compose down
npx.cmd --yes supabase@2.115.0 stop
```

## Supabase-enabled backend checks

The default test command intentionally runs without database credentials and skips environment-dependent report/RLS integration cases. To run the local integration groups, obtain values from `supabase status`, set them only in the current shell, and run:

```powershell
$env:AUTH_MODE='local' # Integration suite uses synthetic test-role tokens; live UI uses supabase.
$env:DATABASE_URL='<local DB_URL>'
$env:SUPABASE_DB_URL='<local DB_URL>'
$env:SUPABASE_URL='<local API_URL>'
$env:SUPABASE_SERVICE_ROLE_KEY='<local SERVICE_ROLE_KEY>'
.\.venv\Scripts\python.exe -m pytest backend
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
docker compose down
```

Run `docker compose down` from the repository root.

Do not stop ports `54320` through `54329` when keeping local Supabase available. If `127.0.0.1:8000` still serves a response but its reported PID does not exist in `Get-Process` or `tasklist`, Windows has retained an orphaned listener. Restart Windows before starting Docker Desktop and the commands above; repeated app starts cannot safely clear a nonexistent process.
