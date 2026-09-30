# Week 4 Day 20 - Report guidance and CRM creation details

Date: 29-09-2026
Branch: `feature/week4-day20-mvp-completion`

## Scope

Match report instructions and controls to the signed-in role; display company/contact
creation dates and times; remove confirmed browser-test leftovers and prevent recurrence.

## Changes

- `frontend/app/(protected)/reports/page.tsx`: role-aware page and status guidance.
  Admin/Management retain preparation, submission, approval, approved PDF download,
  sharing and archive actions. Technical Analyst can prepare/submit and preview.
  Business Development and Read Only see preview guidance and no Download button.
  Download controls for Admin/Management explain the existing Approved-only requirement.
  No backend permissions were expanded.
- Company/contact card components and their list pages: visible Created timestamp,
  formatted like Staff Notes in the browser's local timezone; semantic time value and
  no author label. Existing newest-first sorting remains intact.
- `frontend/tests/review-usability.test.tsx`: all five report roles plus visible CRM dates.
- `frontend/tests/live/fixture-cleanup.ts`: automatic local-only teardown for the existing
  handover/completion tests, including assertion failures. It snapshots record IDs,
  paginates companies/contacts, and archives only newly created known test fixtures.
- Handover browser assertions verify BD preview-only controls and creation timestamps.

## Fixture cleanup and security

The reported names exactly matched the handover acceptance test's generated input.
Ordinary application navigation does not generate these records. Earlier browser tests
created them and omitted cleanup. A local-only cleanup matched the company name's exact
numeric suffix to its domain and checked the demo BD creator; linked contacts also had
to match the Synthetic Reviewer name, test email pattern and demo creator.

16 confirmed test companies and 8 linked test contacts were soft-archived from active
lists. Unrelated/user-created records and required baseline seed data were preserved.
No secret values or private data are included in this evidence. No production system
was accessed. Fixture cleanup is test code, not an application button or background job.

## Validation and remaining steps

- `cd frontend; npm.cmd test`: 9 files, 39 tests passed.
- `npm.cmd run typecheck`: passed.
- `npm.cmd run lint`: no warnings/errors (existing Next lint deprecation notice only).

- `npm.cmd run build` with existing local public Auth settings: passed.
- Browser handover/completion run: 4 passed; invitation scenario initially failed only
  in teardown after sign-out invalidated cleanup's setup session. Cleanup now obtains
  a fresh session. Focused invitation/recovery rerun: 1 passed, 22.6 seconds.
- Real browser coverage confirms BD has preview-only controls, both CRM cards show
  timestamps, approved PDF download still works for Management, and CSV import/export
  succeeds with automatic cleanup.
- Read-only database verification after the CRM tests: zero active matched test
  companies and zero linked test contacts. `git diff --check`: passed.
- Frontend login returns HTTP 200; backend health returns OK. Both servers remain up.

No backend/API/business logic changed. Changes remain uncommitted pending hands-on review, followed by
logical commits, push and PR. The local app remains the review target.
