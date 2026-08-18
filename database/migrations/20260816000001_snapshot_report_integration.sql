
CREATE TABLE IF NOT EXISTS public.security_scans (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    initiated_by uuid REFERENCES public.profiles(id) ON DELETE SET NULL,
    domain text NOT NULL,
    approval_note text NOT NULL CHECK (char_length(approval_note) BETWEEN 5 AND 500),
    approved boolean NOT NULL DEFAULT true CHECK (approved),
    status text NOT NULL DEFAULT 'completed' CHECK (status = 'completed'),
    started_at timestamptz NOT NULL,
    completed_at timestamptz NOT NULL,
    duration_ms integer NOT NULL CHECK (duration_ms >= 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (completed_at >= started_at)
);

CREATE TABLE IF NOT EXISTS public.security_findings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    security_scan_id uuid NOT NULL REFERENCES public.security_scans(id) ON DELETE CASCADE,
    check_name text NOT NULL,
    status text NOT NULL CHECK (status IN ('pass', 'fail', 'observation', 'error', 'timeout', 'skipped')),
    summary text NOT NULL,
    finding boolean NOT NULL DEFAULT false,
    severity text NOT NULL CHECK (severity IN ('info', 'low', 'medium', 'high')),
    method text NOT NULL DEFAULT '',
    evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
    error_classification text,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (security_scan_id, check_name),
    CHECK ((finding AND severity <> 'info') OR (NOT finding AND severity = 'info'))
);

CREATE INDEX IF NOT EXISTS security_scans_company_id_idx ON public.security_scans(company_id);
CREATE INDEX IF NOT EXISTS security_findings_scan_id_idx ON public.security_findings(security_scan_id);

ALTER TABLE public.reports DROP CONSTRAINT IF EXISTS reports_security_scan_id_fkey;
ALTER TABLE public.reports
    ADD CONSTRAINT reports_security_scan_id_fkey
    FOREIGN KEY (security_scan_id) REFERENCES public.security_scans(id) ON DELETE RESTRICT;

ALTER TABLE public.security_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_findings ENABLE ROW LEVEL SECURITY;
REVOKE INSERT, UPDATE, DELETE ON public.security_scans, public.security_findings FROM authenticated, anon;
GRANT SELECT ON public.security_scans, public.security_findings TO authenticated;
CREATE POLICY "security_scans_select_authenticated" ON public.security_scans
    FOR SELECT TO authenticated USING (public.current_user_role() IS NOT NULL);
CREATE POLICY "security_findings_select_authenticated" ON public.security_findings
    FOR SELECT TO authenticated USING (public.current_user_role() IS NOT NULL);
