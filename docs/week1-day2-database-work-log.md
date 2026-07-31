# Week 1 Day 2 Database Work Log

Date: 29-07-2026

Scope: Supabase database baseline for Week 1 / Day 2 of the XY CYBER Growth Intelligence internship project.

## What Was Required

The Week 1 database work needed to cover:

- A tracked migration file.
- `profiles`, `companies`, and `contacts` tables.
- Real project roles from the brief.
- RLS enabled.
- Basic allow/deny policies.
- `read_only` users blocked from inserts and updates.
- Indexes for company and contact lookups.
- Seed data with at least 10 fake companies.
- Fake contacts only.
- No real secrets or real data.
- A short document explaining RLS behavior.

## Main Problems In The Earlier Draft

1. The schema used only `admin` and `member`.
   - This did not match the brief.
   - The brief requires `admin`, `management`, `business_development`, `technical_analyst`, and `read_only`.

2. RLS was too permissive.
   - Any authenticated user could update active companies or contacts if they set `updated_by = auth.uid()`.
   - That meant a `read_only` user was not actually read-only.

3. Company/contact fields were too small for the brief.
   - Week 1 can start with schema v1, but the model should already support the expected CRM fields.

4. `set_updated_at()` did not set a fixed `search_path`.
   - For security-sensitive database functions, using `set search_path = public` is safer and more explicit.

5. Grants were not explicit.
   - In Supabase/PostgREST, table privileges and RLS policies both matter.

## What Was Changed

### 1. Real Project Roles Added

File: `database/migrations/20260729000001_initial_schema.sql`

`profiles.role` now defaults to `read_only` and accepts only:

- `admin`
- `management`
- `business_development`
- `technical_analyst`
- `read_only`

Reason:

The schema now matches the boss brief exactly. We no longer use the generic `member` role.

### 2. Read Only Users Cannot Write

File: `database/migrations/20260729000001_initial_schema.sql`

Company and contact write policies now require:

- authenticated user
- active profile
- role in `admin`, `management`, or `business_development`
- `created_by = auth.uid()` on insert
- `updated_by = auth.uid()` on insert/update

Reason:

This fixes the biggest security issue. A `read_only` user can read active records but cannot insert or update companies or contacts.

### 3. Technical Analyst Is Read-Only For Week 1 CRM Tables

File: `database/migrations/20260729000001_initial_schema.sql`

`technical_analyst` is included as a valid role, but it is not included in the Week 1 CRM writer roles.

Reason:

The technical analyst role will matter more for later Risk Snapshot work. For Week 1 company/contact management, the safer default is read-only unless the brief gives explicit write permission.

### 4. Profile Privilege Escalation Blocked

File: `database/migrations/20260729000001_initial_schema.sql`

Added `prevent_profile_privilege_escalation()` trigger.

What it does:

- A non-admin user cannot change their own `role`.
- A non-admin user cannot change their own `active` status.
- Admin can still manage roles.

Reason:

Without this, a user might be able to update their own profile into a stronger role.

### 5. Company Fields Expanded For Schema V1

File: `database/migrations/20260729000001_initial_schema.sql`

Added fields aligned with the brief:

- `domain`
- `industry`
- `company_size`
- `employee_range`
- `cloud_usage`
- `regulatory_context`
- `lead_source`
- `owner_id`
- `tags`
- `status`
- `last_activity_at`
- `next_action`
- `next_action_due_at`

Reason:

This keeps Week 1 focused, but avoids a schema that is too small for the required CRM workflow.

### 6. Contact Fields Expanded For Schema V1

File: `database/migrations/20260729000001_initial_schema.sql`

Added fields aligned with the brief:

- `role`
- `influence`
- `decision_category`
- `channels`
- `owner_id`
- `last_contact_at`
- `next_follow_up_at`

Reason:

Contacts need enough structure for buyer/champion/influencer/procurement tracking later.

### 7. Updated Timestamp Function Hardened

