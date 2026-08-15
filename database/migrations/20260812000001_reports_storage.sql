-- Week 3 Day 13 report workflow schema and Supabase Storage bucket contract.

create table if not exists public.reports (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references public.companies(id) on delete cascade,
    security_scan_id uuid,
    title text not null,
    status text not null default 'draft' check (
        status in ('draft', 'review', 'approved', 'archived')
    ),
    storage_bucket text not null default 'reports',
    storage_path text,
    html_preview text not null,
    created_by uuid references public.profiles(id) on delete set null,
    reviewed_by uuid references public.profiles(id) on delete set null,
    approved_by uuid references public.profiles(id) on delete set null,
    archived_by uuid references public.profiles(id) on delete set null,
    reviewed_at timestamptz,
    approved_at timestamptz,
    archived_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists reports_company_id_idx
    on public.reports(company_id);

create index if not exists reports_status_idx
    on public.reports(status)
    where status <> 'archived';

create index if not exists reports_created_at_idx
    on public.reports(created_at desc);

drop trigger if exists reports_set_updated_at on public.reports;
create trigger reports_set_updated_at
before update on public.reports
for each row execute function public.set_updated_at();

alter table public.reports enable row level security;

grant select, insert, update on public.reports to authenticated;
revoke delete on public.reports from anon, authenticated;

drop policy if exists "reports_select_authenticated" on public.reports;
create policy "reports_select_authenticated"
on public.reports
for select
to authenticated
using (public.current_user_role() is not null);

drop policy if exists "reports_insert_author_roles" on public.reports;
create policy "reports_insert_author_roles"
on public.reports
for insert
to authenticated
with check (
    status = 'draft'
    and public.has_any_role(array['admin', 'management', 'technical_analyst'])
    and created_by = auth.uid()
);

drop policy if exists "reports_update_author_or_approver_roles" on public.reports;
create policy "reports_update_author_or_approver_roles"
on public.reports
for update
to authenticated
using (
    status <> 'archived'
    and public.has_any_role(array['admin', 'management', 'technical_analyst'])
)
with check (
    public.has_any_role(array['admin', 'management', 'technical_analyst'])
    and (
        status in ('draft', 'review')
        or public.has_any_role(array['admin', 'management'])
    )
);

insert into storage.buckets (id, name, public)
values ('reports', 'reports', false)
on conflict (id) do nothing;

drop policy if exists "report_files_select_approver_roles" on storage.objects;
create policy "report_files_select_approver_roles"
on storage.objects
for select
to authenticated
using (
    bucket_id = 'reports'
    and public.has_any_role(array['admin', 'management'])
);

drop policy if exists "report_files_insert_system_roles" on storage.objects;
create policy "report_files_insert_system_roles"
on storage.objects
for insert
to authenticated
with check (
    bucket_id = 'reports'
    and public.has_any_role(array['admin', 'management', 'technical_analyst'])
);
