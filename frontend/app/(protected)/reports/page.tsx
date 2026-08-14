"use client";

import { AlertCircle, FileSearch, LoaderCircle, RefreshCw } from "lucide-react";
import { useState } from "react";

import { CyberRiskReportPreview } from "@/components/reports/cyber-risk-report-preview";
import { Button } from "@/components/ui/button";

type PreviewState = "ready" | "loading" | "empty" | "error";

const previewStates: { value: PreviewState; label: string }[] = [
  { value: "ready", label: "Ready" },
  { value: "loading", label: "Loading" },
  { value: "empty", label: "Empty" },
  { value: "error", label: "Error" },
];

export default function ReportsPage() {
  const [previewState, setPreviewState] = useState<PreviewState>("ready");

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-medium text-primary">Reporting</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-normal sm:text-3xl">Reports</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          Review the branded HTML layout using structured, synthetic snapshot data. Approval,
          archival, and download controls will be connected when the report workflow API is ready.
        </p>
      </div>

      <section className="rounded-md border bg-card p-4 shadow-sm sm:p-5" aria-labelledby="preview-controls">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 id="preview-controls" className="font-semibold">Preview state</h2>
            <p className="mt-1 text-sm text-muted-foreground">Use these UI states to verify the report experience before API integration.</p>
          </div>
          <div className="flex flex-wrap gap-2" role="group" aria-label="Preview state selector">
            {previewStates.map((state) => (
              <Button key={state.value} type="button" variant={previewState === state.value ? "default" : "outline"} size="sm" onClick={() => setPreviewState(state.value)}>
                {state.label}
              </Button>
            ))}
          </div>
        </div>
      </section>

      {previewState === "ready" ? <CyberRiskReportPreview /> : null}

      {previewState === "loading" ? (
        <section className="flex min-h-80 flex-col items-center justify-center rounded-md border bg-card px-6 text-center shadow-sm" aria-live="polite">
          <LoaderCircle className="size-8 animate-spin text-primary" aria-hidden="true" />
          <h2 className="mt-4 text-lg font-semibold">Preparing report preview</h2>
          <p className="mt-2 max-w-md text-sm leading-6 text-muted-foreground">Structured scan results, company context, and recommendations are being assembled for review.</p>
        </section>
      ) : null}

      {previewState === "empty" ? (
        <section className="flex min-h-80 flex-col items-center justify-center rounded-md border bg-card px-6 text-center shadow-sm">
          <div className="flex size-11 items-center justify-center rounded-md bg-muted text-primary"><FileSearch className="size-6" aria-hidden="true" /></div>
          <h2 className="mt-4 text-lg font-semibold">No report draft is available</h2>
          <p className="mt-2 max-w-md text-sm leading-6 text-muted-foreground">Generate an approved mock snapshot first. A future report workflow will assemble the preview from its structured evidence.</p>
        </section>
      ) : null}

      {previewState === "error" ? (
        <section className="flex min-h-80 flex-col items-center justify-center rounded-md border border-destructive/30 bg-card px-6 text-center shadow-sm" role="alert">
          <div className="flex size-11 items-center justify-center rounded-md bg-destructive/10 text-destructive"><AlertCircle className="size-6" aria-hidden="true" /></div>
          <h2 className="mt-4 text-lg font-semibold">Report preview could not be prepared</h2>
          <p className="mt-2 max-w-md text-sm leading-6 text-muted-foreground">The preview could not load structured report data. No report has been approved, shared, or downloaded.</p>
          <Button type="button" variant="outline" className="mt-5 gap-2" onClick={() => setPreviewState("loading")}><RefreshCw className="size-4" aria-hidden="true" /> Try again</Button>
        </section>
      ) : null}
    </div>
  );
}
