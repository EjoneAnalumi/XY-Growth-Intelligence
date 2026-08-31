# Week 4 Day 19 Demo and Handover

Status: **acceptance-approved**. This script follows the actual internship brief (pp. 18-19); its required browser journey was completed successfully in the final Day 19 acceptance run.

## Deterministic 15-minute final demonstration

1. **0:00-1:00 - context and architecture.** Explain the internal prospect-to-report workflow, local Docker architecture, synthetic-data-only rule, Supabase Auth/RLS, FastAPI, Next.js, and safe snapshot boundary.
2. **1:00-3:00 - authentication and CRM.** Sign in as invited Business Development user. Create a synthetic company and contact; show search/filter, timeline, and role-specific navigation.
3. **3:00-5:00 - ICP and recommendation.** Calculate the configurable deterministic ICP score. Explain rule contributions, stored result, primary/secondary service recommendation, next step, owner, and due action.
4. **5:00-7:00 - pipeline and follow-through.** Create an opportunity, show weighted value, move it in Kanban, inspect retained stage history, record a meeting/activity, add a follow-up task, and show staff attribution.
5. **7:00-9:00 - management visibility.** Show verified dashboard KPIs/panels: pipeline/weighted pipeline, forecast, activity, overdue work, inactive opportunities, and priority actions. Compare a known value to the seeded-data calculation.
6. **9:00-12:00 - safe snapshot.** Use only an approved mock/demo domain. Confirm scope, run DNS/TLS/HTTPS header/SPF/DMARC checks, show evidence and errors separately, explain the cautious language and no-exploitation boundary.
7. **12:00-14:00 - report workflow.** Generate the branded report, show required sections and disclaimer, move Draft -> Technical Review -> Approved, show permission denial for an unauthorized role, then download the stored PDF. Do not send or externally share it.
8. **14:00-15:00 - quality and handover.** Show automated results, migration/RLS evidence, README setup, known limitations, and prioritized next-phase backlog.

## Role checks to demonstrate

- **Admin:** invite users, manage roles; demonstrate that public signup is unavailable.
- **Business Development:** create CRM work; cannot administer users or perform admin-only configuration/snapshot actions.
- **Technical Analyst:** run safe snapshot and review report; cannot perform restricted sales/admin actions.
- **Management:** approve report and manage pipeline policy as permitted.
- **Read Only:** can view allowed records; mutation returns a clear error and leaves data unchanged.

## Setup and test handover

Use the ordered Windows commands in `README.md`: create ignored `.env` from `.env.example`; start local Supabase; reset database; load generated local values only into the active shell; start backend with `AUTH_MODE=supabase`; start frontend; then shut down with the documented commands. Do not expose a service-role key to `NEXT_PUBLIC_*` variables.

Required acceptance retest commands and their current status are in `docs/week4-day19-acceptance-evidence.md`. The local reset, backend gates, frontend build, component tests, and responsive Playwright suite have concrete evidence; a receiving developer must execute the full demonstration above and retain the live Auth/UI evidence.

## Handover contents and current gaps

Available: README, architecture, API contract, decision log, migrations/policies/seed, sample CSV data, test suites, this demo script, and Day 19 evidence.

The deterministic seed includes the brief-required five reports and five scans, with complete report-workflow and scan-finding status coverage. Frontend build, component tests, responsive Playwright, Docker/Supabase startup, clean seed reset, and live Auth/session/browser acceptance are verified. See the acceptance evidence for the exact results.

## Prioritized next-phase backlog

| Priority | Item | Effort |
| --- | --- | --- |
| High | Run and retain the complete live Auth and full-business-flow screenshot acceptance evidence on a browser-enabled local environment. | Medium |
| High | Perform a clean-machine README-only installation and resolve every ambiguous setup step. | Medium |
| Medium | Replace the local Supabase image-download/startup workaround with a documented, reproducible Docker image cache/update procedure. | Small |
| Medium | Add retained user-guide screenshots and accessibility evidence for each mandatory workflow. | Medium |
| Low | Review and remediate frontend dependency-audit findings in a separately scoped dependency-hardening change. | Medium |

## Exact local manual actions

```powershell
Set-Location <repository-root>
npx.cmd --yes supabase@2.115.0 start --ignore-health-check
npx.cmd --yes supabase@2.115.0 status
```

After the Auth container is healthy, use the generated local values from `status` only in the active shell, start the backend and frontend as documented in `README.md`, and execute the 15-minute script above. Capture the terminal output and screenshots/recording as the final acceptance evidence.
