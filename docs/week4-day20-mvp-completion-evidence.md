# Week 4 Day 20 MVP Completion Evidence

Date: 28-09-2026
Branch: `feature/week4-day20-mvp-completion`
Baseline: fetched `origin/main`, commit `f11bd7e`; no direct main changes.
Status: implemented and locally verified; pending author review before commits and PR.

## Scope

Re-read the internship project brief and inspect the current monorepo, then close the
functional gaps recorded in the previous Day 20 handover. This is a local synthetic MVP
completion task. It does not claim supervisor acceptance or production readiness.
Earlier dated evidence and the existing release tag remain historical records.

## Implementation and file map

| Area | Files | Result |
| --- | --- | --- |
| Profiles | `backend/app/schemas/{companies,contacts}.py`, matching API modules, `api/profiles.py`, `frontend/components/record-profile.tsx`, company/contact `[id]` routes | Editable intelligence and follow-up fields, company owner/strategic importance, stored ICP explanation, linked records and chronological relationship timeline |
| Lists | `frontend/lib/api/pagination.ts`, company/contact API clients, `components/record-list-controls.tsx`, list pages/cards | Fetch all API pages, text search, alphabetical sort, 20-record display pages and profile links |
| Tasks | `backend/app/api/tasks.py`, pipeline repository, frontend task API/types and `/tasks` | Standalone create/list/filter, owner, due date, priority, completion outcome and stable completion timestamp; reopening clears timestamp |
| Administration | `backend/app/api/administration.py`, `services/administration.py`, frontend `/administration`, opportunity form | Admin-only ICP/service writes, staff reads, stage editing, service suggestions, user/audit navigation |
| Scoring/recommendations | `backend/app/scoring/icp.py`, `services/recommendations.py`, companies API, ICP panel | Stored weights drive deterministic Python scoring; backend recommendations use stored score signals and active service catalogue |
| Analytics | `backend/app/services/analytics.py`, dashboard API, bulk history repository methods, `frontend/components/management-analytics.tsx` | Country/industry/service/owner/source groups, monthly forecast, ICP distribution, win/loss, stage conversion/duration, due tasks, meetings, proposals, missing actions, recent activity and reports |
| Priority | `services/priority_context.py`, pipeline repositories, dashboard schemas/API/types/page | Adds engagement, expected close, stage, strategic importance and approved snapshot observations; shows owner, action and due date |
| CSV | `backend/app/api/data_exchange.py`, frontend `/data` | Contact/opportunity/activity/task CSV import/export alongside existing company CSV |
| PDF | `backend/app/reporting/{assembly,pdf}.py` | Actual HTML-to-PDF conversion, print CSS, XY branding, embedded fonts and accented Latin text; denies remote/arbitrary local resources |
| Security/dependencies | backend config/errors/requirements, frontend package/lock/config/auth | Rejects development auth outside local environment, safe validation details, patched dependencies, role preservation on token refresh |
| Database | mirrored `20260928000001_service_catalogue.sql` migrations | Company strategic importance 0–5, service catalogue with RLS and seven synthetic catalogue entries |
| Tests | backend completion/report/dashboard/RLS tests; frontend completion/auth tests and `tests/live/completion.spec.ts` | Business-rule, role, CSV, PDF, pagination, token-refresh and live acceptance regressions |

## Verified behavior

- Changes to ICP weights require all eight positive integer weights to sum to 100.
  Each original rule contribution scales to its new maximum. Existing stored scores
  retain their explanation; recalculate explicitly after changing inputs or weights.
- Service names are suggestions and opportunities retain free-text service compatibility.
  Deactivating a catalogue item removes it from new recommendations.
- Priority is capped at 100: existing weighted-value/ICP/task/inactivity points plus
  up to 5 strategic points and 5 each for recent engagement, closing within 30 days,
  late stage and approved medium-or-higher snapshot observations. Observations are
  not presented as verified vulnerabilities. The next open task supplies the action,
  owner and due date, falling back to the opportunity.
- Analytics use non-archived records. Open pipeline excludes Won/Lost. Win rate is
  won / (won + lost). Forecast uses expected close month and explicitly includes
  unscheduled deals. Trend uses currently closed deals' latest closing-stage entry.
  Stage duration measures current occupants, not historical dwell-time averages.
  Stage conversion counts distinct deals with a forward recorded transition, excluding Lost.
- CSV is append-only, at most 1 MB / 1,000 rows. All rows and relationships validate
  before writes; PostgreSQL inserts commit atomically. Imported records belong to the
  importer. Exports omit record IDs/ownership; reimport creates new records, not updates.
  Linked company/contact/opportunity/stage IDs must already exist. Channels use `|`.
  Spreadsheet formula prefixes are escaped on export.

