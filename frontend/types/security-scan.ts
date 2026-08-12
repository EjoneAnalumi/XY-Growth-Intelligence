export type ScanSeverity = "info" | "low" | "medium" | "high";
export type ScanStatus = "idle" | "validating" | "running" | "complete" | "failed";

export type SnapshotCheckResult = {
  check: string;
  status: string;
  summary: string;
  severity: ScanSeverity;
  details: Record<string, string | number | boolean | string[] | null>;
};

export type SnapshotScan = {
  domain: string;
  approved: boolean;
  startedAt: string;
  completedAt: string;
  durationMs: number;
  results: SnapshotCheckResult[];
};

export type SnapshotRequestValues = {
  domain: string;
  approved: boolean;
  approvalNote: string;
  timeoutSeconds: string;
};
