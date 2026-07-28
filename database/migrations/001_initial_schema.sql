-- Initial Supabase schema for the Growth Intelligence MVP.

create extension if not exists pgcrypto;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    full_name text,
    role text not null default 'member' check (role in ('admin', 'member')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.companies (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    website text,
    industry text,
    employee_count integer check (employee_count is null or employee_count >= 0),
    annual_revenue_usd numeric(14, 2) check (
        annual_revenue_usd is null or annual_revenue_usd >= 0
    ),
    headquarters_city text,
    headquarters_country text,
    lifecycle_stage text not null default 'prospect' check (
        lifecycle_stage in ('prospect', 'qualified', 'customer', 'archived')
    ),
    fit_score integer check (fit_score is null or fit_score between 0 and 100),
    created_by uuid references public.profiles(id) on delete set null,
    updated_by uuid references public.profiles(id) on delete set null,
    archived_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.contacts (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references public.companies(id) on delete cascade,
    first_name text not null,
    last_name text not null,
    email text,
    phone text,
    title text,
    department text,
    is_primary boolean not null default false,
    created_by uuid references public.profiles(id) on delete set null,
    updated_by uuid references public.profiles(id) on delete set null,
    archived_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint contacts_email_format check (
        email is null or email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
    )
);

create index if not exists companies_lifecycle_stage_idx
    on public.companies(lifecycle_stage)
    where archived_at is null;

create index if not exists companies_industry_idx
    on public.companies(industry)
    where archived_at is null;

create index if not exists companies_fit_score_idx
    on public.companies(fit_score desc)
    where archived_at is null;

create index if not exists companies_created_by_idx
    on public.companies(created_by);

create index if not exists contacts_company_id_idx
    on public.contacts(company_id);

create index if not exists contacts_email_idx
    on public.contacts(lower(email))
    where email is not null and archived_at is null;

create index if not exists contacts_is_primary_idx
    on public.contacts(company_id, is_primary)
    where archived_at is null;

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

drop trigger if exists companies_set_updated_at on public.companies;
create trigger companies_set_updated_at
before update on public.companies
for each row execute function public.set_updated_at();

drop trigger if exists contacts_set_updated_at on public.contacts;
create trigger contacts_set_updated_at
before update on public.contacts
for each row execute function public.set_updated_at();

alter table public.profiles enable row level security;
alter table public.companies enable row level security;
alter table public.contacts enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own"
on public.profiles
for select
to authenticated
using (id = auth.uid());

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own"
on public.profiles
for insert
to authenticated
with check (id = auth.uid());

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
on public.profiles
for update
to authenticated
using (id = auth.uid())
with check (id = auth.uid());

drop policy if exists "companies_select_authenticated" on public.companies;
create policy "companies_select_authenticated"
on public.companies
for select
to authenticated
using (archived_at is null);

drop policy if exists "companies_insert_authenticated" on public.companies;
create policy "companies_insert_authenticated"
on public.companies
for insert
to authenticated
with check (
    archived_at is null
    and created_by = auth.uid()
    and updated_by = auth.uid()
);

drop policy if exists "companies_update_authenticated" on public.companies;
create policy "companies_update_authenticated"
on public.companies
for update
to authenticated
using (archived_at is null)
with check (updated_by = auth.uid());

drop policy if exists "contacts_select_authenticated" on public.contacts;
create policy "contacts_select_authenticated"
on public.contacts
for select
to authenticated
using (
    archived_at is null
    and exists (
        select 1
        from public.companies
        where companies.id = contacts.company_id
          and companies.archived_at is null
    )
);

drop policy if exists "contacts_insert_authenticated" on public.contacts;
create policy "contacts_insert_authenticated"
on public.contacts
for insert
to authenticated
with check (
    archived_at is null
    and created_by = auth.uid()
    and updated_by = auth.uid()
    and exists (
        select 1
        from public.companies
        where companies.id = contacts.company_id
          and companies.archived_at is null
    )
);

drop policy if exists "contacts_update_authenticated" on public.contacts;
create policy "contacts_update_authenticated"
on public.contacts
for update
to authenticated
using (archived_at is null)
with check (
    updated_by = auth.uid()
    and exists (
        select 1
        from public.companies
        where companies.id = contacts.company_id
          and companies.archived_at is null
    )
);
