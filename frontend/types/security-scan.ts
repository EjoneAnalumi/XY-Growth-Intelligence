export type ScanSeverity = "info" | "low" | "medium" | "high";
export type ScanStatus = "idle" | "validating" | "running" | "complete" | "failed";

export type SnapshotCheckResult = {
  check: string;
  status: string;
  summary: string;
  severity: ScanSeverity;
  finding: boolean;
  method: string;
  evidence: string[];
  errorClassification: string | null;
  details: Record<string, string | number | boolean | string[] | null>;
};

export type SnapshotScan = {
  id: string;
  domain: string;
  approved: boolean;
  startedAt: string;
  completedAt: string;
  durationMs: number;
  results: SnapshotCheckResult[];
};

export type SnapshotRequestValues = {
  companyId: string;
  domain: string;
  approved: boolean;
  approvalNote: string;
  timeoutSeconds: string;
};
