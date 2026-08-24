"use client";

import Link from "next/link";
import { AlertTriangle, CheckCircle2, Clock, FileText, Filter, Radar, ShieldCheck } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { runSnapshotScan } from "@/lib/api/security-scans";
import type {
  ScanSeverity,
  ScanStatus,
  SnapshotRequestValues,
  SnapshotScan,
} from "@/types/security-scan";

const severities: ScanSeverity[] = ["info", "low", "medium", "high"];

const severityStyles: Record<ScanSeverity, string> = {
  info: "bg-muted text-muted-foreground",
  low: "bg-yellow-100 text-yellow-800",
  medium: "bg-orange-100 text-orange-800",
  high: "bg-destructive/10 text-destructive",
};

function prettyStatus(status: ScanStatus) {
  return status.replaceAll("_", " ");
}

function detailsToLines(details: SnapshotScan["results"][number]["details"]) {
  return Object.entries(details).map(([key, value]) => {
    const displayValue = Array.isArray(value) ? value.join(", ") : String(value ?? "none");
    return `${key}: ${displayValue}`;
  });
}

export default function SecurityScansPage() {
  const [values, setValues] = useState<SnapshotRequestValues>({
    companyId: "10000000-0000-4000-8000-000000000001",
    domain: "https://northstar-robotics.example/snapshot",
    approved: true,
    approvalNote: "Approved internal demo target.",
    timeoutSeconds: "1",
  });
  const [status, setStatus] = useState<ScanStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [scan, setScan] = useState<SnapshotScan | null>(null);
  const [severityFilter, setSeverityFilter] = useState<ScanSeverity | "all">("all");

  const filteredResults = useMemo(() => {
    if (!scan) {
      return [];
    }

    if (severityFilter === "all") {
      return scan.results;
    }

    return scan.results.filter((result) => result.severity === severityFilter);
  }, [scan, severityFilter]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!values.domain.trim()) {
      setError("Domain is required.");
      setStatus("failed");
      return;
    }

    if (!values.approved) {
      setError("Confirm approval before running a snapshot check.");
      setStatus("failed");
      return;
    }

    try {
      setError(null);
      setStatus("validating");
      const timeoutSeconds = Number(values.timeoutSeconds || 1);
      setStatus("running");
      setScan(
        await runSnapshotScan({
          companyId: values.companyId,
          domain: values.domain.trim(),
          approved: values.approved,
          approvalNote: values.approvalNote.trim(),
          timeoutSeconds,
        }),
      );
      setStatus("complete");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Snapshot scan failed.");
      setStatus("failed");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-medium text-primary">Cyber Risk Snapshot</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-normal sm:text-3xl">
          Security Scans
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          Confirm scope, run an approved demo snapshot, and inspect structured DNS/TLS findings.
        </p>
      </div>

      <aside className="rounded-md border bg-card p-4 text-sm text-muted-foreground">
        <strong className="text-foreground">What is being scanned?</strong> A company&apos;s explicitly approved public demo domain. The snapshot performs limited DNS/TLS checks; it is not a vulnerability exploit or an internal-network scan. Select the company whose public exposure you are assessing and use only synthetic or authorized targets.
      </aside>

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <form onSubmit={handleSubmit} className="space-y-5 rounded-md border bg-card p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-md bg-muted text-primary">
              <ShieldCheck className="size-5" aria-hidden="true" />
            </div>
            <div>
              <h2 className="font-semibold">Scope Confirmation</h2>
              <p className="text-sm text-muted-foreground">
                Use only approved demo or authorized public targets.
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="company-id">Synthetic company ID</Label>
            <Input
              id="company-id"
              value={values.companyId}
              onChange={(event) =>
                setValues((current) => ({ ...current, companyId: event.target.value }))
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="domain">Domain or URL</Label>
            <Input
              id="domain"
              value={values.domain}
              onChange={(event) =>
                setValues((current) => ({ ...current, domain: event.target.value }))
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="approval-note">Approval evidence</Label>
            <textarea
              id="approval-note"
              className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm"
              value={values.approvalNote}
              onChange={(event) =>
                setValues((current) => ({ ...current, approvalNote: event.target.value }))
              }
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-[1fr_auto] sm:items-end">
            <div className="space-y-2">
              <Label htmlFor="timeout">Timeout seconds</Label>
              <Input
                id="timeout"
                type="number"
                min="0.5"
                max="10"
                step="0.5"
                value={values.timeoutSeconds}
                onChange={(event) =>
                  setValues((current) => ({ ...current, timeoutSeconds: event.target.value }))
                }
              />
            </div>
            <label className="flex min-h-10 items-center gap-2 rounded-md border px-3 text-sm">
              <input
                type="checkbox"
                checked={values.approved}
                onChange={(event) =>
                  setValues((current) => ({ ...current, approved: event.target.checked }))
                }
              />
              Approved
            </label>
          </div>

      {error ? (
        <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          ) : null}

          <Button type="submit" disabled={status === "running"} className="w-full gap-2">
            <Radar className="h-4 w-4" />
            {status === "running" ? "Running scan..." : "Run snapshot scan"}
          </Button>
        </form>

        <section className="rounded-md border bg-card p-5 shadow-sm">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
                {status === "failed" ? (
                  <AlertTriangle className="size-5" />
                ) : status === "complete" ? (
                  <CheckCircle2 className="size-5" />
                ) : (
                  <Clock className="size-5" />
                )}
              </div>
              <div>
                <h2 className="font-semibold">Scan Status</h2>
                <p className="text-sm capitalize text-muted-foreground">{prettyStatus(status)}</p>
              </div>
            </div>

            {scan ? (
              <div className="text-sm text-muted-foreground sm:text-right">
                <p>{scan.domain}</p>
                <p>{scan.durationMs} ms</p>
              </div>
            ) : null}
          </div>

          <div className="mt-5 rounded-md border bg-background p-4">
            <h3 className="text-sm font-semibold">Evidence</h3>
            {scan ? (
              <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-muted-foreground">Approved</dt>
                  <dd>{scan.approved ? "Yes" : "No"}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Checks</dt>
                  <dd>{scan.results.length}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Started</dt>
                  <dd>{scan.startedAt}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Completed</dt>
                  <dd>{scan.completedAt}</dd>
                </div>
              </dl>
            ) : (
              <p className="mt-2 text-sm text-muted-foreground">
                Run an approved scan to capture evidence.
              </p>
            )}
          </div>
          {scan ? (
            <Button asChild className="mt-4 w-full gap-2">
              <Link href={`/reports?security_scan_id=${scan.id}`}>
                <FileText className="size-4" aria-hidden="true" />
                Create report from this snapshot
              </Link>
            </Button>
          ) : null}
        </section>
      </section>

      <section className="rounded-md border bg-card p-5 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-semibold">Findings</h2>
            <p className="text-sm text-muted-foreground">
              Filter structured scan findings by severity.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <label htmlFor="scan-severity-filter" className="sr-only">
              Filter findings by severity
            </label>
            <select
              id="scan-severity-filter"
              className="h-9 rounded-md border bg-background px-3 text-sm"
              value={severityFilter}
              onChange={(event) =>
                setSeverityFilter(event.target.value as ScanSeverity | "all")
              }
            >
              <option value="all">All severities</option>
              {severities.map((severity) => (
                <option key={severity} value={severity}>
                  {severity}
                </option>
              ))}
            </select>
          </div>
        </div>

        {!scan ? (
          <p className="mt-5 rounded-md border bg-background px-4 py-5 text-sm text-muted-foreground">
            No findings yet.
          </p>
        ) : null}

        {scan && filteredResults.length === 0 ? (
          <p className="mt-5 rounded-md border bg-background px-4 py-5 text-sm text-muted-foreground">
            No findings match this severity.
          </p>
        ) : null}

        <div className="mt-5 grid gap-3">
          {filteredResults.map((finding) => (
            <article key={finding.check} className="rounded-md border bg-background p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h3 className="text-sm font-semibold capitalize">{finding.check}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{finding.summary}</p>
                </div>
                <div className="flex gap-2">
                  <span className="rounded-md bg-muted px-2.5 py-1 text-xs text-muted-foreground">
                    {finding.status}
                  </span>
                  <span
                    className={`rounded-md px-2.5 py-1 text-xs ${
                      severityStyles[finding.severity]
                    }`}
                  >
                    {finding.severity}
                  </span>
                </div>
              </div>

              <div className="mt-3 rounded-md bg-muted px-3 py-2">
                {detailsToLines(finding.details).map((line) => (
                  <p key={line} className="text-xs text-muted-foreground">
                    {line}
                  </p>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
