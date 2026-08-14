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
GET /companies?limit=50&offset=0
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

```http
POST /companies/{company_id}/calculate-icp
Authorization: Bearer dev-business-development
```

Valid response shape:

```json
{
  "id": "90000000-0000-4000-8000-000000000001",
  "company_id": "10000000-0000-4000-8000-000000000001",
  "score": 100,
  "max_score": 100,
  "tier": "strong_fit",
  "explanations": [
    {
      "rule_id": "industry_fit",
      "label": "Industry fit",
      "points": 25,
      "max_points": 25,
      "explanation": "Financial Services is a highly regulated target industry."
    }
  ],
  "calculated_by": "00000000-0000-4000-8000-000000000003",
  "calculated_at": "2026-08-06T09:00:00Z"
}
```

Scoring rules:

- Score is deterministic for the same company input.
- Score range is `0` to `100`.
- Tiers are `strong_fit`, `good_fit`, `possible_fit`, and `low_fit`.
- The result stores rule-by-rule explanations.
- The company `fit_score` is updated to the latest calculated score.

### Contacts

```http
GET /contacts?limit=50&offset=0
Authorization: Bearer dev-business-development
```

Optional query:

```http
GET /contacts?company_id={company_id}&limit=50&offset=0
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

### Pipeline Stages

Pipeline stages are read by all authenticated roles. Creating, editing, or archiving stages is
limited to `admin` and `management`.

```http
GET /pipeline-stages
Authorization: Bearer dev-business-development
```

Response:

```json
{
  "items": [
    {
      "id": "30000000-0000-4000-8000-000000000001",
      "name": "Identified",
      "sort_order": 10,
      "default_probability": 5,
      "is_won": false,
      "is_lost": false,
      "created_at": "2026-08-05T10:00:00Z",
      "updated_at": "2026-08-05T10:00:00Z"
    }
  ],
  "total": 15
}
```

```http
POST /pipeline-stages
Authorization: Bearer dev-management
Content-Type: application/json
```

Valid request:

```json
{
  "name": "Custom Review",
  "sort_order": 160,
  "default_probability": 20,
  "is_won": false,
  "is_lost": false
}
```

Permission denied response for Business Development:

```json
{
  "detail": "User does not have permission to perform this action."
}
```

### Opportunities

Opportunity writes are limited to `admin`, `management`, and `business_development`.

```http
GET /opportunities
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
POST /opportunities
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "company_id": "10000000-0000-4000-8000-000000000001",
  "contact_id": "20000000-0000-4000-8000-000000000001",
  "stage_id": "30000000-0000-4000-8000-000000000001",
  "name": "Managed SOC Pilot",
  "service": "Managed SOC",
  "value_usd": 50000,
  "probability": 40,
  "expected_close_date": "2026-09-30",
  "need": "Compliance-driven monitoring requirement",
  "next_action": "Schedule pilot planning call"
}
```

Successful response includes calculated weighted value:

```json
{
  "id": "generated-uuid",
  "company_id": "10000000-0000-4000-8000-000000000001",
  "contact_id": "20000000-0000-4000-8000-000000000001",
  "stage_id": "30000000-0000-4000-8000-000000000001",
  "name": "Managed SOC Pilot",
  "service": "Managed SOC",
  "value_usd": 50000,
  "probability": 40,
  "weighted_value_usd": 20000,
  "expected_close_date": "2026-09-30",
  "owner_id": null,
  "need": "Compliance-driven monitoring requirement",
  "blockers": null,
  "competitor": null,
  "next_action": "Schedule pilot planning call",
  "next_action_due_at": null,
  "lost_reason": null,
  "created_by": "00000000-0000-4000-8000-000000000003",
  "updated_by": "00000000-0000-4000-8000-000000000003",
  "archived_at": null,
  "created_at": "2026-08-05T10:00:00Z",
  "updated_at": "2026-08-05T10:00:00Z"
}
```

```http
PATCH /opportunities/{opportunity_id}
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "value_usd": 60000,
  "probability": 50,
  "next_action": "Send pilot checklist"
}
```

```http
DELETE /opportunities/{opportunity_id}
Authorization: Bearer dev-business-development
```

Delete is currently implemented as archive/soft delete and returns the archived record.

```http
PATCH /opportunities/{opportunity_id}/move-stage
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "to_stage_id": "30000000-0000-4000-8000-000000000003",
  "note": "Prospect replied to outreach."
}
```

Response:

```json
{
  "message": "Opportunity stage updated successfully.",
  "opportunity": {
    "id": "generated-opportunity-uuid",
    "stage_id": "30000000-0000-4000-8000-000000000003"
  },
  "history": {
    "id": "generated-history-uuid",
    "opportunity_id": "generated-opportunity-uuid",
    "from_stage_id": "30000000-0000-4000-8000-000000000001",
    "to_stage_id": "30000000-0000-4000-8000-000000000003",
    "changed_by": "00000000-0000-4000-8000-000000000003",
    "note": "Prospect replied to outreach.",
    "changed_at": "2026-08-05T10:05:00Z"
  }
}
```

```http
GET /opportunities/{opportunity_id}/stage-history
Authorization: Bearer dev-business-development
```

Response:

```json
[
  {
    "id": "generated-history-uuid",
    "opportunity_id": "generated-opportunity-uuid",
    "from_stage_id": "30000000-0000-4000-8000-000000000001",
    "to_stage_id": "30000000-0000-4000-8000-000000000003",
    "changed_by": "00000000-0000-4000-8000-000000000003",
    "note": "Prospect replied to outreach.",
    "changed_at": "2026-08-05T10:05:00Z"
  }
]

