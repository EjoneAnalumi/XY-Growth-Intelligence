"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState } from "@/components/ui/async-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiRequest } from "@/lib/api/client";
import { getSession } from "@/lib/auth";

type Service = { id: string; name: string; description: string; active: boolean };
type Stage = { id: string; name: string; sort_order: number; default_probability: number; is_won: boolean; is_lost: boolean };

export default function AdministrationPage() {
  const [weights, setWeights] = useState<Record<string, number>>({});
  const [services, setServices] = useState<Service[]>([]);
  const [stages, setStages] = useState<Stage[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [stageName, setStageName] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const admin = getSession()?.profile?.role === "admin";
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [rules, catalogue, pipeline] = await Promise.all([
        apiRequest<{ weights: Record<string, number> }>("/icp-rules"),
        apiRequest<{ items: Service[] }>("/services"), apiRequest<{ items: Stage[] }>("/pipeline-stages"),
      ]);
      setWeights(rules.weights); setServices(catalogue.items); setStages(pipeline.items);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Configuration could not be loaded."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { if (admin) void load(); }, [admin, load]);
  async function save(path: string, body: unknown, method = "PUT") {
    setBusy(true); setError(""); setMessage("");
    try { await apiRequest(path, { method, body: JSON.stringify(body) }); await load(); setMessage("Configuration saved."); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Configuration could not be saved."); }
    finally { setBusy(false); }
  }
  async function addService(event: FormEvent) { event.preventDefault(); await save("/services", { name, description, active: true }, "POST"); }
  if (!admin) return <p role="alert">Only administrators can manage this configuration.</p>;
  return <div className="space-y-6">
    <div><h1 className="text-3xl font-semibold">Administration</h1><p className="mt-2 text-sm text-muted-foreground">Manage scoring, services, and pipeline stages. Existing ICP results remain unchanged until recalculated.</p><Link href="/users" className="text-primary underline">Users and audit events</Link></div>
    {error && <ErrorState title="Configuration request failed" description={error} onRetry={load} />}
    {message && <p role="status">{message}</p>}
    {loading ? <LoadingState title="Loading configuration..." /> : <>
      <form className="space-y-4 rounded-md border bg-card p-5" onSubmit={(e) => { e.preventDefault(); void save("/icp-rules", { weights }); }}>
        <h2 className="text-xl font-semibold">ICP weights</h2><p className="text-sm text-muted-foreground">All eight weights must total 100. Each existing rule contribution is scaled proportionally and rounded to the nearest whole point.</p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{Object.entries(weights).map(([key, value]) => <div key={key}><Label htmlFor={`weight-${key}`}>{key.replaceAll("_", " ")}</Label><Input id={`weight-${key}`} type="number" required min={1} max={100} value={value} onChange={(e) => setWeights({ ...weights, [key]: Number(e.target.value) })} /></div>)}</div>
        <p>Total: {Object.values(weights).reduce((a, b) => a + b, 0)} / 100</p><Button disabled={busy || Object.values(weights).reduce((a, b) => a + b, 0) !== 100}>Save weights</Button>
      </form>
      <section className="space-y-3 rounded-md border bg-card p-5"><h2 className="text-xl font-semibold">Services</h2>
        <form onSubmit={addService} className="flex flex-wrap items-end gap-3"><div><Label htmlFor="service-name">New service name</Label><Input id="service-name" required maxLength={120} value={name} onChange={(e) => setName(e.target.value)} /></div><div><Label htmlFor="service-description">Description</Label><Input id="service-description" value={description} onChange={(e) => setDescription(e.target.value)} /></div><Button disabled={busy}>Add service</Button></form>
        {services.map((service, index) => <form key={service.id} className="flex flex-wrap items-end gap-3 border-t pt-3" onSubmit={(e) => { e.preventDefault(); void save(`/services/${service.id}`, { name: service.name, description: service.description, active: service.active }); }}>
          <div><Label htmlFor={`service-${service.id}`}>Name</Label><Input id={`service-${service.id}`} required value={service.name} onChange={(e) => setServices(services.map((s, i) => i === index ? { ...s, name: e.target.value } : s))} /></div>
          <div><Label htmlFor={`description-${service.id}`}>Description</Label><Input id={`description-${service.id}`} value={service.description} onChange={(e) => setServices(services.map((s, i) => i === index ? { ...s, description: e.target.value } : s))} /></div>
          <label className="flex min-h-10 items-center gap-2"><input type="checkbox" checked={service.active} onChange={(e) => setServices(services.map((s, i) => i === index ? { ...s, active: e.target.checked } : s))} />Active</label><Button disabled={busy}>Save service</Button>
        </form>)}
      </section>
      <section className="space-y-3 rounded-md border bg-card p-5"><h2 className="text-xl font-semibold">Pipeline stages</h2><p className="text-sm text-muted-foreground">Changing a default probability applies to newly selected stages in opportunity forms. Existing deal probabilities are preserved.</p>
        <form className="flex items-end gap-3" onSubmit={(e) => { e.preventDefault(); void save("/pipeline-stages", { name: stageName, sort_order: Math.max(0, ...stages.map((s) => s.sort_order)) + 10 }, "POST"); }}><div><Label htmlFor="new-stage">New stage</Label><Input id="new-stage" value={stageName} required onChange={(e) => setStageName(e.target.value)} /></div><Button disabled={busy}>Add stage</Button></form>
        {stages.map((stage, index) => <form key={stage.id} className="flex flex-wrap items-end gap-3 border-t pt-3" onSubmit={(e) => { e.preventDefault(); void save(`/pipeline-stages/${stage.id}`, { name: stage.name, sort_order: stage.sort_order, default_probability: stage.default_probability }, "PATCH"); }}>
          <div><Label htmlFor={`stage-${stage.id}`}>Stage name {stage.is_won ? "(Won)" : stage.is_lost ? "(Lost)" : ""}</Label><Input id={`stage-${stage.id}`} value={stage.name} required onChange={(e) => setStages(stages.map((s, i) => i === index ? { ...s, name: e.target.value } : s))} /></div>
          <div><Label htmlFor={`order-${stage.id}`}>Order</Label><Input className="w-24" id={`order-${stage.id}`} type="number" required value={stage.sort_order} onChange={(e) => setStages(stages.map((s, i) => i === index ? { ...s, sort_order: Number(e.target.value) } : s))} /></div>
          <div><Label htmlFor={`probability-${stage.id}`}>Default probability (%)</Label><Input className="w-24" id={`probability-${stage.id}`} type="number" required min={0} max={100} value={stage.default_probability} onChange={(e) => setStages(stages.map((s, i) => i === index ? { ...s, default_probability: Number(e.target.value) } : s))} /></div><Button disabled={busy}>Save stage</Button>
        </form>)}
      </section>
    </>}
  </div>;
}
