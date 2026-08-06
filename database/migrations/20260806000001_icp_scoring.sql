create table if not exists public.icp_rules (
    id uuid primary key default gen_random_uuid(),
    rule_key text not null unique,
    label text not null,
    max_points integer not null,
    description text not null,
    active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.icp_rules drop constraint if exists icp_rules_max_points_check;

alter table public.icp_rules add constraint icp_rules_max_points_check check (
    max_points > 0
);

drop trigger if exists icp_rules_set_updated_at on public.icp_rules;

create trigger icp_rules_set_updated_at
before update on public.icp_rules
for each row execute function public.set_updated_at();

insert into public.icp_rules (rule_key, label, max_points, description)
values
    ('industry_fit', 'Industry fit', 25, 'Scores whether the company industry matches XY CYBER target markets.'),
    ('company_size', 'Company size', 20, 'Scores whether employee count indicates enough security complexity.'),
    ('revenue_fit', 'Revenue fit', 15, 'Scores whether annual revenue suggests budget capacity.'),
    ('regulatory_context', 'Regulatory context', 15, 'Scores compliance and regulatory security pressure.'),
    ('cloud_usage', 'Cloud usage', 10, 'Scores cloud environment complexity.'),
    ('geography', 'Geography', 5, 'Scores supported commercial geography.'),
    ('lead_source', 'Lead source', 5, 'Scores lead source intent quality.'),
    ('lifecycle', 'Lifecycle signal', 5, 'Scores prospect qualification status.')
on conflict (rule_key) do update set
    label = EXCLUDED.label,
    max_points = EXCLUDED.max_points,
    description = EXCLUDED.description,
    active = true,
    updated_at = now();

create table if not exists public.icp_score_results (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references public.companies(id) on delete cascade,
    score integer not null,
    max_score integer not null default 100,
    tier text not null,
    explanations jsonb not null default '[]'::jsonb,
    calculated_by uuid references public.profiles(id) on delete set null,
    calculated_at timestamptz not null default now()
);

alter table public.icp_score_results drop constraint if exists icp_score_results_score_check;

alter table public.icp_score_results add constraint icp_score_results_score_check check (
    score between 0 and max_score
);

alter table public.icp_score_results drop constraint if exists icp_score_results_max_score_check;

alter table public.icp_score_results add constraint icp_score_results_max_score_check check (
    max_score = 100
);

alter table public.icp_score_results drop constraint if exists icp_score_results_tier_check;

alter table public.icp_score_results add constraint icp_score_results_tier_check check (
    tier in ('strong_fit', 'good_fit', 'possible_fit', 'low_fit')
);

create index if not exists icp_score_results_company_id_idx
    on public.icp_score_results(company_id, calculated_at desc);

create index if not exists icp_score_results_score_idx
    on public.icp_score_results(score desc);

alter table public.icp_rules enable row level security;
alter table public.icp_score_results enable row level security;

drop policy if exists "icp_rules_select_authenticated" on public.icp_rules;
create policy "icp_rules_select_authenticated"
on public.icp_rules
for select
to authenticated
using (public.current_user_role() is not null);

drop policy if exists "icp_score_results_select_authenticated" on public.icp_score_results;
create policy "icp_score_results_select_authenticated"
on public.icp_score_results
for select
to authenticated
using (
    public.current_user_role() is not null
    and exists (
        select 1
        from public.companies
        where companies.id = icp_score_results.company_id
          and companies.archived_at is null
    )
);

drop policy if exists "icp_score_results_insert_writer_roles" on public.icp_score_results;
create policy "icp_score_results_insert_writer_roles"
on public.icp_score_results
for insert
to authenticated
with check (
    public.has_any_role(array['admin', 'management', 'business_development'])
    and calculated_by = auth.uid()
    and exists (
        select 1
        from public.companies
        where companies.id = icp_score_results.company_id
          and companies.archived_at is null
    )
);

grant select on public.icp_rules to authenticated;
grant select, insert on public.icp_score_results to authenticated;

revoke delete on public.icp_rules from anon, authenticated;
revoke delete on public.icp_score_results from anon, authenticated;
