"use client";

import { Plus, Target } from "lucide-react";
import { useState } from "react";

import OpportunityForm from "@/components/opportunities/opportunity-form";
import OpportunityTable from "@/components/opportunities/opportunity-table";
import { Button } from "@/components/ui/button";
import { useCompanies } from "@/hooks/use-companies";
import { useContacts } from "@/hooks/use-contacts";
import { useOpportunities } from "@/hooks/use-opportunities";
import { usePipelineStages } from "@/hooks/use-pipeline-stages";
import { createOpportunity } from "@/lib/api/opportunities";
import type { Opportunity, OpportunityFormValues } from "@/types/opportunity";

export default function OpportunitiesPage() {
  const { companies, loading: companiesLoading, error: companiesError } = useCompanies();
  const { contacts } = useContacts();
  const { stages, loading: stagesLoading, error: stagesError } = usePipelineStages();
  const { opportunities, loading, error, setOpportunities } = useOpportunities();
  const [showForm, setShowForm] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function handleCreateOpportunity(values: OpportunityFormValues) {
    try {
      setSubmitError(null);
      const opportunity: Opportunity = await createOpportunity(values);
      setOpportunities((current) => [...current, opportunity]);
      setShowForm(false);
    } catch (caughtError) {
      setSubmitError(
        caughtError instanceof Error ? caughtError.message : "Failed to create opportunity."
      );
    }
  }

  const setupLoading = companiesLoading || stagesLoading;
  const setupError = companiesError || stagesError;
  const canCreate = companies.length > 0 && stages.length > 0;

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">Pipeline</p>
        <div className="mt-1 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">
              Opportunities
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              Create, review, and edit opportunities from the published FastAPI contract.
            </p>
          </div>

          <Button
            type="button"
            onClick={() => setShowForm((current) => !current)}
            className="w-fit gap-2"
            disabled={!canCreate}
          >
            <Plus className="h-4 w-4" />
            New Opportunity
          </Button>
        </div>
      </div>

      {!canCreate && !setupLoading ? (
        <p className="rounded-md border bg-card px-4 py-3 text-sm text-muted-foreground">
          Create at least one company before creating an opportunity.
        </p>
      ) : null}

      {setupError ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {setupError}
        </p>
      ) : null}

      {showForm ? (
        <OpportunityForm
          companies={companies}
          contacts={contacts}
          stages={stages}
          submitLabel="Create opportunity"
          onSubmit={handleCreateOpportunity}
        />
      ) : null}

      {submitError ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {submitError}
        </p>
      ) : null}

      <section className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
            <Target className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="font-semibold">Opportunity Table</h2>
            <p className="text-sm text-muted-foreground">Opportunities loaded from FastAPI.</p>
          </div>
        </div>

        {loading ? <p className="text-sm text-muted-foreground">Loading opportunities...</p> : null}

        {error ? <p className="text-sm text-red-500">{error}</p> : null}

        {!loading && !error && opportunities.length === 0 ? (
          <p className="rounded-md border bg-card px-4 py-5 text-sm text-muted-foreground">
            No opportunities found.
          </p>
        ) : null}

        {!loading && !error && opportunities.length > 0 ? (
          <OpportunityTable opportunities={opportunities} companies={companies} stages={stages} />
        ) : null}
      </section>
    </div>
  );
}
