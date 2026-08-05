create table if not exists public.pipeline_stages (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    sort_order integer not null,
    default_probability integer not null default 0,
    is_won boolean not null default false,
    is_lost boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.pipeline_stages
    add column if not exists is_won boolean not null default false,
    add column if not exists is_lost boolean not null default false;

alter table public.pipeline_stages drop constraint if exists pipeline_stages_probability_check;

alter table public.pipeline_stages add constraint pipeline_stages_probability_check check (
    default_probability between 0 and 100
);

drop trigger if exists pipeline_stages_set_updated_at on public.pipeline_stages;

create trigger pipeline_stages_set_updated_at
before update on public.pipeline_stages
for each row execute function public.set_updated_at();

insert into public.pipeline_stages (name, sort_order, default_probability, is_won, is_lost)
values
    ('Identified', 10, 5, false, false),
    ('Researching', 20, 10, false, false),
    ('Contacted', 30, 15, false, false),
    ('Meeting Scheduled', 40, 25, false, false),
    ('Discovery Completed', 50, 35, false, false),
    ('Qualified', 60, 45, false, false),
    ('Assessment Offered', 70, 50, false, false),
    ('Pilot Proposed', 80, 60, false, false),
    ('Pilot Active', 90, 70, false, false),
    ('Proposal Sent', 100, 75, false, false),
    ('Negotiation', 110, 85, false, false),
    ('Contract Review', 120, 90, false, false),
    ('Won', 130, 100, true, false),
    ('Lost', 140, 0, false, true),
    ('On Hold', 150, 0, false, false)
on conflict (name) do nothing;

create table if not exists public.opportunities (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references public.companies(id) on delete cascade,
    contact_id uuid references public.contacts(id) on delete set null,
    stage_id uuid not null references public.pipeline_stages(id),
    name text not null,
    service text,
    value_usd numeric(14, 2),
    probability integer not null default 0,
    weighted_value_usd numeric(14, 2),
    expected_close_date date,
    owner_id uuid references public.profiles(id) on delete set null,
    need text,
    blockers text,
    competitor text,
    next_action text,
    next_action_due_at timestamptz,
    lost_reason text,
    created_by uuid references public.profiles(id) on delete set null,
    updated_by uuid references public.profiles(id) on delete set null,
    archived_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.opportunities drop constraint if exists opportunities_probability_check;

alter table public.opportunities add constraint opportunities_probability_check check (
    probability between 0 and 100
);

alter table public.opportunities drop constraint if exists opportunities_value_usd_check;

alter table public.opportunities add constraint opportunities_value_usd_check check (
    value_usd is null or value_usd >= 0
);

drop trigger if exists opportunities_set_updated_at on public.opportunities;

create trigger opportunities_set_updated_at
before update on public.opportunities
for each row execute function public.set_updated_at();

create index if not exists opportunities_company_id_idx
    on public.opportunities(company_id)
    where archived_at is null;

create index if not exists opportunities_stage_id_idx
    on public.opportunities(stage_id)
    where archived_at is null;

create index if not exists opportunities_owner_id_idx
    on public.opportunities(owner_id);

create index if not exists opportunities_expected_close_date_idx
    on public.opportunities(expected_close_date)
    where archived_at is null;

create table if not exists public.opportunity_stage_history (
    id uuid primary key default gen_random_uuid(),
    opportunity_id uuid not null references public.opportunities(id) on delete cascade,
    from_stage_id uuid references public.pipeline_stages(id),
    to_stage_id uuid not null references public.pipeline_stages(id),
    changed_by uuid references public.profiles(id) on delete set null,
    note text,
    changed_at timestamptz not null default now()
);

create index if not exists opportunity_stage_history_opportunity_id_idx
    on public.opportunity_stage_history(opportunity_id, changed_at desc);

create table if not exists public.activities (
    id uuid primary key default gen_random_uuid(),
    company_id uuid not null references public.companies(id) on delete cascade,
    contact_id uuid references public.contacts(id) on delete set null,
    opportunity_id uuid references public.opportunities(id) on delete set null,
    activity_type text not null,
    subject text not null,
    notes text,
    occurred_at timestamptz not null default now(),
    owner_id uuid references public.profiles(id) on delete set null,
    created_by uuid references public.profiles(id) on delete set null,
    updated_by uuid references public.profiles(id) on delete set null,
    archived_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.activities drop constraint if exists activities_activity_type_check;

alter table public.activities add constraint activities_activity_type_check check (
    activity_type in (
        'call',
        'email',
        'meeting',
        'linkedin_message',
        'conference',
        'introduction',
        'workshop',
        'demo',
        'proposal',
        'follow_up',
        'internal_note'
    )
);

drop trigger if exists activities_set_updated_at on public.activities;

create trigger activities_set_updated_at
before update on public.activities
for each row execute function public.set_updated_at();

create index if not exists activities_company_id_idx
    on public.activities(company_id)
    where archived_at is null;

create index if not exists activities_opportunity_id_idx
    on public.activities(opportunity_id)
    where archived_at is null;

create index if not exists activities_occurred_at_idx
    on public.activities(occurred_at desc)
    where archived_at is null;

create table if not exists public.tasks (
    id uuid primary key default gen_random_uuid(),
    company_id uuid references public.companies(id) on delete cascade,
    opportunity_id uuid references public.opportunities(id) on delete cascade,
    owner_id uuid references public.profiles(id) on delete set null,
    title text not null,
    description text,
    due_at timestamptz,
    priority text not null default 'medium',
    status text not null default 'open',
    outcome text,
    completed_at timestamptz,
    created_by uuid references public.profiles(id) on delete set null,
    updated_by uuid references public.profiles(id) on delete set null,
    archived_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.tasks drop constraint if exists tasks_priority_check;

alter table public.tasks add constraint tasks_priority_check check (
    priority in ('low', 'medium', 'high', 'urgent')
);

alter table public.tasks drop constraint if exists tasks_status_check;

alter table public.tasks add constraint tasks_status_check check (
    status in ('open', 'in_progress', 'completed', 'cancelled')
);

drop trigger if exists tasks_set_updated_at on public.tasks;

create trigger tasks_set_updated_at
before update on public.tasks
for each row execute function public.set_updated_at();

create index if not exists tasks_owner_id_idx
    on public.tasks(owner_id)
    where archived_at is null;

create index if not exists tasks_due_at_idx
    on public.tasks(due_at)
    where archived_at is null and status not in ('completed', 'cancelled');

create index if not exists tasks_opportunity_id_idx
    on public.tasks(opportunity_id)
    where archived_at is null;

create index if not exists tasks_status_idx
    on public.tasks(status)
    where archived_at is null;

create table if not exists public.notes (
    id uuid primary key default gen_random_uuid(),
    company_id uuid references public.companies(id) on delete cascade,
    contact_id uuid references public.contacts(id) on delete set null,
    opportunity_id uuid references public.opportunities(id) on delete set null,
    body text not null,
    created_by uuid references public.profiles(id) on delete set null,
    updated_by uuid references public.profiles(id) on delete set null,
    archived_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists notes_set_updated_at on public.notes;

create trigger notes_set_updated_at
before update on public.notes
for each row execute function public.set_updated_at();

create index if not exists notes_company_id_idx
    on public.notes(company_id)
    where archived_at is null;

create index if not exists notes_opportunity_id_idx
    on public.notes(opportunity_id)
    where archived_at is null;

alter table public.pipeline_stages enable row level security;
alter table public.opportunities enable row level security;
alter table public.opportunity_stage_history enable row level security;
alter table public.activities enable row level security;
alter table public.tasks enable row level security;
alter table public.notes enable row level security;

grant select on public.pipeline_stages to authenticated;

grant select, insert, update on public.opportunities to authenticated;
grant select, insert on public.opportunity_stage_history to authenticated;
grant select, insert, update on public.activities to authenticated;
grant select, insert, update on public.tasks to authenticated;
grant select, insert on public.notes to authenticated;

revoke delete on public.pipeline_stages from anon, authenticated;
revoke delete on public.opportunities from anon, authenticated;
revoke delete on public.opportunity_stage_history from anon, authenticated;
revoke delete on public.activities from anon, authenticated;
revoke delete on public.tasks from anon, authenticated;
revoke delete on public.notes from anon, authenticated;