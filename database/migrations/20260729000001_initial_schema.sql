-- Initial Supabase schema for the Growth Intelligence MVP.
-- Week 1 scope: profiles, companies, contacts, indexes, and first RLS policies.

create extension if not exists pgcrypto;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    full_name text,
    role text not null default 'read_only',
    active boolean not null default true,
    last_login_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.companies (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    domain text,
    website text,
    industry text,
    company_size text,
    employee_range text,
    employee_count integer,
    annual_revenue_usd numeric(14, 2),
    headquarters_city text,
    headquarters_country text,
    cloud_usage text[] not null default '{}',
    regulatory_context text[] not null default '{}',
    lead_source text,
    owner_id uuid references public.profiles(id) on delete set null,
    tags text[] not null default '{}',
    status text not null default 'prospect',
    lifecycle_stage text not null default 'prospect',
    fit_score integer,
    last_activity_at timestamptz,
    next_action text,
    next_action_due_at timestamptz,
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
    role text,
    influence text,
    decision_category text,
    channels text[] not null default '{}',
    owner_id uuid references public.profiles(id) on delete set null,
    last_contact_at timestamptz,
    next_follow_up_at timestamptz,
    is_primary boolean not null default false,
    created_by uuid references public.profiles(id) on delete set null,
    updated_by uuid references public.profiles(id) on delete set null,
    archived_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Keep the migration repeatable if an earlier Day 2 draft was already applied.
update public.profiles
set role = 'business_development'
where role = 'member';

alter table public.profiles
    add column if not exists active boolean not null default true,
    add column if not exists last_login_at timestamptz;

alter table public.companies
    add column if not exists domain text,
    add column if not exists company_size text,
    add column if not exists employee_range text,
    add column if not exists cloud_usage text[] not null default '{}',
    add column if not exists regulatory_context text[] not null default '{}',
    add column if not exists lead_source text,
    add column if not exists owner_id uuid references public.profiles(id) on delete set null,
    add column if not exists tags text[] not null default '{}',
    add column if not exists status text not null default 'prospect',
    add column if not exists last_activity_at timestamptz,
    add column if not exists next_action text,
    add column if not exists next_action_due_at timestamptz;

alter table public.contacts
    add column if not exists role text,
    add column if not exists influence text,
    add column if not exists decision_category text,
    add column if not exists channels text[] not null default '{}',
    add column if not exists owner_id uuid references public.profiles(id) on delete set null,
    add column if not exists last_contact_at timestamptz,
    add column if not exists next_follow_up_at timestamptz;

alter table public.profiles drop constraint if exists profiles_role_check;
alter table public.profiles add constraint profiles_role_check check (
    role in (
        'admin',
        'management',
        'business_development',
        'technical_analyst',
        'read_only'
    )
);

alter table public.companies drop constraint if exists companies_employee_count_check;
alter table public.companies add constraint companies_employee_count_check check (
    employee_count is null or employee_count >= 0
);

alter table public.companies drop constraint if exists companies_annual_revenue_usd_check;
alter table public.companies add constraint companies_annual_revenue_usd_check check (
    annual_revenue_usd is null or annual_revenue_usd >= 0
);

alter table public.companies drop constraint if exists companies_status_check;
alter table public.companies add constraint companies_status_check check (
    status in ('prospect', 'qualified', 'customer', 'partner', 'inactive', 'archived')
);

alter table public.companies drop constraint if exists companies_lifecycle_stage_check;
alter table public.companies add constraint companies_lifecycle_stage_check check (
    lifecycle_stage in ('prospect', 'qualified', 'customer', 'archived')
);

alter table public.companies drop constraint if exists companies_fit_score_check;
alter table public.companies add constraint companies_fit_score_check check (
    fit_score is null or fit_score between 0 and 100
);

alter table public.contacts drop constraint if exists contacts_email_format;
alter table public.contacts add constraint contacts_email_format check (
    email is null or email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
);

alter table public.contacts drop constraint if exists contacts_influence_check;
alter table public.contacts add constraint contacts_influence_check check (
    influence is null or influence in ('high', 'medium', 'low', 'unknown')
);

alter table public.contacts drop constraint if exists contacts_decision_category_check;
alter table public.contacts add constraint contacts_decision_category_check check (
    decision_category is null
    or decision_category in ('buyer', 'champion', 'influencer', 'procurement', 'unknown')
);

create index if not exists companies_name_idx
    on public.companies using gin (to_tsvector('simple', coalesce(name, '')))
    where archived_at is null;

create index if not exists companies_domain_idx
    on public.companies(lower(domain))
    where domain is not null and archived_at is null;

create index if not exists companies_status_idx
    on public.companies(status)
    where archived_at is null;

create index if not exists companies_lifecycle_stage_idx
    on public.companies(lifecycle_stage)
    where archived_at is null;

create index if not exists companies_industry_idx
    on public.companies(industry)
    where archived_at is null;

create index if not exists companies_country_idx
    on public.companies(headquarters_country)
    where archived_at is null;

create index if not exists companies_owner_id_idx
    on public.companies(owner_id);

create index if not exists companies_fit_score_idx
    on public.companies(fit_score desc)
    where archived_at is null;

create index if not exists companies_created_by_idx
    on public.companies(created_by);

create index if not exists contacts_company_id_idx
    on public.contacts(company_id);

create index if not exists contacts_owner_id_idx
    on public.contacts(owner_id);

create index if not exists contacts_email_idx
    on public.contacts(lower(email))
    where email is not null and archived_at is null;

create index if not exists contacts_decision_category_idx
    on public.contacts(decision_category)
    where archived_at is null;

create index if not exists contacts_is_primary_idx
    on public.contacts(company_id, is_primary)
    where archived_at is null;

create or replace function public.current_user_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
    select p.role
    from public.profiles p
    where p.id = auth.uid()
      and p.active = true
$$;

create or replace function public.has_any_role(allowed_roles text[])
returns boolean
language sql
stable
security definer
set search_path = public
as $$
    select coalesce(public.current_user_role() = any(allowed_roles), false)
$$;

create or replace function public.prevent_profile_privilege_escalation()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    if auth.uid() = old.id
       and public.current_user_role() <> 'admin'
       and (new.role is distinct from old.role or new.active is distinct from old.active)
    then
        raise exception 'Only admins can change profile role or active status.';
    end if;

    return new;
end;
$$;

drop trigger if exists profiles_prevent_privilege_escalation on public.profiles;
create trigger profiles_prevent_privilege_escalation
before update on public.profiles
for each row execute function public.prevent_profile_privilege_escalation();

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
drop policy if exists "profiles_insert_own" on public.profiles;
drop policy if exists "profiles_update_own" on public.profiles;
drop policy if exists "profiles_select_self_or_admin" on public.profiles;
drop policy if exists "profiles_insert_self_read_only" on public.profiles;
drop policy if exists "profiles_update_self_or_admin" on public.profiles;

create policy "profiles_select_self_or_admin"
on public.profiles
for select
to authenticated
using (
    id = auth.uid()
    or public.has_any_role(array['admin'])
);

create policy "profiles_insert_self_read_only"
on public.profiles
for insert
to authenticated
with check (
    id = auth.uid()
    and role = 'read_only'
);

create policy "profiles_update_self_or_admin"
on public.profiles
for update
to authenticated
using (
    id = auth.uid()
    or public.has_any_role(array['admin'])
)
with check (
    id = auth.uid()
    or public.has_any_role(array['admin'])
);

drop policy if exists "companies_select_authenticated" on public.companies;
drop policy if exists "companies_insert_authenticated" on public.companies;
drop policy if exists "companies_update_authenticated" on public.companies;
drop policy if exists "companies_select_active_authenticated" on public.companies;
drop policy if exists "companies_insert_writer_roles" on public.companies;
drop policy if exists "companies_update_writer_roles" on public.companies;

create policy "companies_select_active_authenticated"
on public.companies
for select
to authenticated
using (
    archived_at is null
    and public.current_user_role() is not null
);

create policy "companies_insert_writer_roles"
on public.companies
for insert
to authenticated
with check (
    archived_at is null
    and public.has_any_role(array['admin', 'management', 'business_development'])
    and created_by = auth.uid()
    and updated_by = auth.uid()
);

create policy "companies_update_writer_roles"
on public.companies
for update
to authenticated
using (
    archived_at is null
    and public.has_any_role(array['admin', 'management', 'business_development'])
)
with check (
    public.has_any_role(array['admin', 'management', 'business_development'])
    and updated_by = auth.uid()
);

drop policy if exists "contacts_select_authenticated" on public.contacts;
drop policy if exists "contacts_insert_authenticated" on public.contacts;
drop policy if exists "contacts_update_authenticated" on public.contacts;
drop policy if exists "contacts_select_active_authenticated" on public.contacts;
drop policy if exists "contacts_insert_writer_roles" on public.contacts;
drop policy if exists "contacts_update_writer_roles" on public.contacts;

create policy "contacts_select_active_authenticated"
on public.contacts
for select
to authenticated
using (
    archived_at is null
    and public.current_user_role() is not null
    and exists (
        select 1
        from public.companies
        where companies.id = contacts.company_id
          and companies.archived_at is null
    )
);

create policy "contacts_insert_writer_roles"
on public.contacts
for insert
to authenticated
with check (
    archived_at is null
    and public.has_any_role(array['admin', 'management', 'business_development'])
    and created_by = auth.uid()
    and updated_by = auth.uid()
    and exists (
        select 1
        from public.companies
        where companies.id = contacts.company_id
          and companies.archived_at is null
    )
);

create policy "contacts_update_writer_roles"
on public.contacts
for update
to authenticated
using (
    archived_at is null
    and public.has_any_role(array['admin', 'management', 'business_development'])
)
with check (
    public.has_any_role(array['admin', 'management', 'business_development'])
    and updated_by = auth.uid()
    and exists (
        select 1
        from public.companies
        where companies.id = contacts.company_id
          and companies.archived_at is null
    )
);

grant usage on schema public to authenticated;

grant select, insert, update on public.profiles to authenticated;
grant select, insert, update on public.companies to authenticated;
grant select, insert, update on public.contacts to authenticated;

revoke delete on public.profiles from anon, authenticated;
revoke delete on public.companies from anon, authenticated;
revoke delete on public.contacts from anon, authenticated;

grant execute on function public.current_user_role() to authenticated;
grant execute on function public.has_any_role(text[]) to authenticated;
