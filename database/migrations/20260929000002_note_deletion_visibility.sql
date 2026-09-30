-- Personal deletions are durable and isolated from the shared note.
create table public.note_dismissals (
 user_id uuid not null references public.profiles(id) on delete cascade,
 note_id uuid not null references public.notes(id) on delete cascade,
 deleted_at timestamptz not null default now(),
 primary key(user_id,note_id)
);
alter table public.note_dismissals enable row level security;
revoke all on public.note_dismissals from anon,authenticated;
grant select,insert on public.note_dismissals to authenticated;
create policy note_dismissals_own on public.note_dismissals to authenticated
using(user_id=auth.uid() and public.current_user_role() is not null)
with check(user_id=auth.uid() and public.current_user_role() is not null);
-- Shared deletion continues through the trusted API with author/admin checks.
-- Authenticated clients cannot bypass those checks with a direct update/delete.
revoke update,delete on public.notes from authenticated,anon;
