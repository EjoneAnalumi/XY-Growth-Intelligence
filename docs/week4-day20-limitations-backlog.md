# Week 4 Day 20 Known Limitations and Next-Phase Backlog

Date: 24-09-2026
Branch: `feature/week4-day20-final-handover`

This register distinguishes unfinished brief requirements from future production work.
Passing the demonstrated core workflow does not mean every detailed brief item is implemented.

| Priority | Gap / next action | Owner | Effort | Acceptance |
| --- | --- | --- | --- | --- |
| P1 | Complete administration UI for stages, services, configurable ICP rules and audit events; Users UI exists | Both | Large | Authorized editing and audit browsing, denial tests |
| P1 | Expand analytics beyond current stage summaries/priority/follow-up panels: country, industry, owner, service, lead source, monthly forecast, conversion and trends | Both | Large | Independently reconciled seed calculations and UI charts |
| P1 | Complete company/contact profile and timeline screens, broader editable intelligence fields, and searchable/filterable/paginated lists | Both | Large | All brief fields usable and records beyond first page discoverable |
| P1 | Standalone task list with due-date filters; tasks currently managed on opportunity details | Frontend | Medium | Today/week/overdue filters and completion flow |
| P1 | Expand CSV beyond companies to other core business records if required for receiving team's workflow | Backend | Medium | Round-trip validation, ownership and role tests |
| P1 | Complete priority inputs and displayed owner/action/due information beyond current score/reason model | Both | Medium | Explain all brief factors with deterministic tests |
| P1 | Dependency vulnerability triage before any hosted release; Day 18 recorded high/critical findings | Both | Medium | Current audit, reviewed upgrades, regression gate |
| P1 | Retain full invitation/recovery/session-expiry browser evidence and independent supervisor acceptance | Both / receiver | Medium | Mailpit-only demo, screenshots and signed review |
| P2 | Improve PDF layout and Unicode/font support; current renderer is text-focused and does not reproduce HTML CSS | Backend | Medium | Branded PDF visual review and Unicode fixtures |
| P2 | Expand live browser role matrix and component coverage for ICP/task forms | Both | Medium | Five-role browser tests plus validation/empty/error cases |
| P2 | Add scheduled local integration CI and fresh-clone verification for the final tag | Backend | Medium | Repeatable isolated database/Storage gate without skipped tests |
| P2 | Harden local startup and Docker health handling across Windows/Linux | Both | Small | Clean setup without ignore-health workaround |
| P3 | Approved hosted staging, SMTP, backup/restore, observability and secret rotation | Receiver | Large | Explicit supervisor authorization, deployment review |

## Product/security boundaries

- Only synthetic `.example` / `.test` data is permitted in this internship release.
- Snapshot errors/timeouts describe unknown coverage, not verified vulnerabilities or safety.
- The report exposure indicator is a documented synthetic triage heuristic, not a validated risk score.
- Report download currently applies only to Approved status; Shared is an internal workflow marker.
- Seed reports represent synthetic role-based workflow examples, not human approval of real findings.
- Local demo accounts must never be provisioned unchanged into a hosted production project.
- Several lists have practical MVP limits and are not designed for large datasets.
- No public deployment, real data migration, external emailing or live third-party scan was authorized.

## Release decision

The internship handover can be transferred as a versioned local MVP with these explicit gaps.
It is not a claim of complete conformance to every functional detail of the brief, nor
production readiness. P1 items above remain required follow-up work, not optional polish.
