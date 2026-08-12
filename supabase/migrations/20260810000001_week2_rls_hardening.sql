-- Week 2 Day 10 RLS hardening after Supabase Advisor review.
-- Keep public tables private to anon and make Week 2 sales workflow policies explicit.

alter table public.profiles enable row level security;
alter table public.companies enable row level security;
alter table public.contacts enable row level security;
alter table public.pipeline_stages enable row level security;
alter table public.opportunities enable row level security;
alter table public.opportunity_stage_history enable row level security;
alter table public.activities enable row level security;
alter table public.tasks enable row level security;
alter table public.notes enable row level security;
alter table public.icp_rules enable row level security;
alter table public.icp_score_results enable row level security;

revoke all on public.profiles from anon;
revoke all on public.companies from anon;
revoke all on public.contacts from anon;
revoke all on public.pipeline_stages from anon;
revoke all on public.opportunities from anon;
revoke all on public.opportunity_stage_history from anon;
revoke all on public.activities from anon;
revoke all on public.tasks from anon;
revoke all on public.notes from anon;
revoke all on public.icp_rules from anon;
revoke all on public.icp_score_results from anon;

grant select, insert, update on public.profiles to authenticated;
grant select, insert, update on public.companies to authenticated;
grant select, insert, update on public.contacts to authenticated;
grant select, insert, update on public.pipeline_stages to authenticated;
grant select, insert, update on public.opportunities to authenticated;
grant select, insert on public.opportunity_stage_history to authenticated;
grant select, insert, update on public.activities to authenticated;
grant select, insert, update on public.tasks to authenticated;
grant select, insert, update on public.notes to authenticated;
grant select on public.icp_rules to authenticated;
grant select, insert on public.icp_score_results to authenticated;

revoke delete on public.profiles from anon, authenticated;
revoke delete on public.companies from anon, authenticated;
revoke delete on public.contacts from anon, authenticated;
revoke delete on public.pipeline_stages from anon, authenticated;
revoke delete on public.opportunities from anon, authenticated;
revoke delete on public.opportunity_stage_history from anon, authenticated;
revoke delete on public.activities from anon, authenticated;
revoke delete on public.tasks from anon, authenticated;
revoke delete on public.notes from anon, authenticated;
revoke delete on public.icp_rules from anon, authenticated;
revoke delete on public.icp_score_results from anon, authenticated;

drop policy if exists "pipeline_stages_select_authenticated" on public.pipeline_stages;
drop policy if exists "pipeline_stages_insert_manager_roles" on public.pipeline_stages;
drop policy if exists "pipeline_stages_update_manager_roles" on public.pipeline_stages;

create policy "pipeline_stages_select_authenticated"
on public.pipeline_stages
for select
to authenticated
using (public.current_user_role() is not null);

create policy "pipeline_stages_insert_manager_roles"
on public.pipeline_stages
for insert
to authenticated
with check (public.has_any_role(array['admin', 'management']));

create policy "pipeline_stages_update_manager_roles"
on public.pipeline_stages
for update
to authenticated
using (public.has_any_role(array['admin', 'management']))
with check (public.has_any_role(array['admin', 'management']));

drop policy if exists "opportunities_select_active_authenticated" on public.opportunities;
drop policy if exists "opportunities_insert_writer_roles" on public.opportunities;
drop policy if exists "opportunities_update_writer_roles" on public.opportunities;

create policy "opportunities_select_active_authenticated"
on public.opportunities
for select
to authenticated
using (
    archived_at is null
    and public.current_user_role() is not null
);

create policy "opportunities_insert_writer_roles"
on public.opportunities
for insert
to authenticated
with check (
    archived_at is null
    and public.has_any_role(array['admin', 'management', 'business_development'])
    and created_by = auth.uid()
    and updated_by = auth.uid()
);

create policy "opportunities_update_writer_roles"
on public.opportunities
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

drop policy if exists "opportunity_stage_history_select_authenticated"
    on public.opportunity_stage_history;
drop policy if exists "opportunity_stage_history_insert_writer_roles"
    on public.opportunity_stage_history;

create policy "opportunity_stage_history_select_authenticated"
on public.opportunity_stage_history
for select
to authenticated
using (public.current_user_role() is not null);

create policy "opportunity_stage_history_insert_writer_roles"
on public.opportunity_stage_history
for insert
to authenticated
with check (
    public.has_any_role(array['admin', 'management', 'business_development'])
    and changed_by = auth.uid()
);

drop policy if exists "activities_select_active_authenticated" on public.activities;
drop policy if exists "activities_insert_writer_roles" on public.activities;
drop policy if exists "activities_update_writer_roles" on public.activities;

create policy "activities_select_active_authenticated"
on public.activities
for select
to authenticated
using (
    archived_at is null
    and public.current_user_role() is not null
);

create policy "activities_insert_writer_roles"
on public.activities
for insert
to authenticated
with check (
    archived_at is null
    and public.has_any_role(array['admin', 'management', 'business_development'])
    and created_by = auth.uid()
    and updated_by = auth.uid()
);

create policy "activities_update_writer_roles"
on public.activities
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

drop policy if exists "tasks_select_active_authenticated" on public.tasks;
drop policy if exists "tasks_insert_writer_roles" on public.tasks;
drop policy if exists "tasks_update_writer_roles" on public.tasks;

create policy "tasks_select_active_authenticated"
on public.tasks
for select
to authenticated
using (
    archived_at is null
    and public.current_user_role() is not null
);

create policy "tasks_insert_writer_roles"
on public.tasks
for insert
to authenticated
with check (
    archived_at is null
    and public.has_any_role(array['admin', 'management', 'business_development'])
    and created_by = auth.uid()
    and updated_by = auth.uid()
);

create policy "tasks_update_writer_roles"
on public.tasks
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

drop policy if exists "notes_select_active_authenticated" on public.notes;
drop policy if exists "notes_insert_writer_roles" on public.notes;
drop policy if exists "notes_update_writer_roles" on public.notes;

create policy "notes_select_active_authenticated"
on public.notes
for select
to authenticated
using (
    archived_at is null
    and public.current_user_role() is not null
);

create policy "notes_insert_writer_roles"
on public.notes
for insert
to authenticated
with check (
    archived_at is null
    and public.has_any_role(array['admin', 'management', 'business_development'])
    and created_by = auth.uid()
    and updated_by = auth.uid()
);

create policy "notes_update_writer_roles"
on public.notes
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
