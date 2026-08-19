-- Day 17 CSV imports reject duplicate active company names and domains.
-- These indexes keep the API duplicate policy race-safe in the Supabase-backed path.

create unique index if not exists companies_active_name_unique_idx
    on public.companies (lower(name))
    where archived_at is null;

create unique index if not exists companies_active_domain_unique_idx
    on public.companies (lower(domain))
    where domain is not null and archived_at is null;
