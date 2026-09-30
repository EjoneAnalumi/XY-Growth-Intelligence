-- Retain existing tasks, but remove assignments that the assignee cannot act on.
update public.tasks set owner_id=null
where owner_id in (select id from public.profiles where role='read_only' or not active);
