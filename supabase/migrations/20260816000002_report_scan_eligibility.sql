-- Permit persisted scan lifecycle states so report generation can reject ineligible snapshots safely.

ALTER TABLE public.security_scans
    DROP CONSTRAINT IF EXISTS security_scans_approved_check;
ALTER TABLE public.security_scans
    ALTER COLUMN approved SET DEFAULT false;
ALTER TABLE public.security_scans
    DROP CONSTRAINT IF EXISTS security_scans_status_check;
ALTER TABLE public.security_scans
    ADD CONSTRAINT security_scans_status_check
    CHECK (status IN ('pending', 'running', 'completed', 'failed'));
