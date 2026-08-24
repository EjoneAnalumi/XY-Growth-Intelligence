# Week 4 Day 18 follow-up: persistent CRM and workflow usability

Date: 24-08-2026  
Branch: `feature/crm-workflow-persistence-usability`

## Scope

This follow-up is deliberately not named Day 19. It completes the user-requested CRM usability and durability work after the Day 18 clean-install PR: persistent core records, company/contact CRUD, staff notes and to-dos, opportunity contact/stage guidance, dashboard explanations, scan/report explanations, and role guidance.

## Implemented

- FastAPI selects Supabase PostgreSQL repositories whenever `DATABASE_URL` is configured; the in-memory repositories remain only as a database-free unit-test fallback.
- Companies and contacts now support update and soft-delete/archive APIs and UI actions.
- Opportunities, activities, tasks, notes, pipeline stages, stage history, and dashboard calculations read/write the existing Supabase tables.
- Staff can record activities, schedule and complete tasks, and create/edit/archive internal notes on an opportunity.
- Staff Notes now has a dedicated main-navigation page for shared reminders; opportunity-specific notes remain visible on opportunity details. Activities and tasks also expose edit/archive controls, and opportunities expose edit/archive controls on the detail page.
- The opportunity form filters contacts to the selected company, auto-selects the sole matching contact, and explains why other contacts are excluded.
- In-app guidance explains opportunity names, pipeline stages, dashboard calculations, scan targets, report subjects/workflow, and the four staff roles.

## Verification

- `python -m pytest backend/tests -q`: 96 passed, 5 skipped with local Supabase running.
- `python -m ruff check backend`: passed.
- `npm.cmd run typecheck`: passed.
- `npm.cmd run lint`: passed with no warnings or errors.
- `npm.cmd run build`: passed; 11 routes generated.
- Local Supabase persistence test with `DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres`: passed. It created synthetic company/contact/opportunity/note records, constructed fresh repository instances, verified every record remained, and archived its fixtures.
- `npm.cmd ci` retained the known audit result: 15 findings (3 moderate, 11 high, 1 critical). No force upgrade was applied.
- Automated in-app browser interaction could not start because its local runtime asset was unavailable. UI verification therefore relies on type-check, lint, production build, and live API checks; a manual click-through remains recommended before merge.
- A live UI check exposed seeded companies/contacts with nullable audit-owner columns. Response schemas now match the nullable Supabase columns; regression coverage was added, and companies, contacts, opportunities, stages, and dashboard endpoints all returned HTTP 200 after the container rebuild.
- Four leaked `Admin Stage <suffix>` RLS-test rows were traced to a missing test cleanup. Two unused rows were removed; the referenced synthetic closed-win opportunity and history were remapped to the existing `Won` stage before the remaining rows were removed. The test now removes its own temporary stage. Supabase was verified at 15 intended stages and zero `Admin Stage` rows after the full suite.

## Security

- Synthetic `.example`/`.test` fixtures only.
- Deletes are soft archives; the persistence test removes its uniquely named fixtures from active views.
- No generated Supabase keys, service-role keys, API keys, real credentials, or real prospect/customer data are committed.
- Direct database access is a local MVP runtime path. Production deployment must use properly scoped credentials and complete Supabase Auth/JWT enforcement.

## Remaining work

- Real Supabase Auth remains incomplete. The demo login and role tokens do not authenticate real users or isolate their identities.
- Dependency audit findings need a separately scoped, tested upgrade.
- Broader browser interaction tests and deployment configuration remain production-hardening work.

## Status

The requested persistent core CRM and usability follow-up is implemented and verified locally. Core CRM records now survive logout and backend restart when Supabase is running. Authentication itself is still a documented MVP limitation.
