import { apiRequest } from "@/lib/api/client";
import type { ScanSeverity, SnapshotScan } from "@/types/security-scan";

type SnapshotCheckApiResponse = {
  check: string;
  status: string;
  summary: string;
  details: Record<string, string | number | boolean | string[] | null>;
};

type SnapshotApiResponse = {
  domain: string;
  approved: boolean;
  started_at: string;
  completed_at: string;
  duration_ms: number;
  results: SnapshotCheckApiResponse[];
};

function severityForStatus(status: string): ScanSeverity {
  if (status === "fail") {
    return "high";
  }

  if (status === "timeout") {
    return "medium";
  }

  if (status === "warning") {
    return "low";
  }

  return "info";
}

function mapSnapshotScan(scan: SnapshotApiResponse): SnapshotScan {
  return {
    domain: scan.domain,
    approved: scan.approved,
    startedAt: scan.started_at,
    completedAt: scan.completed_at,
    durationMs: scan.duration_ms,
    results: scan.results.map((result) => ({
      check: result.check,
      status: result.status,
      summary: result.summary,
      severity: severityForStatus(result.status),
      details: result.details,
    })),
  };
}

export async function runSnapshotScan(values: {
  domain: string;
  approved: boolean;
  approvalNote: string;
  timeoutSeconds: number;
}): Promise<SnapshotScan> {
  const response = await apiRequest<SnapshotApiResponse>("/security-scans/snapshot", {
    method: "POST",
    body: JSON.stringify({
      domain: values.domain,
      approved: values.approved,
      approval_note: values.approvalNote,
      timeout_seconds: values.timeoutSeconds,
    }),
  });

  return mapSnapshotScan(response);
}
