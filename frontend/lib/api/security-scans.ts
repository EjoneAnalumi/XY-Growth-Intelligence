import { apiRequest } from "@/lib/api/client";
import type { ScanSeverity, SnapshotScan } from "@/types/security-scan";

type SnapshotCheckApiResponse = {
  check: string;
  status: string;
  summary: string;
  finding: boolean;
  severity: ScanSeverity;
  method: string;
  evidence: string[];
  error_classification: string | null;
  details: Record<string, string | number | boolean | string[] | null>;
};

type SnapshotApiResponse = {
  id: string;
  domain: string;
  approved: boolean;
  started_at: string;
  completed_at: string;
  duration_ms: number;
  results: SnapshotCheckApiResponse[];
};

function mapSnapshotScan(scan: SnapshotApiResponse): SnapshotScan {
  return {
    id: scan.id,
    domain: scan.domain,
    approved: scan.approved,
    startedAt: scan.started_at,
    completedAt: scan.completed_at,
    durationMs: scan.duration_ms,
    results: scan.results.map((result) => ({
      check: result.check,
      status: result.status,
      summary: result.summary,
      severity: result.severity,
      finding: result.finding,
      method: result.method,
      evidence: result.evidence,
      errorClassification: result.error_classification,
      details: result.details,
    })),
  };
}

export async function runSnapshotScan(values: {
  companyId: string;
  domain: string;
  approved: boolean;
  approvalNote: string;
  timeoutSeconds: number;
}): Promise<SnapshotScan> {
  const response = await apiRequest<SnapshotApiResponse>("/security-scans/snapshot", {
    method: "POST",
    body: JSON.stringify({
      domain: values.domain,
      company_id: values.companyId,
      approved: values.approved,
      approval_note: values.approvalNote,
      timeout_seconds: values.timeoutSeconds,
    }),
  });

  return mapSnapshotScan(response);
}