File: `database/migrations/20260729000001_initial_schema.sql`

`set_updated_at()` now includes:

```sql
set search_path = public
```

Reason:

This is a small hardening step for database functions.

### 8. Explicit Grants Added

File: `database/migrations/20260729000001_initial_schema.sql`

Added:

```sql
grant select, insert, update on public.profiles to authenticated;
grant select, insert, update on public.companies to authenticated;
grant select, insert, update on public.contacts to authenticated;
```

Also explicitly revoked delete for `anon` and `authenticated`.

Reason:

Supabase needs privileges and RLS policies. Grants allow PostgREST to attempt the operation; RLS decides whether the user is allowed for that row/action.

### 9. Indexes Added For Lookups

File: `database/migrations/20260729000001_initial_schema.sql`

Indexes now cover common lookups and filters:

- company name search
- company domain
- company status
- lifecycle stage
- industry
- country
- owner
- fit score
- contact company ID
- contact owner
- contact email
- contact decision category
- primary contact lookup

Reason:

The brief requires indexes for foreign keys and common dashboard/search filters.

### 10. Seed Data Expanded

File: `database/seed/seed.sql`

Seed now creates:

- 30 fictional companies
- 50 fictional contacts
- reserved `.example` domains
- fake `+1-555-01xx` phone numbers

Reason:

The Day 2 checklist requires at least 10 fake companies and fake contacts only. This seed file already exceeds that minimum and supports later demo/dashboard work.

### 11. RLS Documentation Added

Files:

- `database/policies/week1-rls.md`
- `database/policies/week1-rls-test-plan.md`

What they explain:

- which roles exist
- who can read
- who can write
- what is denied
- how to manually test allow/deny behavior in Supabase

Reason:

The checklist requires a short doc explaining what RLS allows and denies. The test plan gives evidence steps for review.

### 12. Project Docs Updated

Files:

- `README.md`
- `database/README.md`
- `docs/architecture.md`
- `docs/decision-log.md`

Reason:

The brief requires decisions and implementation status to be documented. The docs now state that the database Day 2 baseline is done, but the full Week 1 vertical slice still needs backend auth/API and frontend work.

## Day 2 Checklist Result

- Schema file exists as a migration: done.
- `profiles`, `companies`, `contacts` exist: done.
- Real roles from brief are used: done.
- RLS is enabled: done.
- Basic allow/deny policies exist: done.
- `read_only` cannot insert/update records: done.
- Indexes exist for company/contact lookups: done.
- Seed creates at least 10 fake companies: done. Current file creates 30.
- Seed uses fake contacts only: done.
- No real secrets or real data: checked.
- Short RLS doc exists: done.
- Explicit grants added: done.
- `set_updated_at()` hardened with fixed search path: done.

## Verification Performed

Commands run:

```bash
pytest
git diff --check
rg -n "(secret|service_role|apikey|api_key|password|token|BEGIN (RSA|OPENSSH|PRIVATE)|sk-[A-Za-z0-9])" -S --glob "!.git/**" --glob "!.env"
```

Results:

- Backend tests passed: `1 passed`.
- Diff whitespace check passed.
- No obvious secrets were found in tracked project files.

Limit:

`psql` is not installed in this local environment, so the SQL migration was not applied locally from this terminal. It still needs to be applied and manually checked in Supabase SQL editor or an environment with `psql`.

## How To Explain This In Review

Short version:

We fixed the Week 1 database baseline so it matches the brief roles and is not too permissive. The old `admin/member` model was replaced with the five required roles. RLS now lets authenticated users read active records, but only Admin, Management, and Business Development can create or update companies and contacts. Read Only and Technical Analyst cannot write CRM records in Week 1. We also added explicit grants, hardened the timestamp trigger, expanded company/contact fields for schema v1, added seed data, and documented the allow/deny behavior.

## Suggested Commit Message

```text
Complete week 1 database RLS baseline
```
