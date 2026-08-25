-- Supabase Auth profile provisioning and business-change audit trail.

create or replace function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (id, full_name, role, active)
    values (
        new.id,
        coalesce(new.raw_user_meta_data ->> 'full_name', split_part(new.email, '@', 1)),
        'read_only',
        true
    )
    on conflict (id) do update
    set full_name = coalesce(excluded.full_name, public.profiles.full_name),
        updated_at = now();
    return new;
end;
$$;

drop trigger if exists auth_user_profile_created on auth.users;
create trigger auth_user_profile_created
after insert or update of raw_user_meta_data on auth.users
for each row execute function public.handle_new_auth_user();

create table if not exists public.audit_logs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references public.profiles(id) on delete set null,
    entity_type text not null,
    entity_id uuid not null,
    action text not null check (action in ('created', 'updated', 'archived')),
    changed_at timestamptz not null default now()
);

create index if not exists audit_logs_entity_idx
    on public.audit_logs(entity_type, entity_id, changed_at desc);
create index if not exists audit_logs_user_idx
    on public.audit_logs(user_id, changed_at desc);

alter table public.audit_logs enable row level security;
revoke all on public.audit_logs from anon;
grant select on public.audit_logs to authenticated;
create policy "audit_logs_select_authenticated"
on public.audit_logs for select to authenticated
using (public.current_user_role() is not null);

create or replace function public.record_business_audit()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
    actor uuid;
    audit_action text;
begin
    actor := case when tg_op = 'INSERT' then new.created_by else new.updated_by end;
    audit_action := case
        when tg_op = 'INSERT' then 'created'
        when new.archived_at is not null and old.archived_at is null then 'archived'
        else 'updated'
    end;
    insert into public.audit_logs(user_id, entity_type, entity_id, action)
    values (actor, tg_table_name, new.id, audit_action);
    return new;
end;
$$;

do $$
declare table_name text;
begin
    foreach table_name in array array[
        'companies', 'contacts', 'opportunities', 'activities', 'tasks', 'notes'
    ] loop
        execute format('drop trigger if exists %I_audit on public.%I', table_name, table_name);
        execute format(
            'create trigger %I_audit after insert or update on public.%I '
            'for each row execute function public.record_business_audit()',
            table_name,
            table_name
        );
    end loop;
end;
$$;
