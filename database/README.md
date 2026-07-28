# Database

Supabase PostgreSQL database files live here.

## Directories

- `migrations`: SQL migrations tracked in Git.
- `policies`: Row Level Security policy notes and test evidence.
- `seed`: Synthetic seed data and seed scripts.

## Rules

- Use UUID primary keys.
- Include `created_at` and `updated_at` timestamps.
- Include `created_by` and `updated_by` where meaningful.
- Use soft delete fields such as `archived_at` or `deleted_at` for business records where practical.
- Add indexes for foreign keys and common dashboard filters.
- Enable and test RLS for sensitive business tables.
- Use synthetic data only.
- Do not store real customer, prospect, or personal data.

## Week 1 TODO

- Create migrations for `profiles`, `companies`, and `contacts`.
- Add 10 synthetic companies and related contacts.
- Add first RLS allow/deny policies.
- Document how to apply migrations and seed data.
