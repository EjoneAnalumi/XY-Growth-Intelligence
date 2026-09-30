# Week 4 Day 20 Operator Guide and Final Demonstration

Date: 30-09-2026
Branch: `feature/week4-day20-mvp-completion`

## Before the demonstration

Follow the root README with local Supabase, all migrations, SQL seed and report bootstrap.
Open `http://localhost:3000/login`. Use only the existing local synthetic accounts from the
seed migration. Keep credentials and tokens out of recordings. The demo never scans a
third-party domain, sends an email externally, or deploys publicly.

## Fifteen-minute demonstration / presentation

| Time | Operator action | Explain / verify |
| --- | --- | --- |
| 0?1 min | Show architecture and problem | One internal prospect-to-report workflow; Python API, Supabase Auth/RLS/Storage, Next.js |
| 1?3 min | Sign in as Business Development; Companies ? Add Company; Contacts ? Add Contact | Fictional name and `.example` domain; link contact to company; refresh to confirm persistence |
| 3?5 min | Select company in ICP Score Breakdown ? Calculate | Explain stored rule contributions, service recommendation and next step |
| 5?7 min | Opportunities ? New Opportunity; set value/probability; move in Kanban; Details ? Record activity / Schedule task | EUR 10,000 ? 50% = EUR 5,000 before stage change; stage movement may replace probability with stage default; show history and attribution |
| 7?9 min | Dashboard | Compare before/after pipeline +10,000, activity +1, overdue task +1; show priority and follow-up panels |
| 9?12 min | Sign out; sign in as Management or Technical Analyst; Security Scans ? confirm synthetic scope ? Run snapshot scan | Findings, evidence and failed checks are distinct; only approved mock target |
| 12?14 min | Generate report from scan; Review; Management approves; Download | Inspect required report sections, cautious exposure heuristic, private stored PDF; demonstrate Read Only denial |
| 14?15 min | Companies ? Import CSV / Export CSV; show tests and handover | Use a unique fictional row for import; duplicate import is rejected; disclose limitations and next-phase backlog |

From Reports, Create report from a snapshot runs the scan and creates/opens a draft.
Standalone scans provide Create report from this snapshot. Scan/report dates use local time.

Technical Analyst can generate/submit for review; Admin or Management approves/downloads.
Shared is an internal tracking status required by the brief; it sends no email. PDF download currently requires Approved status. Admin/Management can archive any active report directly.
Never represent the synthetic workflow approval as a real security assessment approval.

## Operator reference

- Company/contact Edit updates a record; Archive requires confirmation and preserves history.
- Opportunity Details contains activity, task and staff-note forms, plus stage history.
- Use Tasks or opportunity Details to schedule an overdue task and see the dashboard count change; Mark complete removes it from open work.
- Company CSV accepts UTF-8, the exported header set and pipe-delimited list values. Use the sample file as a format reference; do not reimport existing seed names/domains.
- On an API error, inspect the displayed message, verify both local services and the active account role, then retry. Never disable RLS to resolve a permission error.
- Admin Users provides invitation and account management; no public registration is intended.

## Retained demonstration artifacts

Artifacts are in [week4-day20-artifacts](week4-day20-artifacts/). Screenshots contain
synthetic data only. The live Playwright test uses actual Auth and API calls; it does not
route/mock network responses. Responsive tests use separate deterministic mock fixtures.

1. [Login](week4-day20-artifacts/01-login.png)
2. [Company and ICP](week4-day20-artifacts/02-company-icp.png)
3. [Opportunity history and follow-up](week4-day20-artifacts/03-opportunity-history-follow-up.png)
4. [Dashboard](week4-day20-artifacts/04-dashboard.png)
5. [Snapshot evidence](week4-day20-artifacts/05-snapshot.png)
6. [Approved report](week4-day20-artifacts/06-approved-report.png)
7. [Read Only permissions](week4-day20-artifacts/07-read-only-permissions.png)
8. [Downloaded synthetic PDF](week4-day20-artifacts/approved-synthetic-report.pdf)
9. [Dashboard before/after API comparison](week4-day20-artifacts/dashboard-comparison.json)
10. [CSV workflow](week4-day20-artifacts/08-csv.png) and [exported synthetic CSV](week4-day20-artifacts/synthetic-companies.csv)

## Receiver acceptance

The receiver should run this script from the tagged source on a fresh clone, retain its
own installation evidence, and review the latest submission readiness record. Supervisor
sign-off and organizational repository ownership transfer remain receiver actions.
