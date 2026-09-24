# Decision Log

Use this file for decisions that affect implementation, architecture, scope, dependencies, API contracts, database schema, security, or delivery evidence.

The project brief defines three decision levels:

- Green: decide independently, record briefly, continue.
- Yellow: coordinate between both interns, update affected docs/issues, continue.
- Red: supervisor approval required before the risky action.

Red examples include public deployment, real customer data, paid services, disabling RLS, live third-party scanning, deleting shared data, or changing core scope.

## Template

### DD-MM-YYYY - Decision Title

- Date:
- Decision owner:
- Decision level: Green | Yellow | Red
- Status: Proposed | Accepted | Superseded
- Problem:
- Options considered:
- Decision:
- Reason:
- Affected files or APIs:
- Rollback approach:
- Supervisor approval required: Yes | No

## Blocker Template

- Issue:
- Expected behavior:
- Actual behavior:
- Smallest reproduction:
- Exact error/log:
- Attempts made:
- AI or documentation consulted:
- Time spent:
- Safe task switched to:
- Supervisor decision required: Yes | No

## Decisions

### 28-07-2026 - Use A Single Monorepo

- Date: 28-07-2026
- Decision owner: Project team
- Decision level: Green
- Status: Accepted
- Problem: The project combines backend, frontend, database, docs, and sample data for a one-month internship MVP.
- Options considered: Single monorepo; separate backend and frontend repositories.
- Decision: Keep all project code and documentation in one repository.
- Reason: The brief requires a single monorepo and the team is small, so cross-layer changes should be reviewed together.
- Affected files or APIs: Repository layout.
- Rollback approach: Not planned; this is a project requirement.
- Supervisor approval required: No

### 28-07-2026 - Keep README And Add Private Local Work Log

- Date: 28-07-2026
- Decision owner: Codex support
- Decision level: Green
- Status: Accepted
- Problem: The intern needs detailed private explanations, but the brief also requires a README for handover.
- Options considered: Delete README; keep README only; keep README and add an ignored local log.
- Decision: Keep `README.md` as the public handover document and create ignored `LOCAL_WORK_LOG.md` for private intern notes.
- Reason: This preserves the final handover requirement while keeping personal learning notes out of Git.
- Affected files or APIs: `.gitignore`, `README.md`, `LOCAL_WORK_LOG.md`.
- Rollback approach: Remove local log and rely only on shared docs if the team wants all notes public.
- Supervisor approval required: No

### 29-07-2026 - Use Brief Roles For Week 1 RLS

- Date: 29-07-2026
- Decision owner: Backend and Data Owner
- Decision level: Green
- Status: Accepted
- Problem: The first database draft used generic `admin` and `member` roles, which did not match the project brief and made RLS too permissive.
- Options considered: Keep `admin/member`; use the five roles from the brief.
- Decision: Use `admin`, `management`, `business_development`, `technical_analyst`, and `read_only` in `profiles.role`.
- Reason: The brief explicitly requires those roles and Read Only users must not be able to create or update business records.
- Affected files or APIs: `database/migrations/20260729000001_initial_schema.sql`, `database/policies/week1-rls.md`.
- Rollback approach: Replace role constraint and RLS helper checks in a follow-up migration if the supervisor changes the role model.
- Supervisor approval required: No

### 24-09-2026 - Correct Day 19 acceptance and package the internship MVP

- Decision owner: backend/data and frontend/product maintainers (review required).
- Decision level: Yellow; requested by the repository owner in the Day 20 task.
- Decision: retain PR #30 history in the Day 20 branch; replace placeholder report SQL
  with local-only real PDF bootstrap, add required report sections, live evidence and frontend CI.
- Reason: row counts cannot demonstrate downloadable reports, and partial evidence must
  not be presented as complete acceptance. Repeated seeding must preserve workflow states.
- API impact: no public request/response shape changed. Exposure indicator is explicitly
  a synthetic report triage heuristic, not a validated security risk rating.
- Rollback: revert the feature commits; keep private report objects and existing CRM data.
- Supervisor approval required: no for local synthetic work; yes before hosted deployment.
- Release: versioned internship prerelease with explicit functional gaps and human review pending.