```

### Activities

```http
POST /activities
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "company_id": "10000000-0000-4000-8000-000000000001",
  "opportunity_id": "generated-opportunity-uuid",
  "activity_type": "meeting",
  "subject": "Discovery meeting",
  "notes": "Reviewed SOC monitoring priorities."
}
```

Supported activity types:

- `call`
- `email`
- `meeting`
- `linkedin_message`
- `conference`
- `introduction`
- `workshop`
- `demo`
- `proposal`
- `follow_up`
- `internal_note`

### Tasks

```http
POST /tasks
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "company_id": "10000000-0000-4000-8000-000000000001",
  "opportunity_id": "generated-opportunity-uuid",
  "title": "Send pilot checklist",
  "due_at": "2026-08-07T17:00:00Z",
  "priority": "high",
  "status": "open"
}
```

```http
PATCH /tasks/{task_id}
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "status": "completed",
  "outcome": "Checklist sent"
}
```

### Notes

```http
POST /notes
Authorization: Bearer dev-business-development
Content-Type: application/json
```

Valid request:

```json
{
  "company_id": "10000000-0000-4000-8000-000000000001",
  "opportunity_id": "generated-opportunity-uuid",
  "body": "Client asked for compliance references."
}
```

### Dashboard Summary

```http
GET /dashboard/summary
Authorization: Bearer dev-business-development
```

Valid response shape:

```json
{
  "total_opportunities": 4,
  "open_opportunities": 2,
  "won_opportunities": 1,
  "lost_opportunities": 1,
  "pipeline_value_usd": 140000,
  "weighted_pipeline_value_usd": 80000,
  "high_priority_opportunities": 1,
  "inactive_opportunities": 1,
  "open_tasks": 2,
  "overdue_tasks": 1,
  "due_this_week_tasks": 1,
  "activities_count": 2,
  "average_days_in_current_stage": 0,
  "stage_summaries": [
    {
      "stage_id": "30000000-0000-4000-8000-000000000001",
      "stage_name": "Identified",
      "opportunity_count": 1,
      "total_value_usd": 100000,
      "weighted_value_usd": 50000
    }
  ],
  "priority_opportunities": [
    {
      "opportunity_id": "60000000-0000-4000-8000-000000000001",
      "name": "High priority scored deal",
      "stage_id": "30000000-0000-4000-8000-000000000010",
      "stage_name": "Proposal Sent",
      "company_id": "10000000-0000-4000-8000-000000000001",
      "priority_score": 75,
      "weighted_value_usd": 160000,
      "days_in_current_stage": 0,
      "reason": "high weighted value, strong ICP fit, follow-up due this week"
    }
  ]
}
```

Metric rules:

- `pipeline_value_usd` counts active opportunities that are not in Won or Lost stages.
- `weighted_pipeline_value_usd` is `value_usd * probability / 100` for active open opportunities.
- `days_in_current_stage` is calculated from the latest stage movement into the current stage, or from `created_at` if the opportunity never moved.
- `overdue_tasks` excludes completed and cancelled tasks.
- `due_this_week_tasks` excludes completed and cancelled tasks and uses the next seven days.
- `priority_opportunities` ranks open opportunities by weighted value, ICP fit score, task urgency, and inactivity.
- `high_priority_opportunities` counts opportunities in the high score band or with the combined signals of meaningful weighted value, strong ICP fit, and urgent/inactive workflow risk.
- `inactive_opportunities` counts open opportunities that stayed in their stage for at least 14 days and have no recent activity or open task.

### Security Snapshot

```http
POST /security-scans/snapshot
Authorization: Bearer dev-technical-analyst
Content-Type: application/json
```

Valid request:

```json
{
  "domain": "https://demo.xy-cyber.example/snapshot",
  "approved": true,
  "approval_note": "Approved internal demo target.",
  "timeout_seconds": 1
}
```

Valid response shape:

```json
{
  "domain": "demo.xy-cyber.example",
  "approved": true,
  "started_at": "2026-08-12T09:00:00Z",
  "completed_at": "2026-08-12T09:00:00Z",
  "duration_ms": 2,
  "results": [
    {
      "check": "dns",
      "status": "pass",
      "summary": "Synthetic DNS result returned for demo safety.",
      "finding": false,
      "severity": "info",
      "method": "deterministic mock",
      "evidence": ["A 203.0.113.10"],
      "error_classification": null,
      "details": {
        "addresses": ["203.0.113.10"],
        "record_type": "A"
      }
    }
  ]
}
```

Validation rules:

- Request must include explicit approval.
- Domain is normalized from URL/host input to lowercase hostname.
- IP addresses, localhost, malformed hostnames, and empty domains are rejected.
- Technical Analyst, Management, and Admin can run snapshot checks.
- Business Development and Read Only cannot run snapshot checks.
- `.example` domains return deterministic mock DNS/TLS results for safe demos.
- Non-`.example` domains use bounded DNS and TLS checks with configured timeout.
- Frontend route `/security-scans` lets the user confirm scope, initiate a snapshot scan, inspect status/evidence, and filter findings by severity.
- Non-`.example` domains must be present in the server-side live scan allowlist.
- DNS results that resolve only to private, loopback, link-local, reserved, multicast, or unspecified addresses are rejected.
- TLS connects to a validated public resolved IP while preserving hostname verification with SNI.
- DNS and TLS failures are returned as structured check results instead of false positive findings.
- HTTP header, SPF, and DMARC checks are included for approved live targets and as deterministic
  mock results for `.example` domains.
- Each result includes `finding`, `severity`, `method`, `evidence`, and optional
  `error_classification` fields. A timeout, lookup failure, or HTTP request failure has
  `finding: false` and `severity: info`; it must not be represented as a security finding.
- Header observations cover Content-Security-Policy, Strict-Transport-Security,
  X-Content-Type-Options, X-Frame-Options, and Referrer-Policy. Missing controls are
  phrased as potential risks, not verified vulnerabilities.
- SPF uses a DNS TXT lookup at the submitted domain; DMARC uses DNS TXT at
  `_dmarc.{domain}`. Multiple SPF records, absent records, and monitoring-only
  DMARC (`p=none`) are severity-rated observations when the lookup completes.

## Reports

### GET /reports

Lists report records visible to the authenticated user.

### POST /reports/generate

Generates a synthetic HTML report context, creates PDF bytes, stores the file reference, and
returns a draft report record.

Allowed roles: `admin`, `management`, `technical_analyst`.

Example request:

```json
{
  "company_id": "10000000-0000-4000-8000-000000000001",
  "company_name": "Northstar Commerce Group",
  "domain": "demo.xy-cyber.example",
  "scan_summary": "Approved demo snapshot with SPF pass, DMARC monitoring, and missing CSP."
}
```

Example response:

```json
{
  "id": "90000000-0000-4000-8000-000000000001",
  "company_id": "10000000-0000-4000-8000-000000000001",
  "company_name": "Northstar Commerce Group",
  "domain": "demo.xy-cyber.example",
  "title": "Cyber Risk Snapshot - Northstar Commerce Group",
  "status": "draft",
  "storage_bucket": "reports",
  "storage_path": "reports/90000000-0000-4000-8000-000000000001.pdf",
  "download_url": null
}
```

### POST /reports/{report_id}/review

Moves a draft report to review.

Allowed roles: `admin`, `management`, `technical_analyst`.

### POST /reports/{report_id}/approve

Moves a review report to approved and exposes its download URL.

Allowed roles: `admin`, `management`.

### POST /reports/{report_id}/archive

Archives a report and removes its download URL.

Allowed roles: `admin`, `management`.

### GET /reports/{report_id}/download

Returns the approved PDF payload as base64 with filename, content type, storage bucket, and
storage path.

Allowed roles: `admin`, `management`.

Reports must be approved before download. Draft, review, and archived reports return a safe error
instead of file content.

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
- `GET /reports`: implemented with local in-memory repository.
- `POST /reports/generate`: implemented with HTML assembly, PDF bytes, and storage reference.
- `POST /reports/{id}/review`: implemented.
- `POST /reports/{id}/approve`: implemented for Admin/Management.
- `POST /reports/{id}/archive`: implemented for Admin/Management.
- `GET /reports/{id}/download`: implemented for approved reports and Admin/Management.
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
- `POST /companies/{id}/calculate-icp`: implemented with deterministic scoring and stored explanations.
- `PATCH /companies/{id}`
- `GET /contacts`: implemented with local in-memory repository.
- `POST /contacts`: implemented with local in-memory repository.
- `GET /contacts/{id}`: implemented with local in-memory repository.
- `PATCH /contacts/{id}`
- `GET /pipeline-stages`: implemented with local in-memory repository.
- `POST /pipeline-stages`: implemented for Admin/Management.
- `GET /opportunities`: implemented with local in-memory repository.
- `POST /opportunities`: implemented with weighted value calculation.
- `PATCH /opportunities/{id}`: implemented with weighted value recalculation.
- `DELETE /opportunities/{id}`: implemented as archive/soft delete.
- `PATCH /opportunities/{id}/move-stage`: implemented with stage history.
- `GET /opportunities/{id}/stage-history`: implemented.
- `GET/POST/PATCH/DELETE /activities`: implemented with local in-memory repository.
- `GET/POST/PATCH/DELETE /tasks`: implemented with local in-memory repository.
- `GET/POST/PATCH/DELETE /notes`: implemented with local in-memory repository.
- `GET /dashboard/summary`: implemented with weighted pipeline, stage duration, task, activity, and stage summary metrics.
- Dashboard summary now includes priority and inactive-opportunity workflow metrics.
- `POST /security-scans/snapshot`: implemented for approved demo DNS/TLS checks with timeout handling.
- `GET/POST /reports`: implemented for report generation, review, approval, archive, and download workflow.
