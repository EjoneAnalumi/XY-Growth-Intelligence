# Backend

FastAPI backend for protected business logic in the XY CYBER Growth Intelligence MVP.

## Current Implementation

- `GET /health`
- Environment configuration helper
- Structured JSON logging setup
- Basic pytest coverage
- Local snapshot-to-report fallback for development without Supabase runtime credentials

## Run Locally

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python -m ruff check .
python -m uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/health
```

Expected response:

```json
{"status": "ok"}
```

Snapshot/report integration uses the tracked Supabase migrations when these environment variables
are configured:

```text
DATABASE_URL
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

If they are not configured, the backend uses an in-memory fallback so the approved demo
snapshot-to-report flow can still be tested locally without committing secrets.

## Near-Term TODO

- Supabase Auth token verification.
- User profile and role lookup.
- Company/contact API endpoints.
- Permission checks for writes.
- Consistent error response helpers.
- API examples in `docs/api-contract.md`.
