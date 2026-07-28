# Decision Log

Use this file for decisions that affect implementation, architecture, scope, dependencies, API contracts, database schema, security, or delivery evidence.

The project brief defines three decision levels:

- Green: decide independently, record briefly, continue.
- Yellow: coordinate between both interns, update affected docs/issues, continue.
- Red: supervisor approval required before the risky action.

Red examples include public deployment, real customer data, paid services, disabling RLS, live third-party scanning, deleting shared data, or changing core scope.

## Template

### YYYY-MM-DD - Decision Title

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

### 2026-07-28 - Use A Single Monorepo

- Date: 2026-07-28
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

### 2026-07-28 - Keep README And Add Private Local Work Log

- Date: 2026-07-28
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
