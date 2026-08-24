# Backend

FastAPI backend for the XY CYBER Growth Intelligence MVP.

Use the root [README](../README.md) for the complete clean-install, Supabase, Docker, environment, and shutdown procedure.

## Local checks

Create the shared virtual environment from the repository root, then run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check backend
```

Start FastAPI directly:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: http://127.0.0.1:8000/health
- OpenAPI UI: http://127.0.0.1:8000/docs

## Runtime boundaries

- Local bearer-token authentication and role checks are implemented; Supabase Auth JWT verification is not yet connected.
- With `DATABASE_URL` set, core CRM and pipeline repositories persist to Supabase PostgreSQL. Without it, tests use isolated in-memory repositories.
- Core CRM and pipeline repositories remain in memory, so new records do not survive a backend restart.
- PostgreSQL-backed behavior currently covers selected company CSV, snapshot, and report paths.
- `DATABASE_URL`, `SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY` enable relevant local integrations. Keep the service-role key server-side and never expose it through `NEXT_PUBLIC_*` variables.
- The backend container reaches host-published Supabase services through `host.docker.internal`; direct host execution uses `127.0.0.1`.
