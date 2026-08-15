-- Day 13 durable report persistence, private Storage, and enforced workflow.

ALTER TABLE public.reports
    ADD COLUMN IF NOT EXISTS shared_by uuid REFERENCES public.profiles(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS shared_at timestamptz;
ALTER TABLE public.reports DROP CONSTRAINT IF EXISTS reports_status_check;
ALTER TABLE public.reports ADD CONSTRAINT reports_status_check
    CHECK (status IN ('draft', 'review', 'approved', 'shared', 'archived'));

INSERT INTO storage.buckets (id, name, public)
VALUES ('reports', 'reports', false)
ON CONFLICT (id) DO UPDATE SET public = false;

-- Synthetic identities used exclusively by the existing local FastAPI demo tokens.
INSERT INTO auth.users (id, instance_id, aud, role, email, encrypted_password, email_confirmed_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at) VALUES
('00000000-0000-4000-8000-000000000001','00000000-0000-0000-0000-000000000000','authenticated','authenticated','admin.demo@example.test',crypt('local-demo',gen_salt('bf')),now(),'{"provider":"email","providers":["email"]}'::jsonb,'{}'::jsonb,now(),now()),
('00000000-0000-4000-8000-000000000002','00000000-0000-0000-0000-000000000000','authenticated','authenticated','management.demo@example.test',crypt('local-demo',gen_salt('bf')),now(),'{"provider":"email","providers":["email"]}'::jsonb,'{}'::jsonb,now(),now()),
('00000000-0000-4000-8000-000000000003','00000000-0000-0000-0000-000000000000','authenticated','authenticated','bd.demo@example.test',crypt('local-demo',gen_salt('bf')),now(),'{"provider":"email","providers":["email"]}'::jsonb,'{}'::jsonb,now(),now()),
('00000000-0000-4000-8000-000000000004','00000000-0000-0000-0000-000000000000','authenticated','authenticated','analyst.demo@example.test',crypt('local-demo',gen_salt('bf')),now(),'{"provider":"email","providers":["email"]}'::jsonb,'{}'::jsonb,now(),now()),
('00000000-0000-4000-8000-000000000005','00000000-0000-0000-0000-000000000000','authenticated','authenticated','readonly.demo@example.test',crypt('local-demo',gen_salt('bf')),now(),'{"provider":"email","providers":["email"]}'::jsonb,'{}'::jsonb,now(),now()) ON CONFLICT (id) DO NOTHING;
INSERT INTO public.profiles (id,full_name,role,active) VALUES
('00000000-0000-4000-8000-000000000001','Admin Demo','admin',true),('00000000-0000-4000-8000-000000000002','Management Demo','management',true),('00000000-0000-4000-8000-000000000003','Business Development Demo','business_development',true),('00000000-0000-4000-8000-000000000004','Technical Analyst Demo','technical_analyst',true),('00000000-0000-4000-8000-000000000005','Read Only Demo','read_only',true)
ON CONFLICT (id) DO UPDATE SET role=EXCLUDED.role,active=EXCLUDED.active,full_name=EXCLUDED.full_name;

CREATE TABLE IF NOT EXISTS public.report_files (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id uuid NOT NULL UNIQUE REFERENCES public.reports(id) ON DELETE CASCADE,
    storage_bucket text NOT NULL CHECK (storage_bucket = 'reports'),
    storage_path text NOT NULL UNIQUE,
    content_type text NOT NULL CHECK (content_type = 'application/pdf'),
    size_bytes bigint NOT NULL CHECK (size_bytes > 0),
    created_by uuid REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS report_files_report_id_idx ON public.report_files(report_id);

CREATE OR REPLACE FUNCTION public.report_actor_role() RETURNS text LANGUAGE sql STABLE AS $$
    SELECT COALESCE(NULLIF(current_setting('app.report_actor_role', true), ''), public.current_user_role())
$$;
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
 ELSIF OLD.status='shared' AND NEW.status='archived' AND actor_role IN ('admin','management') THEN NEW.archived_by:=actor_id; NEW.archived_at:=now();
 ELSE RAISE EXCEPTION 'invalid report workflow transition'; END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS reports_enforce_workflow ON public.reports;
CREATE TRIGGER reports_enforce_workflow BEFORE INSERT OR UPDATE ON public.reports FOR EACH ROW EXECUTE FUNCTION public.enforce_report_workflow();

ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_files ENABLE ROW LEVEL SECURITY;
REVOKE INSERT, UPDATE, DELETE ON public.reports, public.report_files FROM authenticated, anon;
GRANT SELECT ON public.reports, public.report_files TO authenticated;
DROP POLICY IF EXISTS "reports_select_authenticated" ON public.reports;
CREATE POLICY "reports_select_authenticated" ON public.reports FOR SELECT TO authenticated USING (public.current_user_role() IS NOT NULL);
DROP POLICY IF EXISTS "reports_insert_author_roles" ON public.reports;
DROP POLICY IF EXISTS "reports_update_author_or_approver_roles" ON public.reports;
DROP POLICY IF EXISTS "report_files_select_approver_roles" ON public.report_files;
CREATE POLICY "report_files_select_approver_roles" ON public.report_files FOR SELECT TO authenticated USING (public.has_any_role(ARRAY['admin','management']));
DROP POLICY IF EXISTS "report_files_select_approver_roles" ON storage.objects;
CREATE POLICY "report_files_select_approver_roles" ON storage.objects FOR SELECT TO authenticated USING (bucket_id='reports' AND public.has_any_role(ARRAY['admin','management']));
DROP POLICY IF EXISTS "report_files_insert_system_roles" ON storage.objects;