## Validation

Python 3.12, local Supabase PostgreSQL/Auth/private Storage and Chrome were used.
Local CLI values were passed through process environment variables without printing them.
The existing local database was preserved; no destructive reset was performed.

| Command / check | Result |
| --- | --- |
| `cd backend; python -m pytest -q -p no:cacheprovider` with local Supabase test environment | **128 passed, no skips**, 17.17 seconds; 10 upstream Starlette deprecation warnings |
| `cd backend; python -m ruff check .` | All checks passed |
| `cd frontend; npm.cmd run typecheck` | Passed |
| `cd frontend; npm.cmd run lint` | No ESLint warnings or errors; Next 15 notes future CLI deprecation |
| `cd frontend; npm.cmd run build` | Next 15.5.26 production build passed, 19 generated pages plus dynamic profile/detail routes |
| `cd frontend; npm.cmd test` | 8 files, **23 tests passed** |
| `cd frontend; npx.cmd playwright test --config playwright.live.config.ts` with local synthetic `DEMO_PASSWORD` and `PLAYWRIGHT_CHANNEL=chrome` | **5 passed**, 1.5 minutes |
| `cd frontend; npm.cmd audit` | 0 vulnerabilities |
| `cd backend; python -m pip_audit -r requirements-dev.txt --timeout 60` (audit utility installed separately) | No known vulnerabilities found |
| `git diff --check` | No whitespace errors |
| `docker build -t xy-growth-intelligence:completion-check backend` | Passed using `python:3.12-slim` and a clean dependency install |
| `docker run --rm --network none xy-growth-intelligence:completion-check ...` (calls `render_pdf_bytes` with synthetic HTML and asserts PDF signature) | Offline container PDF smoke passed, 41,826 bytes |
| `cd backend; python -m pytest tests/test_report_content.py -q -p no:cacheprovider` after metadata-label spacing adjustment | 4 passed; Ruff also passed |

The live browser suite covers profile persistence, ICP/recommendations, standalone task
completion, CSV import/export, dashboard panels, configuration saves, all five roles,
real token refresh, invitation acceptance, Mailpit password recovery and invalid-session
sign-out. The existing end-to-end flow additionally covers company/contact/opportunity,
stage move, activity, overdue task, snapshot, report review/approval and private PDF download.
Screenshots contain synthetic records only; no tokens or credentials are retained.

See [completion artifacts](week4-day20-completion-artifacts/) for profile/task/analytics/admin,
invitation/recovery/session screenshots and the approved synthetic PDF. The four PDF pages
were visually inspected for readable text, required sections and branding. Print layout
intentionally differs from the screen preview; findings may continue across page boundaries.

## Run and review

Follow the root README environment setup. Existing installations apply the additive migration
with `npx.cmd --yes supabase@2.115.0 migration up --local`; do not reset a working database.
Install updated backend requirements and run `npm.cmd ci` in `frontend` after updating.
Start with `scripts/start-local.ps1`, or run the API and frontend manually as documented.

1. Sign in as the local synthetic Admin; open Administration and review weights/services/stages.
2. Open Companies, choose Profile, edit intelligence, then calculate ICP on the company list.
3. Open Tasks, create a due task, filter it and complete it with an outcome.
4. Inspect management analytics and the priority owner/action/due fields.
5. Use Data exchange with synthetic CSV; review an approved report and download its PDF.
6. Sign in as Read Only and confirm write controls/actions are unavailable.

## Security and remaining work

- Synthetic data only. No real prospect records, hosted keys, credentials or service-role
  values were added. Local testing retained private Storage and real Supabase sessions.
- Service/ICP writes require Admin in the API. Direct authenticated service writes are denied
  by database privileges/RLS; anonymous reads are denied. Backend database access remains a
  trusted server boundary, so API authorization is also covered by tests.
- The PDF renderer only resolves its two bundled font resources. Snapshot mocks and the
  existing target allowlist remain in place; no external target scans were performed.
- Search/pagination operate on all loaded records and analytics load the small MVP dataset.
  Large-data server filtering/aggregation and cursor pagination remain future scalability work.
- Embedded Vera supports tested accented Latin names; comprehensive CJK/RTL typography needs
  additional fonts and layout testing. Existing stored PDFs are preserved, not silently replaced.
- Independent author/supervisor acceptance, repository transfer and any final release tag are
  pending. A fresh recipient-machine install and scheduled full Supabase integration CI remain
  follow-up checks; passing this local suite does not claim those were completed.
- Dependency audits are point-in-time results, not a guarantee that software has no flaws.
- Changes remain uncommitted for the requested author review. Planned commit groups are
  implementation, tests, database catalogue/migration, and documentation/evidence.
