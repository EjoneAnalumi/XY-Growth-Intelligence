# API Contract

This file records request and response examples before dependent frontend screens are built.

Breaking API changes require a Yellow decision and same-day update here.

## Current Implemented Endpoint

### Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Current User

```http
GET /users/me
Authorization: Bearer dev-business-development
```

Local development response:

```json
{
  "id": "00000000-0000-4000-8000-000000000003",
  "email": "bd.demo@example.test",
  "full_name": "Business Development Demo",
  "role": "business_development"
}
```

Invalid or missing token response:

```json
{
  "detail": "Missing bearer token."
}
```

Local development demo tokens:

- `dev-admin`
- `dev-management`
- `dev-business-development`
- `dev-technical-analyst`
- `dev-read-only`

## Minimum API Groups From Brief

These groups are required later in the MVP:

- `GET /users/me`
- `/companies`
- `/companies/{id}/timeline`
- `/contacts`
- `/opportunities`
- `/opportunities/{id}/move-stage`
- `/activities`
- `/tasks`
- `/companies/{id}/calculate-icp`
- `/companies/{id}/recommendations`
- `/companies/{id}/security-scans`
- `/security-scans/{id}/findings`
- `/reports`
- `/reports/{id}/generate`
- `/reports/{id}/approve`
- `/reports/{id}/download`
- `/dashboard/summary`
- `/dashboard/pipeline`
- `/dashboard/forecast`
- `/dashboard/follow-ups`

## API Rules

- Every write validates user permission and request data.
- Every list endpoint supports pagination or a documented practical limit.
- Important list endpoints support search, filter, and sort.
- Errors use consistent status codes and user-safe messages.
- Critical calculations have automated tests with known inputs and outputs.
- OpenAPI documentation should include readable example payloads.

## TODO: Week 1 Contracts

- `GET /users/me`
- `GET /companies`
- `POST /companies`
- `GET /companies/{id}`
- `PATCH /companies/{id}`
- `GET /contacts`
- `POST /contacts`
- `GET /contacts/{id}`
- `PATCH /contacts/{id}`
