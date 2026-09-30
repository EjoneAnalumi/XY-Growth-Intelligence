# Week 4 Day 20 Review Follow-up

Date: 29-09-2026
Branch: `feature/week4-day20-mvp-completion`
Baseline: continues the uncommitted completion branch based on `origin/main` at `f11bd7e`.
Status: implemented and locally verified; awaiting author review before commits.

## Requested scope

Use EUR throughout; remove Read Only users from task assignment; clean up local test tasks
and the temporary invitation account; default to newest-first sorting; personalize the task
list; add persistent unread assignment/note counts and deadline reminders; clarify report
preview, sorting, hiding and workflow actions; clarify Technical Analyst responsibilities.

## Changes

| Area and files | Behavior |
| --- | --- |
| Backend company/opportunity/dashboard schemas, scoring/repositories, frontend API clients/types/currency formatters, seed SQL, API contract | `annual_revenue_eur`, `value_eur`, `weighted_value_eur` and dashboard monetary fields use EUR. Opportunity CSV exports use `value_eur`. |
| `20260928000002_review_usability.sql` mirrored migrations | Defines EUR monetary fields, assignment provenance, per-user read receipts with RLS, and the report archive transition. |
| `20260929000001_clear_ineligible_task_owners.sql` mirrored migrations | Retains tasks but clears existing Read Only/inactive assignments. |
| `backend/app/api/tasks.py`, `services/task_assignment.py`, task schema/repositories | Server checks require an active non-Read-Only assignee; omitted owner means creator, explicit null means unassigned. Records assignment actor/time and refreshes those on reassignment. Analysts can change only status/outcome on their own assigned tasks. |
| `backend/app/api/inbox.py`, frontend inbox client and app shell | Persistent per-user unread task/note IDs, sidebar count badges, overdue/24-hour deadline counts. Counts refresh on navigation, focus and explicit actions; no push, polling timer or external notifications. |
| Tasks page | Default: current user's open tasks, then unassigned tasks; others via owner filter. Newest first within each group; oldest, A-Z, Z-A and earliest due date also available. Overdue dates come first in due-date order; undated tasks come last. Shows assignment actor, recipient and creation time. Mark seen acknowledges an assignment. |
| Company/contact API clients/types and `record-list-controls.tsx` | Creation timestamp is preserved and defaults to newest-first. Oldest-first and A-Z/Z-A remain available with search and pagination. |
| Notes API and page | Shared team notes, newest-first by default, alternate sorting and unread-only filter. Each user can mark a note read independently; own notes are not unread. Editing a shared note makes it unread again for other users. Analysts may create notes and edit/archive only their own notes. |
| Reports page and repository/workflow migration | Explicit status explanations, actions shown only when relevant, success/error feedback, newest-first/A-Z/Z-A sorting, search/status filter, archived hidden by default. Preview identifies and focuses the selected report. Hide reports collapses the list without changing data. Admin/Management may archive Draft, Review, Approved or Shared directly. |
| Tests | EUR CSV/weighted-value checks; task assignment restrictions and analyst ownership; receipt isolation/reassignment; report archival from multiple states; RLS cross-user denial; sorting, preview selection and list collapsing; real Supabase browser acceptance. |

## Role boundaries

- Admin/Management retain report approval, download and archive authority.
- Technical Analyst: approved snapshot checks, report drafts/submission for review, completion
  and outcomes for assigned tasks, and authoring their own shared notes. Sales data/configuration
  writes and report approval remain unavailable.
- Read Only: view records and acknowledge their own note reads; cannot receive tasks or mutate
  business records. The backend enforces these restrictions in addition to UI controls.
- Staff Notes are shared team context, not private recipient-addressed messages. Unread state is
  personal. Task counts include open/in-progress assignments, excluding completed/cancelled ones.

## Local cleanup

Removed the temporary `Synthetic Invitation Acceptance` authentication account after verifying
its exact fixture name and reserved email pattern. Invitation acceptance itself remains because
it is a required authentication flow; only the test account was unnecessary after verification.

Initially archived 38 verified seed/test task entries from the local active list. Selection combined exact
fixture titles, seed UUID prefixes, synthetic creator IDs and linked handover demo domains.
`Research` and `Confirm scope call` were retained. Soft archive preserves recoverability and
the 25-task seed fixture required for a fresh installation remains in source control.
No database reset or blanket task deletion was performed. The new browser acceptance test
archives only its own temporary tasks/notes after verification; invitation testing removes its
temporary account. Any fixtures from the older acceptance suite are cleaned after the final run.
The final run added five more task fixtures; those were also archived, for 43 removed from
the active list in total. A single company from a failed test setup was archived by its exact
fixture name/domain. The final invitation run removed its own account.

For an existing local installation, apply migrations with
`npx.cmd --yes supabase@2.115.0 migration up --local`, then start the updated services using
the root README or `scripts/start-local.ps1`. Do not run a database reset to apply this update.

## Checks and evidence

| Check | Result |
| --- | --- |
| `cd backend; python -m pytest -q --tb=line -p no:cacheprovider` with local Supabase environment | 136 passed, no skips, 19.64 seconds |
| `cd backend; python -m ruff check .` | All checks passed |
| `cd frontend; npm.cmd run typecheck` | Passed |
| `cd frontend; npm.cmd test` | 9 files, 26 tests passed |
| `cd frontend; npm.cmd run lint` | No ESLint warnings/errors |
| `cd frontend; npm.cmd run build` | Production build passed |
| `npx.cmd playwright test review-usability.spec.ts --config playwright.live.config.ts` with local synthetic credentials | 1 passed, 32.3 seconds; real Auth/database/Storage, not mocked APIs |
| `npx.cmd playwright test --config playwright.live.config.ts` with local synthetic credentials | All 6 passed, 2.2 minutes; includes the original sales-to-approved-PDF flow and invitation/recovery |
| Focused browser rerun after final display-text corrections | 1 passed, 32.6 seconds; final screenshots refreshed and visually checked |

Backend output includes existing upstream Starlette deprecation warnings. Frontend tooling
prints existing Vite/Node notices and the Next 15 lint-command deprecation notice.
Visual evidence is saved under `docs/week4-day20-review-artifacts/` after final inspection.
Final service checks returned backend `{"status":"ok"}` and frontend login HTTP 200.
The read-only fixture check found zero remaining active task fixtures and zero temporary
invitation accounts. Backend and frontend are left running for author review.

## Security and remaining steps

All data used in testing is synthetic. No credential, token, hosted key, or new external
service was added. Read receipts are scoped to the authenticated user; cross-user and anonymous
access are tested. Assignment eligibility is checked in the API and on database owner changes.
The API remains the trusted path for analyst task/note writes; direct database write privileges
were not broadened. Download still requires Approved status and Admin/Management; archiving
does not approve a report or expose its stored PDF.

API consumers and CSV templates use the documented EUR field names. Apply all migrations
before starting the backend.

The work remains uncommitted for the requested hands-on review. User acceptance, logical commits,
push/PR and independent supervisor acceptance remain pending. Public deployment is outside this
follow-up. No live notification infrastructure or private messaging system was introduced.
