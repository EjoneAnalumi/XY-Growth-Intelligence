# Architecture

This document tracks the intended architecture for the XY CYBER Growth Intelligence MVP. It should stay aligned with the internship brief and the actual code.

## Goal

Build a secure internal platform that helps XY CYBER manage prospects, score opportunities, track follow-ups, analyze pipeline performance, and generate approved executive Cyber Risk Snapshot reports.

## Target Architecture

```text
Browser
  -> Next.js / TypeScript frontend
       -> Supabase Auth for user sessions
       -> FastAPI for protected business logic
            -> Supabase PostgreSQL
            -> Supabase Storage for report files
            -> Safe snapshot modules
            -> Optional Claude API feature flag after deterministic MVP works

Development
  -> GitHub monorepo
  -> Docker Compose
  -> GitHub Actions lint and test checks
```

## Component Responsibilities

- Frontend: Internal operator UI, login flow, route protection, tables, Kanban, dashboards, report preview, and user-facing workflow states.
- Supabase Auth: Login, logout, reset flow, invitation acceptance, sessions, and user identity.
- FastAPI: Protected business actions, validation, permission checks, scoring, priority logic, report orchestration, and safe snapshot execution.
- Supabase PostgreSQL: Business records, stage history, score results, scan findings, report metadata, audit events, and RLS enforcement.
- Supabase Storage: Generated report HTML/PDF files.
- Docker Compose: Local development environment before any hosted staging.
- GitHub Actions: Evidence for linting and automated tests.

## Required MVP Flow

```text
login
  -> create company
  -> create contact
  -> calculate ICP score
  -> create opportunity
  -> move pipeline stage
  -> record activity
  -> schedule follow-up
  -> dashboard updates
  -> safe snapshot on approved/mock target
  -> report draft
  -> technical review
  -> approval
  -> PDF download
  -> CSV import/export
```

## Backend Module Intent

- `api`: HTTP route modules and route-level dependencies.
- `core`: configuration, structured logging, auth helpers, error handling, and cross-cutting app setup.
- `models`: database-facing domain models or persistence abstractions when needed.
- `schemas`: Pydantic request and response schemas.
- `services`: application use cases and orchestration.
- `scoring`: deterministic ICP scoring, weighted value, priority, and recommendation rules.
- `scanning`: safe DNS, TLS, HTTP header, SPF, and DMARC checks with timeouts and mock fixtures.
- `reporting`: report assembly, HTML rendering, PDF generation, storage metadata, and status transitions.

## Minimum Data Model

The brief requires these tables when database work begins:

- `profiles`
- `companies`
- `contacts`
- `opportunities`
- `pipeline_stages`
- `activities`
- `tasks`
- `services`
- `icp_rules`
- `icp_score_results`
- `security_scans`
- `security_findings`
- `reports`
- `report_files`
- `audit_logs`

Common fields should include UUID primary keys, timestamps, creator/updater fields where meaningful, status fields where meaningful, soft deletion where practical, and indexes for foreign keys and dashboard filters.

## Authorization Model

Roles required by the brief:

- Admin
- Management
- Business Development
- Technical Analyst
- Read Only

Authorization must exist in both places:

- Supabase RLS for database access boundaries.
- FastAPI checks for protected business actions and privileged workflows.

Frontend-only authorization is not sufficient.

## Cyber Risk Snapshot Boundary

Allowed:

- DNS records and resolution.
- HTTPS availability and redirect behavior.
- TLS certificate validity and expiration.
- HTTP security headers.
- SPF and DMARC records.
- Approved public subdomain data or deterministic mock data.
- Approved demo domains and local test environments.

Not allowed:

- Credential attacks.
- Password guessing.
- Authentication bypass attempts.
- Exploit execution.
- Aggressive port scanning.
- Denial-of-service or load testing.
- Accessing non-public or restricted systems.
- Scanning a company only because it is a sales prospect.

## Current implementation

The historical foundation above has been implemented and expanded. For the verified
Day 20 runtime, persistence modes, operational ownership, configuration and remaining
brief deviations, see [architecture and operations](week4-day20-architecture-operations.md).
