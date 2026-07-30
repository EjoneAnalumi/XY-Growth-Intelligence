Week 1 RLS Test Plan

Run these checks against the local Supabase stack (default per project brief: local Docker environment first; hosted/remote is a Red decision requiring supervisor approval).

bash
supabase start
supabase db reset

supabase db reset re-applies every migration in supabase/migrations/ (currently 20260729000001_initial_schema.sql) and re-seeds from database/seed/seed.sql, so it already covers what a manual psql run would do. Only fall back to psql "$DATABASE_URL" -f <file> if you are testing against a disposable Supabase cloud project instead of local Docker, and note that as a Yellow/Red decision in the decision log.

Use real test users created through Supabase Auth (e.g. via Supabase Studio at http://127.0.0.1:54323 → Authentication → Add user) so profiles.id can reference auth.users(id).

Test Users

Create at least these test users:

business_development
read_only
technical_analyst
admin

Then insert or update their public.profiles records with matching roles. Do this setup with a privileged local SQL session (Supabase Studio SQL editor or supabase db query), not from the application UI.

Required Checks
Business Development can create a company.
Expected: insert succeeds when created_by and updated_by match the signed-in user ID.
Business Development can update a company.
Expected: update succeeds when updated_by matches the signed-in user ID.
Read Only can read active companies and contacts.
Expected: select succeeds for non-archived records.
Read Only cannot create or update companies.
Expected: Supabase/PostgREST returns an RLS permission error and no row changes.
Read Only cannot create or update contacts.
Expected: Supabase/PostgREST returns an RLS permission error and no row changes.
Technical Analyst cannot create or update companies/contacts in Week 1 CRM scope.
Expected: Supabase/PostgREST returns an RLS permission error and no row changes.
Anonymous user cannot read Week 1 business records.
Expected: unauthenticated request returns no access.
Non-admin user cannot change their own role or active fields.
Expected: trigger raises Only admins can change profile role or active status.
Admin can update another user's profile role.
Expected: update succeeds.
Evidence To Capture
SQL editor output or API response for one allowed write.
SQL editor output or API response for one denied read_only write.
Screenshot or copied response showing RLS enabled on profiles, companies, and contacts.
Row count after seed showing 30 companies and 50 contacts