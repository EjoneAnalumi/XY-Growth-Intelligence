"use client";

import Link from "next/link";
import { formatLocalDateTime } from "@/lib/date-time";
import { useEffect, useRef, useState } from "react";
import { CyberRiskReportPreview } from "@/components/reports/cyber-risk-report-preview";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { approveReport, archiveReport, downloadReport, generateReport, listReports, submitReportForReview, shareReport, type Report } from "@/lib/api/reports";
import { getSession } from "@/lib/auth";

function reportExplanation(status: Report["status"], canPrepare: boolean, canApprove: boolean) {
  if (status === "archived") return "Archived: you can preview this report for reference. No further workflow actions are available.";
  if (!canPrepare) return {
    draft: "Draft: you can preview the findings. The report is not yet reviewed or approved.",
    review: "In review: you can preview the findings while Admin or Management checks the report.",
    approved: "Approved: you can preview the approved findings. Ask Admin or Management if you need the PDF.",
    shared: "Shared: you can preview the findings. This status records internal sharing; no email was sent.",
  }[status];
  if (status === "draft") return "Draft: check the preview, then submit it for review.";
  if (status === "review") return canApprove ? "In review: check the preview, then approve the report when it is ready. Download becomes available after approval." : "Submitted for review: you can preview the findings. Admin or Management must approve the report.";
  if (status === "approved") return canApprove ? "Approved: you can download the PDF, mark it shared internally, or archive it." : "Approved: you can preview the approved findings. Admin or Management handles PDF downloads and sharing.";
  return canApprove ? "Shared internally: you can preview or archive this report. No email was sent; downloads are available only in Approved status." : "Shared internally: you can preview this report. Admin or Management handles sharing and archiving.";
}
export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [scanId, setScanId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [hidden, setHidden] = useState(false);
  const [sort, setSort] = useState("newest");
  const [status, setStatus] = useState("active");
  const [query, setQuery] = useState("");
  const preview = useRef<HTMLElement>(null);
  const focusPreview = useRef(false);
  const role = getSession()?.profile?.role ?? "";
  const canGenerate = ["admin", "management", "technical_analyst"].includes(role);
  const canApprove = ["admin", "management"].includes(role);
  const selected = reports.find((report) => report.id === selectedId);

  async function refresh() {
    setLoading(true); setError("");
    try {
      const items = (await listReports()).items;
      setReports(items);
      const requested = new URLSearchParams(window.location.search).get("report_id");
      const report = items.find((item) => item.id === requested);
      if (report) { focusPreview.current = true; setSelectedId(report.id); setMessage("Your draft report is ready. Preview it below before submitting for review."); }
    }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Reports could not be loaded."); }
    finally { setLoading(false); }
  }
  useEffect(() => { setScanId(new URLSearchParams(window.location.search).get("security_scan_id")); void refresh(); }, []);
  useEffect(() => {
    if (selectedId && focusPreview.current) { preview.current?.scrollIntoView({ behavior: "smooth", block: "start" }); preview.current?.focus({ preventScroll: true }); focusPreview.current = false; }
  }, [selectedId]);
  function openPreview(report: Report) {
    focusPreview.current = true; setSelectedId(report.id);
    setMessage(`Preview opened: ${report.title}`);
    if (selectedId === report.id) { preview.current?.scrollIntoView({ behavior: "smooth" }); preview.current?.focus({ preventScroll: true }); }
  }
  async function action(operation: () => Promise<Report | void>, success: string) {
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await operation();
      if (result) {
        setReports((items) => items.some((item) => item.id === result.id) ? items.map((item) => item.id === result.id ? result : item) : [result, ...items]);
        focusPreview.current = true; setSelectedId(result.id);
      }
      setMessage(success);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Report action failed."); }
    finally { setBusy(false); }
  }
  async function download(report: Report) {
    const result = await downloadReport(report.id);
    const bytes = Uint8Array.from(atob(result.contentBase64), (character) => character.charCodeAt(0));
    const url = URL.createObjectURL(new Blob([bytes], { type: result.contentType }));
    const link = document.createElement("a"); link.href = url; link.download = result.filename; link.click(); URL.revokeObjectURL(url);
  }
  const visible = reports.filter((r) => (status === "all" || (status === "active" ? r.status !== "archived" : r.status === status)) && `${r.title} ${r.companyName} ${r.domain}`.toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => sort === "newest" || sort === "oldest" ? (new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()) * (sort === "oldest" ? -1 : 1) : a.title.localeCompare(b.title) * (sort === "za" ? -1 : 1));
  return <div className="space-y-5">
    <div><h1 className="text-3xl font-semibold">Reports</h1><p className="mt-2 text-sm text-muted-foreground">A report summarizes one security snapshot. Open its preview to read the findings before taking the next action.</p></div>
    <div className="rounded-md border bg-card p-4 text-sm"><p className="font-semibold">{canApprove ? "Prepare, review and approve reports" : canGenerate ? "Prepare reports for review" : "Preview reports"}</p><p className="mt-1">{canApprove ? "You can create drafts, submit them for review, approve reviewed reports, and download approved PDFs. You can also archive active reports." : canGenerate ? "You can create drafts, preview findings and submit reports for review. Admin or Management handles approval, PDF downloads, sharing and archiving." : "You can preview reports and check their status. Report preparation, approval and PDF downloads are handled by the authorized team members."}</p></div>
    <div className="flex flex-wrap gap-2"><Button variant="outline" disabled={busy} onClick={refresh}>Refresh reports</Button><Button variant="outline" aria-expanded={!hidden} aria-controls="report-list" onClick={() => setHidden(!hidden)}>{hidden ? "Show reports" : "Hide reports"}</Button>{canGenerate && (scanId ? <Button disabled={busy} onClick={() => action(() => generateReport(scanId), "Draft generated. Check the preview before submitting for review.")}>Generate from snapshot</Button> : <Button asChild><Link href="/security-scans?create_report=1">Create report from a snapshot</Link></Button>)}</div>
    {!canGenerate && <p className="text-sm text-muted-foreground">Your role can preview reports. Workflow changes and PDF downloads are restricted to the roles described above.</p>}
    {error && <p role="alert" className="rounded-md border border-destructive p-3 text-destructive">{error}</p>}
    {message && <p role="status" className="rounded-md border bg-card p-3 text-sm">{message}</p>}
    {loading && <p role="status">Loading reports...</p>}
    {!hidden && <section id="report-list" aria-label="Report list" className="space-y-3">
      <div className="flex flex-wrap items-center gap-3"><Input aria-label="Search reports" placeholder="Search reports" className="max-w-sm" value={query} onChange={(e) => setQuery(e.target.value)} /><label>Sort reports <select aria-label="Sort reports" className="h-10 rounded-md border bg-background px-3" value={sort} onChange={(e) => setSort(e.target.value)}><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="az">A-Z</option><option value="za">Z-A</option></select></label><label>Status <select aria-label="Report status" className="h-10 rounded-md border bg-background px-3" value={status} onChange={(e) => setStatus(e.target.value)}>{["active", "all", "draft", "review", "approved", "shared", "archived"].map((s) => <option key={s} value={s}>{s === "active" ? "Active reports" : s}</option>)}</select></label></div>
      <p className="text-sm text-muted-foreground">{visible.length} reports. Preview opens the selected report below; Hide reports collapses this list without archiving anything.</p>
      <div className="max-h-[32rem] space-y-3 overflow-y-auto pr-1">
        {!loading && !visible.length && <p className="rounded-md border p-4">No reports match these filters.</p>}
        {visible.map((report) => <article key={report.id} data-report-id={report.id} className={`rounded-md border bg-card p-4 ${selectedId === report.id ? "border-primary ring-1 ring-primary" : ""}`}>
          <div className="flex flex-wrap items-center gap-2"><h2 className="font-semibold">{report.title}</h2><span className="rounded-full bg-muted px-2 py-1 text-xs uppercase">{report.status}</span>{selectedId === report.id && <span className="text-xs text-primary">Preview selected</span>}</div>
          <p className="mt-1 text-sm">{report.companyName} | {report.domain}</p><p className="mt-1 text-xs text-muted-foreground">Created {formatLocalDateTime(report.createdAt)}</p>
          <p className="my-3 text-sm text-muted-foreground">{reportExplanation(report.status, canGenerate, canApprove)} {report.isLegacy && "Legacy report: no linked snapshot."}</p>
          <div className="flex flex-wrap gap-2"><Button variant="outline" size="sm" onClick={() => openPreview(report)}>Preview</Button>
            {canGenerate && report.status === "draft" && <Button size="sm" disabled={busy} onClick={() => action(() => submitReportForReview(report.id), "Submitted for review. Admin or Management can now approve.")}>Submit for review</Button>}
            {canApprove && report.status === "review" && <Button size="sm" disabled={busy} onClick={() => action(() => approveReport(report.id), "Report approved. Its PDF is ready to download.")}>Approve</Button>}
            {canApprove && <Button variant="outline" size="sm" disabled={report.status !== "approved" || busy} title={report.status !== "approved" ? "Download requires Approved status" : "Download approved PDF"} onClick={() => action(() => download(report), "PDF downloaded.")}>Download</Button>}
            {canApprove && report.status === "approved" && <Button variant="outline" size="sm" disabled={busy} onClick={() => action(() => shareReport(report.id), "Marked shared internally; no email was sent.")}>Mark shared internally</Button>}
            {canApprove && report.status !== "archived" && <Button variant="outline" size="sm" disabled={busy} onClick={() => { if (window.confirm(`Archive ${report.title}? The preview will remain available under Archived; downloading will be disabled.`)) void action(() => archiveReport(report.id), "Report archived. Find it with the Archived status filter."); }}>Archive</Button>}
          </div>
        </article>)}
      </div>
    </section>}
    <section ref={preview} tabIndex={-1} aria-labelledby="selected-preview" className="scroll-mt-24 space-y-3 rounded-md border bg-card p-4 focus:outline-primary">
      <h2 id="selected-preview" className="text-xl font-semibold">{selected ? `Report preview: ${selected.title}` : "Report preview"}</h2>
      {selected ? <><p className="text-sm text-muted-foreground">{selected.companyName} | {selected.status} | Created {formatLocalDateTime(selected.createdAt)}</p><CyberRiskReportPreview key={selected.id} htmlPreview={selected.htmlPreview} /></> : <p className="text-sm text-muted-foreground">Choose Preview on a report above. Its title and contents will appear here.</p>}
    </section>
  </div>;
}
