# Week 4 Day 20 Handover Evidence and Status

Date: 24-09-2026
Branch: `feature/week4-day20-final-handover`
Baseline: fetched `origin/main` at `9621379`; incorporates colleague PR #30 at `15f51f1`.
Release tag: `v0.1.0-internship.1` (local synthetic MVP prerelease).

## Exact scope and outcome

Review and correct Day 19 acceptance defects, demonstrate the core local workflow, and
prepare a tagged Day 20 handover with retrospective, known limitations and prioritized
next-phase backlog. The work preserves PR #30's authorship. No changes are committed to main.

Day 20's handover materials and the demonstrated core flow are delivered. Full conformance
to every detailed brief requirement remains partial: see the explicit P1 functional gaps
in [the backlog](week4-day20-limitations-backlog.md). Supervisor acceptance, actual repository
ownership transfer and a fresh installation of the final tag remain receiver actions.

## Implemented changes

- `backend/app/seed_reports.py`: loopback-only synthetic report bootstrap; creates five
  real private PDF objects through the normal generator/workflow; upgrades only exact
  file-less Day 19 placeholders; verifies existing PDFs and preserves completed states.
- `database/seed/seed.sql`: retains deterministic scans/findings; removes non-downloadable
  placeholder report rows and unconditional status rewinds. Report upload is an explicit second step.
- `backend/app/services/report_repository.py`: optional internal fixed report ID for repeatable
  seed generation. Public API fields and permissions are unchanged.
- `backend/app/reporting/assembly.py`: required posture, asset, impact, actions, service and
  next-engagement sections; severity order and transparent synthetic exposure heuristic.
- `backend/tests/test_seed_reports.py` and `test_report_content.py`: repeated seed/PDF retrieval,
  local-target guard, escaping, required content and PDF-conversion regression checks.
- `frontend/tests/live/handover.spec.ts`: real Supabase login and browser sales-to-report/CSV
  journeys; no API mocking; screenshots/PDF and numeric API comparison retained.
- `frontend/components/companies/icp-score-panel.tsx`: accessible label for company selection.
- Playwright configs: separate opt-in live suite, portable npm command and installed-browser option.
- `.github/workflows/ci.yml`: frontend typecheck, lint, Vitest and production build.
- README/database guide: document the report bootstrap and portable setup; handover docs
  include architecture, operations, demonstration/user guide, retrospective and release notes.
- Day 19 evidence: correct overstated closure, fix filename/date conventions and preserve historical results.

## Verification

Python 3.12.6; local Docker/Supabase PostgreSQL and private Storage; actual Auth sessions for
browser tests. Frontend local runtime was Node 26.3.0; CI targets Node 22 LTS.

| Command / check | Result |
| --- | --- |
| Backend: `python -m pytest -q -p no:cacheprovider` with local Supabase variables and `AUTH_MODE=local` | 112 passed, no skips; full database/RLS/Storage gate |
| Backend: `python -m pytest` without injected Storage configuration | 105 passed, 7 skipped; local RLS tests available, remaining integration cases run in full gate above |
| Backend: `python -m ruff check .` | All checks passed |
| `python -m app.seed_reports` | Five actual PDF objects verified; repeat run and two SQL seed executions pass |
| Frontend: `npm.cmd run typecheck` | Passed |
| Frontend: `npm.cmd run lint` | Passed, no ESLint warnings/errors |
| Frontend: `npm.cmd test` | 7 files, 19 tests passed |
| Frontend: `npm.cmd run build` | Passed, 16 routes generated (final rerun passed before release) |
| `PLAYWRIGHT_CHANNEL=msedge npm.cmd run test:responsive` | 9 passed; mobile/tablet/desktop |
| `PLAYWRIGHT_CHANNEL=chrome npx.cmd playwright test --config playwright.live.config.ts` | 2 passed; real-session core workflow and company CSV |
| Downloaded PDF inspected with pypdf | 2 pages; required posture/impact/actions/asset sections present |
| `git diff --check` | Passed |

Generated local connection values were supplied only in process memory. The backend
integration gate deliberately uses synthetic test-role tokens; real Auth is separately
exercised in the live browser run. Do not confuse those two forms of evidence.

The in-app browser connector timed out twice; installed Chrome was used for live browser
acceptance. Edge passed responsive tests but produced a teardown error after download
flows, so those runs were not counted as a passing live gate. Chrome completed with exit
code zero. Concurrent Next.js test/dev servers initially caused stale chunks; final runs
were sequential. No failed attempt was silently recorded as a pass.

## Demonstrated acceptance and retained artifacts

See [operator guide and screenshots](week4-day20-demo-user-guide.md) and
[artifact directory](week4-day20-artifacts/). The actual browser test proves:

- Business Development login; synthetic company/contact creation; ICP calculation.
- Opportunity creation and stage movement; activity and overdue follow-up creation.
- Dashboard pipeline, activity and overdue deltas independently asserted against API results.
- Logout; Management login; approved mock scan; draft ? review ? approved report.
- Actual private PDF download and branded HTML preview.
- Read Only login; company mutation denied with 403 and download control disabled.
- CSV import of one unique fictional company and CSV export through the UI.

The test adds uniquely named synthetic records and preserves existing local data. Screenshots
show the resulting local dataset, not an assertion that the entire database is pristine.
SQL reseed regression checks roll back their CRM updates. No full database reset was run.

## Security and limitations

No real prospect/customer data, hosted secrets, API keys or service-role values were added.
No public deployment, external report sending, live third-party scan or RLS disabling occurred.
Live browser traces are disabled to avoid retaining bearer tokens; committed evidence is
limited to synthetic screenshots, CSV, dashboard values and the downloaded synthetic PDF.
Report seeding accepts only loopback destinations and APP_ENV=local. Private Storage remains private.

The exposure indicator is explicitly a synthetic heuristic; errors/timeouts mean unknown
coverage. The lightweight PDF renderer retains content but does not reproduce HTML CSS.
Required unfinished administration/analytics/profile/task/CSV breadth is documented rather
than claimed complete. Invitation/reset/session-expiry browser evidence and independent
receiver sign-off are still pending. Historical Day 18/19 clean-install records are retained;
they are not presented as a fresh clean-machine test of this final revision.

## Transfer checklist

- Review combined PR, including colleague Day 19 commits and these corrections.
- Check out the immutable tag and follow root README on the receiving environment.
- Assign backend/data and frontend/product maintainers and reviewers.
- Provide receiver-owned local configuration outside Git; never transfer secrets in the PR.
- Run the demonstration and review the P1 backlog before supervisor acceptance.
- Merge only after human review; transfer GitHub ownership through the account owners.
