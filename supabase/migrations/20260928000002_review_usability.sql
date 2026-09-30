-- Monetary fields use EUR.
alter table public.companies rename column annual_revenue_usd to annual_revenue_eur;
alter table public.opportunities rename column value_usd to value_eur;
alter table public.opportunities rename column weighted_value_usd to weighted_value_eur;

alter table public.tasks add column assigned_by uuid references public.profiles(id) on delete set null;
alter table public.tasks add column assigned_at timestamptz;
update public.tasks set assigned_by=created_by, assigned_at=created_at where owner_id is not null;
create or replace function public.track_task_assignment() returns trigger language plpgsql as $$
begin
 if new.owner_id is not null and (tg_op='INSERT' or new.owner_id is distinct from old.owner_id) then
  if not exists(select 1 from public.profiles where id=new.owner_id and active and role <> 'read_only') then
   raise exception 'Tasks require an active staff assignee with write permissions' using errcode='23514';
  end if;
  new.assigned_at=clock_timestamp();
  new.assigned_by=coalesce(auth.uid(),new.updated_by,new.created_by);
 elsif new.owner_id is null then
  new.assigned_at=null; new.assigned_by=null;
 end if;
 return new;
end $$;
create trigger tasks_track_assignment before insert or update of owner_id on public.tasks
for each row execute function public.track_task_assignment();

create table public.inbox_reads (
 user_id uuid not null references public.profiles(id) on delete cascade,
 kind text not null check(kind in ('tasks','notes')),
 record_id uuid not null,
 read_at timestamptz not null default now(),
 primary key(user_id,kind,record_id)
);
alter table public.inbox_reads enable row level security;
revoke all on public.inbox_reads from anon,authenticated;
grant select,insert,update on public.inbox_reads to authenticated;
create policy inbox_reads_own on public.inbox_reads to authenticated
using(user_id=auth.uid() and public.current_user_role() is not null)
with check(user_id=auth.uid() and public.current_user_role() is not null);

-- Archiving is independent of sharing; approval remains mandatory for downloads.
CREATE OR REPLACE FUNCTION public.enforce_report_workflow() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE actor_role text := public.report_actor_role(); actor_id uuid := COALESCE(NULLIF(current_setting('app.report_actor_id', true), '')::uuid, auth.uid());
BEGIN
 IF TG_OP = 'INSERT' THEN
  IF NEW.status <> 'draft' OR actor_role NOT IN ('admin','management','technical_analyst') OR NEW.created_by IS DISTINCT FROM actor_id THEN RAISE EXCEPTION 'invalid report creation'; END IF;
  RETURN NEW;
 END IF;
 IF NEW.status = OLD.status THEN RAISE EXCEPTION 'report updates must use a workflow transition'; END IF;
 IF OLD.status='draft' AND NEW.status='review' AND actor_role IN ('admin','management','technical_analyst') THEN NEW.reviewed_by:=actor_id; NEW.reviewed_at:=now();
 ELSIF OLD.status='review' AND NEW.status='approved' AND actor_role IN ('admin','management') THEN NEW.approved_by:=actor_id; NEW.approved_at:=now();
 ELSIF OLD.status='approved' AND NEW.status='shared' AND actor_role IN ('admin','management') THEN NEW.shared_by:=actor_id; NEW.shared_at:=now();
 ELSIF OLD.status IN ('draft','review','approved','shared') AND NEW.status='archived' AND actor_role IN ('admin','management') THEN NEW.archived_by:=actor_id; NEW.archived_at:=now();
 ELSE RAISE EXCEPTION 'invalid report workflow transition'; END IF;
 RETURN NEW;
END $$;
