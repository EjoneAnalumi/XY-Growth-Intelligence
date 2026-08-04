create table if not exists public.opportunity_stage_history (
    id uuid primary key default gen_random_uuid(),

    opportunity_id uuid not null references public.opportunities(id) on delete cascade,

    from_stage_id uuid references public.pipeline_stages(id),
    to_stage_id uuid not null references public.pipeline_stages(id),
    changed_by uuid references public.profiles(id) on delete set null,
    note text,

    changed_at timestamptz default now()
);


alter table public.opportunity_stage_history enable row level security;


create policy allow_anon_all_stage_history
on public.opportunity_stage_history
for all
to anon
using (true)
with check (true);
