## Apply to Supabase (via CLI)

This project uses the Supabase CLI to apply migrations and seed data, not `psql` directly.

Prerequisites: Supabase CLI installed (`npm install -g supabase`), logged in (`supabase login`), and the project linked (`supabase link --project-ref <your-project-ref>`).

Apply schema migrations to the remote (cloud) database:

```bash
supabase db push
```

Apply seed data to the remote database:

```bash
supabase db query --file supabase/seed.sql --linked
```

For local development with Docker (optional):

```bash
supabase start
supabase db reset
```

Note: `supabase/migrations/` and `supabase/seed.sql` (used by the Supabase CLI) are the operational source of truth. `database/migrations/` and `database/seed.sql` are kept as a readable reference copy for documentation purposes.

Do not run seed scripts against a production database. The internship project uses synthetic data only.