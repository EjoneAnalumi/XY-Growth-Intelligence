"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { getApiBaseUrl } from "@/lib/api/client";
import { getAccessToken, getSession } from "@/lib/auth";

export default function DataPage() {
  const [entity, setEntity] = useState("contacts");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const writer = ["admin", "management", "business_development"].includes(getSession()?.profile?.role ?? "");
  async function exchange(importing: boolean) {
    if (importing && !file) return;
    setBusy(true); setError(""); setMessage("");
    try {
      if (file && importing && file.size > 1_000_000) throw new Error("Choose a CSV file no larger than 1 MB.");
      const token = await getAccessToken();
      if (!token) throw new Error("Sign in before exchanging data.");
      const response = await fetch(`${getApiBaseUrl()}/data/${entity}/${importing ? "import" : "export"}`, {
        method: importing ? "POST" : "GET",
        headers: { Authorization: `Bearer ${token}`, ...(importing ? { "Content-Type": "text/csv" } : {}) },
        body: importing ? await file!.arrayBuffer() : undefined,
      });
      if (!response.ok) { const body = await response.json(); throw new Error(typeof body.detail === "string" ? body.detail : "CSV request failed."); }
      if (importing) { const result = await response.json(); setMessage(`${result.created} records imported. Imported records are assigned to you.`); }
      else {
        const url = URL.createObjectURL(await response.blob()); const link = document.createElement("a");
        link.href = url; link.download = `${entity}.csv`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
        setMessage("CSV exported.");
      }
    } catch (caught) { setError(caught instanceof Error ? caught.message : "CSV request failed."); }
    finally { setBusy(false); }
  }
  return <div className="max-w-3xl space-y-5"><h1 className="text-3xl font-semibold">Data exchange</h1>
    <p className="text-sm text-muted-foreground">Use synthetic records only. Export a CSV to obtain the correct columns. Imports append new records; existing company, contact, opportunity, and stage IDs must be valid. Company CSV tools are on Companies. Each import is limited to 1 MB and 1,000 rows.</p>
    <div><Label htmlFor="csv-entity">Record type</Label><select id="csv-entity" className="ml-3 rounded-md border bg-background p-2" value={entity} onChange={(e) => { setEntity(e.target.value); setMessage(""); }}>{["contacts", "opportunities", "activities", "tasks"].map((item) => <option key={item}>{item}</option>)}</select></div>
    <Button disabled={busy} onClick={() => exchange(false)}>Export CSV</Button>
    {writer && <div className="space-y-3 rounded-md border bg-card p-5"><Label htmlFor="csv-file">Synthetic CSV file</Label><input id="csv-file" className="block w-full" type="file" accept=".csv,text/csv" onChange={(e) => setFile(e.target.files?.[0] ?? null)} /><Button disabled={busy || !file} onClick={() => exchange(true)}>Import CSV</Button><p className="text-sm text-muted-foreground">Repeating an import creates additional records. Dates use ISO 8601; list values use |. Spreadsheet formula cells are escaped on export.</p></div>}
    {error && <p role="alert" className="text-destructive">{error}</p>}{message && <p role="status">{message}</p>}
  </div>;
}
