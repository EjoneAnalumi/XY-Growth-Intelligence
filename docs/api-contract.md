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

### Companies

```http
GET /companies
Authorization: Bearer dev-business-development
```

Response:

```json
{
  "items": [],
  "total": 0
}
```

```http
POST /companies
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "name": "Northstar Robotics Labs",
  "domain": "northstar-robotics.example",
  "industry": "Manufacturing Technology",
  "headquarters_country": "United States",
  "lead_source": "conference"
}
```

Invalid request:

```json
{
  "name": "",
  "employee_count": -1
}
```

```http
GET /companies/{company_id}
Authorization: Bearer dev-business-development
```

Not found response:

```json
{
  "detail": "Company not found."
}
```

### Contacts

```http
GET /contacts
Authorization: Bearer dev-business-development
```

Optional query:

```http
GET /contacts?company_id={company_id}
```

```http
POST /contacts
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "company_id": "10000000-0000-4000-8000-000000000001",
  "first_name": "Mira",
  "last_name": "Vale",
  "email": "mira.vale@northstar-robotics.example",
  "decision_category": "champion"
}
```

Invalid request:

```json
{
  "company_id": "not-a-uuid",
  "first_name": "",
  "last_name": "",
  "email": "not-an-email"
}
```

```http
GET /contacts/{contact_id}
Authorization: Bearer dev-business-development
```

Not found response:

```json
{
  "detail": "Contact not found."
}
```

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
- `GET /companies`: implemented with local in-memory repository.
- `POST /companies`: implemented with local in-memory repository.
- `GET /companies/{id}`: implemented with local in-memory repository.
- `PATCH /companies/{id}`
- `GET /contacts`: implemented with local in-memory repository.
- `POST /contacts`: implemented with local in-memory repository.
- `GET /contacts/{id}`: implemented with local in-memory repository.
- `PATCH /contacts/{id}`
