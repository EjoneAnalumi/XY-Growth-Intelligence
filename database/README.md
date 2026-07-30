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

## Current Week 1 Files

- `database/migrations/20260729000001_initial_schema.sql`
- `database/seed/seed.sql`
- `database/policies/week1-rls.md`
- `database/policies/week1-rls-test-plan.md`

## Current Seed Data

- 30 fictional companies
- 50 fictional contacts
- reserved `.example` domains
- fake `+1-555-01xx` phone numbers

Do not run seed scripts against a production database. The internship project uses synthetic data only.
