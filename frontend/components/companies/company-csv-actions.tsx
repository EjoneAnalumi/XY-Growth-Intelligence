"use client";

import { ChangeEvent, useState } from "react";
import { Download, Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api/client";
import { exportCompaniesCsv, importCompaniesCsv } from "@/lib/api/companies";

type CompanyCsvActionsProps = {
  onImportComplete: () => Promise<void>;
};

type Feedback = { tone: "error" | "success"; message: string } | null;

function csvErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return "These companies already exist. No records were imported.";
    }
    if (error.status === 422) {
      return "The CSV could not be validated. Check its headers and rows, then try again.";
    }
    if (error.status === 403) {
      return "You do not have permission to import company data.";
    }
  }
  return "The CSV action could not be completed. Please try again.";
}

function isCsvFile(file: File): boolean {
  return file.name.toLowerCase().endsWith(".csv") && (!file.type || file.type.includes("csv"));
}

export default function CompanyCsvActions({ onImportComplete }: CompanyCsvActionsProps) {
  const [file, setFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [feedback, setFeedback] = useState<Feedback>(null);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0] ?? null;
    setFeedback(null);
    if (!selectedFile) {
      setFile(null);
      return;
    }
    if (!isCsvFile(selectedFile)) {
      setFile(null);
      event.target.value = "";
      setFeedback({ tone: "error", message: "Choose a UTF-8 .csv file." });
      return;
    }
    setFile(selectedFile);
  }

  async function handleImport() {
    if (!file) return;
    setImporting(true);
    setFeedback(null);
    try {
      const created = await importCompaniesCsv(file);
      await onImportComplete();
      setFile(null);
      setFeedback({
        tone: "success",
        message: `${created} ${created === 1 ? "company" : "companies"} imported successfully.`,
      });
    } catch (error) {
      setFeedback({ tone: "error", message: csvErrorMessage(error) });
    } finally {
      setImporting(false);
    }
  }

  async function handleExport() {
    setExporting(true);
    setFeedback(null);
    try {
      const { blob, filename } = await exportCompaniesCsv();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename || "companies.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setFeedback({ tone: "success", message: "Company CSV download started." });
    } catch (error) {
      setFeedback({ tone: "error", message: csvErrorMessage(error) });
    } finally {
      setExporting(false);
    }
  }

  const busy = importing || exporting;

  return (
    <section aria-labelledby="company-csv-heading" className="rounded-md border bg-card p-4 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-1">
          <h2 id="company-csv-heading" className="font-semibold">Company CSV</h2>
          <p className="text-sm text-muted-foreground">
            Import synthetic company data or export the current company list.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="space-y-1">
            <label htmlFor="company-csv-file" className="text-sm font-medium">CSV file</label>
            <input
              id="company-csv-file"
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
              disabled={busy}
              className="block max-w-full text-sm file:mr-3 file:rounded-md file:border-0 file:bg-muted file:px-3 file:py-2 file:text-sm file:font-medium hover:file:bg-muted/80"
            />
          </div>
          <Button type="button" onClick={handleImport} disabled={!file || busy} className="gap-2">
            <Upload className="h-4 w-4" aria-hidden="true" />
            {importing ? "Importing..." : "Import CSV"}
          </Button>
          <Button type="button" variant="outline" onClick={handleExport} disabled={busy} className="gap-2">
            <Download className="h-4 w-4" aria-hidden="true" />
            {exporting ? "Exporting..." : "Export CSV"}
          </Button>
        </div>
      </div>
      {file ? <p className="mt-3 text-sm text-muted-foreground">Selected: {file.name}</p> : null}
      {feedback ? (
        <p
          role="status"
          aria-live="polite"
          className={`mt-3 rounded-md px-3 py-2 text-sm ${
            feedback.tone === "error"
              ? "border border-destructive/30 bg-destructive/10 text-destructive"
              : "bg-primary/10 text-primary"
          }`}
        >
          {feedback.message}
        </p>
      ) : null}
    </section>
  );
}
