-- Service catalogue is readable by staff; configuration writes go through the Admin API.
alter table public.companies add column strategic_importance integer not null default 0
check (strategic_importance between 0 and 5);
create table public.services (
    id uuid primary key default gen_random_uuid(),
    name text not null check (length(trim(name)) between 1 and 120),
    description text not null default '',
    active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
alter table public.services enable row level security;
revoke all on public.services from anon, authenticated;
grant select on public.services to authenticated;
create policy services_staff_read on public.services for select to authenticated
using (public.current_user_role() is not null);
insert into public.services(name) values
('Cloud Security Assessment'), ('Compliance Readiness Review'), ('Managed SOC'),
('Cyber Risk Snapshot'), ('External Attack Surface Review'),
('Executive Security Workshop'), ('Security Discovery Workshop');
