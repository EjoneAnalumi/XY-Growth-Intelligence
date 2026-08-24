"use client";

import { ArrowLeft, Pencil } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import ActivityTaskPanel from "@/components/opportunities/activity-task-panel";
import OpportunityForm from "@/components/opportunities/opportunity-form";
import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState } from "@/components/ui/async-state";
import { useCompanies } from "@/hooks/use-companies";
import { useContacts } from "@/hooks/use-contacts";
import { usePipelineStages } from "@/hooks/use-pipeline-stages";
import {
  archiveOpportunity,
  getOpportunity,
  getOpportunityStageHistory,
  opportunityToFormValues,
  updateOpportunity,
} from "@/lib/api/opportunities";
import type {
  Opportunity,
  OpportunityFormValues,
  OpportunityStageHistory,
} from "@/types/opportunity";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function OpportunityDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const opportunityId = params.id;
  const { companies } = useCompanies();
  const { contacts } = useContacts();
  const { stages } = usePipelineStages();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [stageHistory, setStageHistory] = useState<OpportunityStageHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const loadOpportunity = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [opportunityResponse, historyResponse] = await Promise.all([
        getOpportunity(opportunityId),
        getOpportunityStageHistory(opportunityId),
      ]);

      setOpportunity(opportunityResponse);
      setStageHistory(historyResponse);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to load opportunity");
    } finally {
      setLoading(false);
    }
  }, [opportunityId]);

  useEffect(() => {
    void loadOpportunity();
  }, [loadOpportunity]);

  const companyById = useMemo(
    () => new Map(companies.map((company) => [company.id, company.name])),
    [companies],
  );
  const contactById = useMemo(
    () =>
      new Map(
        contacts.map((contact) => [contact.id, `${contact.firstName} ${contact.lastName}`]),
      ),
    [contacts],
  );
  const stageById = useMemo(
    () => new Map(stages.map((stage) => [stage.id, stage.name])),
    [stages],
  );

  async function handleUpdate(values: OpportunityFormValues) {
    try {
      setSubmitError(null);
      const updated = await updateOpportunity(opportunityId, values);
      const history = await getOpportunityStageHistory(opportunityId);
      setOpportunity(updated);
      setStageHistory(history);
      setIsEditing(false);
    } catch (caughtError) {
      setSubmitError(
        caughtError instanceof Error ? caughtError.message : "Failed to update opportunity."
      );
    }
  }

  if (loading) {
    return <LoadingState title="Loading opportunity..." />;
  }

  if (error || !opportunity) {
    return (
      <div className="space-y-4">
        <Button asChild variant="outline">
          <Link href="/opportunities">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Opportunities
          </Link>
        </Button>
        <ErrorState
          title="Opportunity could not be loaded"
          description={error ?? "Opportunity not found."}
          onRetry={loadOpportunity}
        />
      </div>
    );
  }

  const fields = [
    ["Company", companyById.get(opportunity.companyId) ?? "Unknown company"],
    ["Contact", opportunity.contactId ? contactById.get(opportunity.contactId) ?? "Unknown contact" : "None"],
    ["Stage", stageById.get(opportunity.stageId) ?? "Unknown stage"],
    ["Service", opportunity.service || "Not set"],
    ["Value", currencyFormatter.format(opportunity.valueUsd)],
    ["Probability", `${opportunity.probability}%`],
    ["Weighted Value", currencyFormatter.format(opportunity.weightedValueUsd)],
    ["Days in Current Stage", String(opportunity.daysInCurrentStage)],
    ["Current Stage Entered", opportunity.currentStageEnteredAt || "Not set"],
    ["Expected Close", opportunity.expectedCloseDate || "Not set"],
    ["Need", opportunity.need || "Not set"],
    ["Blockers", opportunity.blockers || "None"],
    ["Competitor", opportunity.competitor || "None"],
    ["Next Action", opportunity.nextAction || "Not set"],
    ["Next Action Due", opportunity.nextActionDueAt || "Not set"],
    ["Lost Reason", opportunity.lostReason || "None"],
  ];

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Button asChild variant="outline" size="sm">
            <Link href="/opportunities">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Opportunities
            </Link>
          </Button>
          <p className="mt-5 text-sm font-medium text-primary">Opportunity Detail</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal sm:text-3xl">
            {opportunity.name}
          </h1>
        </div>

        <div className="flex gap-2">
          <Button type="button" onClick={() => setIsEditing((current) => !current)} className="gap-2">
            <Pencil className="h-4 w-4" />
            {isEditing ? "Close edit" : "Edit"}
          </Button>
          <Button type="button" variant="outline" onClick={async () => {
            if (!window.confirm(`Archive ${opportunity.name}?`)) return;
            await archiveOpportunity(opportunity.id);
            router.push("/opportunities");
          }}>Archive</Button>
        </div>
      </div>

      {isEditing ? (
        <OpportunityForm
          companies={companies}
          contacts={contacts}
          stages={stages}
          initialValues={opportunityToFormValues(opportunity)}
          submitLabel="Save changes"
          onSubmit={handleUpdate}
        />
      ) : null}

      {submitError ? (
        <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {submitError}
        </p>
      ) : null}

      <section className="rounded-md border bg-card p-5 shadow-sm">
        <h2 className="font-semibold">Fields</h2>
        <dl className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {fields.map(([label, value]) => (
            <div key={label} className="rounded-md border bg-background p-3">
              <dt className="text-xs font-medium uppercase text-muted-foreground">{label}</dt>
              <dd className="mt-1 text-sm">{value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <ActivityTaskPanel opportunity={opportunity} companies={companies} contacts={contacts} />

      <section className="rounded-md border bg-card p-5 shadow-sm">
        <h2 className="font-semibold">Stage History</h2>
        {stageHistory.length === 0 ? (
          <p className="mt-3 text-sm text-muted-foreground">No stage changes recorded yet.</p>
        ) : (
          <div className="mt-4 space-y-3">
            {stageHistory.map((history) => (
              <div key={history.id} className="rounded-md border bg-background p-3 text-sm">
                <p className="font-medium">
                  {history.fromStageId ? stageById.get(history.fromStageId) : "No previous stage"}{" "}
                  to {stageById.get(history.toStageId) ?? "Unknown stage"}
                </p>
                <p className="mt-1 text-muted-foreground">{history.note ?? "No note"}</p>
                <p className="mt-1 text-xs text-muted-foreground">{history.changedAt}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
