# Database

This project uses Supabase PostgreSQL with tracked migrations, seed data, and Row Level Security.

## Local First Workflow

The project brief says local Docker development comes first. Use the local Supabase stack for Week 1 verification.

Prerequisites:

- Docker Desktop
- Supabase CLI

Run from the repository root:

```bash
supabase start
supabase db reset
```

`supabase db reset` uses `supabase/config.toml` and applies:

- migrations from `database/migrations/**/*.sql`
- seed data from `database/seed/seed.sql`

## Remote Supabase

Remote or hosted Supabase changes are not the default Week 1 path. Use them only after team coordination and approval, with synthetic data only.

If a disposable approved remote project is used later, document that decision first and verify the exact commands before running them.

## Migration and policy sources

- All SQL files in `database/migrations/`, in timestamp order
- `database/seed/seed.sql`
- `database/policies/week1-rls.md`
- `database/policies/week1-rls-test-plan.md`

## Current Seed Data

- 30 fictional companies
- 50 fictional contacts
- 20 opportunities, 40 activities, 25 tasks, 5 scans
- 5 real PDF reports after the local report bootstrap below
- reserved `.example` domains
- fake `+1-555-01xx` phone numbers

Do not run seed scripts against a production database. The internship project uses synthetic data only.

## Report bootstrap after SQL seed

From `backend/`, with the same local `DATABASE_URL`, `SUPABASE_URL` and server-only
`SUPABASE_SERVICE_ROLE_KEY` loaded as in the root README:

```powershell
python -m app.seed_reports
```

This creates branded HTML and private PDFs using the production report generator and
advances five fixed synthetic reports through the normal role-checked workflow. It can
be run repeatedly: existing objects are verified and completed states are not rewound.
Only the exact five empty Day 19 placeholder records are upgraded automatically. The
command refuses non-loopback destinations and any `APP_ENV` other than `local`.
No policy/trigger is disabled. Normal application startup must never reset the database.
