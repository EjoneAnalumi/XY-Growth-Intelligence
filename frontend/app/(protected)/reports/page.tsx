"use client";

import {
  AlertCircle,
  Archive,
  CheckCircle2,
  Download,
  FileText,
  LoaderCircle,
  RefreshCw,
  Send,
  Share2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { CyberRiskReportPreview } from "@/components/reports/cyber-risk-report-preview";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api/client";
import {
  approveReport,
  archiveReport,
  downloadReport,
  generateDemoReport,
  listReports,
  Report,
  submitReportForReview,
  shareReport,
} from "@/lib/api/reports";
import { getMockSession } from "@/lib/auth";

type LoadState = "loading" | "ready" | "error";

const statusStyles = {
  draft: "border-muted bg-muted text-muted-foreground",
  review: "border-orange-300 bg-orange-50 text-orange-800",
  approved: "border-primary/30 bg-primary/10 text-primary",
  shared: "border-sky-300 bg-sky-50 text-sky-800",
  archived: "border-muted bg-muted text-muted-foreground",
};

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [message, setMessage] = useState<string | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const session = getMockSession();
  const canGenerate = ["admin", "technical_analyst", "management"].includes(session?.role ?? "");
  const canApprove = ["admin", "management"].includes(session?.role ?? "");
  const latestReport = useMemo(() => reports[reports.length - 1] ?? null, [reports]);

  useEffect(() => {
    void refreshReports();
  }, []);

  async function refreshReports() {
    try {
      setState("loading");
      setMessage(null);
      const response = await listReports();
      setReports(response.items);
      setState("ready");
    } catch (error) {
      setState("error");
      setMessage(error instanceof ApiError ? error.message : "Reports could not be loaded.");
    }
  }

  async function runAction(actionName: string, action: () => Promise<Report | void>) {
    try {
      setBusyAction(actionName);
      setMessage(null);
      const result = await action();
      if (result) {
        setReports((current) => {
          const exists = current.some((report) => report.id === result.id);
          return exists
            ? current.map((report) => (report.id === result.id ? result : report))
            : [...current, result];
        });
      }
    } catch (error) {
      setMessage(error instanceof ApiError ? error.message : "Report action failed.");
    } finally {
      setBusyAction(null);
    }
  }

  function saveDownload(download: Awaited<ReturnType<typeof downloadReport>>) {
    const binary = atob(download.contentBase64);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    const blob = new Blob([bytes], { type: download.contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = download.filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Reporting</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal sm:text-3xl">Reports</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Generate a synthetic PDF report, submit it for review, approve it with Management, and
            download only after approval.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="outline" className="gap-2" onClick={refreshReports}>
            <RefreshCw className="size-4" aria-hidden="true" />
            Refresh
          </Button>
          <Button
            type="button"
            className="gap-2"
            disabled={!canGenerate || busyAction === "generate"}
            onClick={() => runAction("generate", generateDemoReport)}
          >
            {busyAction === "generate" ? (
              <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
            ) : (
              <FileText className="size-4" aria-hidden="true" />
            )}
            Generate PDF
          </Button>
        </div>
      </div>

      {message ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {message}
        </p>
      ) : null}

      {!canGenerate ? (
        <p className="rounded-md border bg-card px-3 py-2 text-sm text-muted-foreground">
          This role can review report content but cannot generate, approve, archive, or download PDFs.
        </p>
      ) : null}

      {state === "loading" ? (
        <section className="flex min-h-48 items-center justify-center rounded-md border bg-card">
          <LoaderCircle className="size-7 animate-spin text-primary" aria-hidden="true" />
        </section>
      ) : null}

      {state === "error" ? (
        <section className="rounded-md border border-destructive/30 bg-card p-6" role="alert">
          <div className="flex items-center gap-2 font-semibold text-destructive">
            <AlertCircle className="size-5" aria-hidden="true" />
            Reports could not be loaded
          </div>
        </section>
      ) : null}

      {state === "ready" ? (
        <section className="grid gap-4">
          {reports.length === 0 ? (
            <div className="rounded-md border bg-card p-6 text-sm text-muted-foreground">
              No generated reports yet. Use a Technical Analyst or Management demo role to generate
              the synthetic PDF report.
            </div>
          ) : null}

          {reports.map((report) => (
            <article key={report.id} className="rounded-md border bg-card p-4 shadow-sm">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-semibold">{report.title}</h2>
                    <span
                      className={`rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${statusStyles[report.status]}`}
                    >
                      {report.status}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {report.companyName} - {report.domain}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Stored at {report.storageBucket}/{report.storagePath}
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    disabled={report.status !== "draft" || !canGenerate || busyAction === report.id}
                    onClick={() =>
                      runAction(report.id, () => submitReportForReview(report.id))
                    }
                  >
                    <Send className="size-4" aria-hidden="true" />
                    Review
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    disabled={report.status !== "approved" || !canApprove || busyAction === report.id}
                    onClick={() => runAction(report.id, () => shareReport(report.id))}
                  >
                    <Share2 className="size-4" aria-hidden="true" />
                    Share internally
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    className="gap-2"
                    disabled={report.status !== "review" || !canApprove || busyAction === report.id}
                    onClick={() => runAction(report.id, () => approveReport(report.id))}
                  >
                    <CheckCircle2 className="size-4" aria-hidden="true" />
                    Approve
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    disabled={report.status !== "approved" || !canApprove || busyAction === report.id}
                    onClick={() =>
                      runAction(report.id, async () => {
                        saveDownload(await downloadReport(report.id));
                      })
                    }
                  >
                    <Download className="size-4" aria-hidden="true" />
                    Download
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    disabled={report.status !== "shared" || !canApprove || busyAction === report.id}
                    onClick={() => {
                      if (window.confirm("Archive this shared report? It will no longer be downloadable.")) {
                        void runAction(report.id, () => archiveReport(report.id));
                      }
                    }}
                  >
                    <Archive className="size-4" aria-hidden="true" />
                    Archive
                  </Button>
                </div>
              </div>
            </article>
          ))}
        </section>
      ) : null}

      <section aria-labelledby="latest-preview" className="space-y-3">
        <div>
          <h2 id="latest-preview" className="text-lg font-semibold">
            Report preview
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {latestReport
              ? `Latest generated report: ${latestReport.title}`
              : "Static branded preview shown until a report is generated."}
          </p>
        </div>
        <CyberRiskReportPreview />
        {latestReport ? (
          <p className="rounded-md border bg-card px-3 py-2 text-xs text-muted-foreground">
            Backend generated and stored the PDF source for this report at{" "}
            {latestReport.storageBucket}/{latestReport.storagePath}.
          </p>
        ) : null}
      </section>
    </div>
  );
}
