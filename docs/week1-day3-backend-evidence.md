# Week 1 Day 3 Backend Evidence

Task from brief:

- Create FastAPI config.
- Keep health endpoint working.
- Add auth verification.
- Add company/contact APIs.
- Ensure OpenAPI shows tested endpoints with valid/invalid examples.

Owner area:

- Intern 1 / Backend and Data.

## Implemented

### FastAPI config

- `backend/app/core/config.py` now reads:
  - `APP_NAME`
  - `APP_ENV`
  - `AUTH_MODE`
  - `LOG_LEVEL`
- `backend/app/main.py` uses `settings.app_name` for the FastAPI app title.

### Health endpoint

Implemented endpoint:

```http
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

### Auth verification

Implemented local development bearer-token verification in:

```text
backend/app/core/auth.py
```

Current local tokens:

- `dev-admin`
- `dev-management`
- `dev-business-development`
- `dev-technical-analyst`
- `dev-read-only`

Implemented endpoint:

```http
GET /users/me
Authorization: Bearer dev-business-development
```

Expected response:

```json
{
  "id": "00000000-0000-4000-8000-000000000003",
  "email": "bd.demo@example.test",
  "full_name": "Business Development Demo",
  "role": "business_development"
}
```

Missing token should return `401`.

Invalid token should return `401`.

### Company APIs

Implemented endpoints:

```http
GET /companies
POST /companies
GET /companies/{company_id}
```

List endpoints support:

- `limit`, default `50`, min `1`, max `100`
- `offset`, default `0`, min `0`

Write access is restricted to:

- `admin`
- `management`
- `business_development`

`read_only` cannot create companies.

### Contact APIs

Implemented endpoints:

```http
GET /contacts
POST /contacts
GET /contacts/{contact_id}
```

List endpoints support:

- `company_id` optional filter
- `limit`, default `50`, min `1`, max `100`
- `offset`, default `0`, min `0`

Write access is restricted to:

- `admin`
- `management`
- `business_development`

`read_only` cannot create contacts.

## OpenAPI / Swagger Evidence

Run backend from repository root:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Open Swagger:

```text
http://localhost:8000/docs
```

The following paths must be visible:

- `GET /health`
- `GET /users/me`
- `GET /companies`
- `POST /companies`
- `GET /companies/{company_id}`
- `GET /contacts`
- `POST /contacts`
- `GET /contacts/{contact_id}`

Machine-checkable OpenAPI verification:

```bash
cd backend
python -c "from app.main import app; print(sorted(app.openapi()['paths'].keys()))"
```

Expected paths:

```text
['/companies', '/companies/{company_id}', '/contacts', '/contacts/{contact_id}', '/health', '/users/me']
```

## Swagger Manual Test Flow

Open:

```text
http://localhost:8000/docs
```

Click `Authorize` and enter:

```text
dev-business-development
```

If Swagger expects the full value, use:

```text
Bearer dev-business-development
```

Test these:

1. `GET /health`
   - Expected: `200`, `{"status": "ok"}`
2. `GET /users/me` without token
   - Expected: `401`
3. `GET /users/me` with token
   - Expected: `200`, current demo user
4. `POST /companies` with a valid company body
   - Expected: `201`
5. `POST /companies` with invalid body such as empty `name`
   - Expected: `422`
6. `GET /companies`
   - Expected: `200`, created companies appear while backend process is running
7. `POST /contacts` with a valid `company_id`
   - Expected: `201`
8. `POST /contacts` with invalid UUID or invalid email
   - Expected: `422`
9. `POST /contacts` with unknown `company_id`
   - Expected: `404`

## Automated Verification

Run from repository root:

```bash
python -m pytest
python -m ruff check .
```

Latest local result:

- pytest: `18 passed`
- Ruff: `All checks passed`

## Current Limitation

Company/contact persistence currently uses an in-memory repository:

```text
backend/app/services/growth_repository.py
```

This is intentional for the Day 3 API contract slice. Data created through Swagger exists only while the backend process is running.

Supabase-backed persistence is the next backend integration step after the API contract and auth flow are reviewed.
