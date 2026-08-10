"use client";

import { ArrowRight, CalendarClock, MoveRight } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import type { Company } from "@/types/company";
import type { Opportunity, PipelineStage } from "@/types/opportunity";

type OpportunityKanbanProps = {
  opportunities: Opportunity[];
  companies: Company[];
  stages: PipelineStage[];
  onMoveStage: (opportunityId: string, toStageId: string, note: string) => Promise<void>;
};

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function OpportunityKanban({
  opportunities,
  companies,
  stages,
  onMoveStage,
}: OpportunityKanbanProps) {
  const [moveDrafts, setMoveDrafts] = useState<Record<string, { stageId: string; note: string }>>(
    {},
  );
  const [movingId, setMovingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const companyById = useMemo(
    () => new Map(companies.map((company) => [company.id, company.name])),
    [companies],
  );
  const sortedStages = useMemo(
    () => [...stages].sort((first, second) => first.sortOrder - second.sortOrder),
    [stages],
  );

  function updateDraft(opportunityId: string, field: "stageId" | "note", value: string) {
    setMoveDrafts((current) => ({
      ...current,
      [opportunityId]: {
        stageId: current[opportunityId]?.stageId ?? "",
        note: current[opportunityId]?.note ?? "",
        [field]: value,
      },
    }));
  }

  async function handleMove(opportunity: Opportunity) {
    const draft = moveDrafts[opportunity.id];
    const nextStageId = draft?.stageId;

    if (!nextStageId || nextStageId === opportunity.stageId) {
      setError("Select a different stage before moving the opportunity.");
      return;
    }

    try {
      setError(null);
      setMovingId(opportunity.id);
      await onMoveStage(opportunity.id, nextStageId, draft?.note ?? "");
      setMoveDrafts((current) => ({
        ...current,
        [opportunity.id]: { stageId: "", note: "" },
      }));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to move opportunity.");
    } finally {
      setMovingId(null);
    }
  }

  return (
    <div className="space-y-3">
      {error ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <div className="overflow-x-auto pb-2">
        <div className="grid min-w-[1120px] auto-cols-[18rem] grid-flow-col gap-4">
          {sortedStages.map((stage) => {
            const stageOpportunities = opportunities.filter(
              (opportunity) => opportunity.stageId === stage.id,
            );

            return (
              <section key={stage.id} className="rounded-md border bg-card shadow-sm">
                <div className="border-b px-4 py-3">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-sm font-semibold">{stage.name}</h3>
                    <span className="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground">
                      {stageOpportunities.length}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Default probability {stage.defaultProbability}%
                  </p>
                </div>

                <div className="space-y-3 p-3">
                  {stageOpportunities.length === 0 ? (
                    <p className="rounded-md border border-dashed bg-background px-3 py-4 text-sm text-muted-foreground">
                      No opportunities in this stage.
                    </p>
                  ) : null}

                  {stageOpportunities.map((opportunity) => {
                    const draft = moveDrafts[opportunity.id] ?? { stageId: "", note: "" };

                    return (
                      <article key={opportunity.id} className="rounded-md border bg-background p-3">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h4 className="text-sm font-semibold">{opportunity.name}</h4>
                            <p className="mt-1 text-xs text-muted-foreground">
                              {companyById.get(opportunity.companyId) ?? "Unknown company"}
                            </p>
                          </div>
                          <Button asChild variant="ghost" size="icon" aria-label="Open opportunity">
                            <Link href={`/opportunities/${opportunity.id}`}>
                              <ArrowRight className="h-4 w-4" />
                            </Link>
                          </Button>
                        </div>

                        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                          <div className="rounded-md bg-muted px-2 py-1">
                            {currencyFormatter.format(opportunity.valueUsd)}
                          </div>
                          <div className="rounded-md bg-muted px-2 py-1">
                            {opportunity.probability}% probability
                          </div>
                        </div>

                        <p className="mt-3 line-clamp-2 text-xs text-muted-foreground">
                          {opportunity.nextAction || "No next action set."}
                        </p>
                        {opportunity.nextActionDueAt ? (
                          <p className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
                            <CalendarClock className="h-3.5 w-3.5" />
                            {opportunity.nextActionDueAt}
                          </p>
                        ) : null}

                        <div className="mt-3 space-y-2">
                          <select
                            className="h-9 w-full rounded-md border bg-background px-2 text-xs"
                            value={draft.stageId}
                            onChange={(event) =>
                              updateDraft(opportunity.id, "stageId", event.target.value)
                            }
                          >
                            <option value="">Move to stage</option>
                            {sortedStages
                              .filter((targetStage) => targetStage.id !== opportunity.stageId)
                              .map((targetStage) => (
                                <option key={targetStage.id} value={targetStage.id}>
                                  {targetStage.name}
                                </option>
                              ))}
                          </select>
                          <input
                            className="h-9 w-full rounded-md border bg-background px-2 text-xs"
                            value={draft.note}
                            onChange={(event) =>
                              updateDraft(opportunity.id, "note", event.target.value)
                            }
                            placeholder="Movement note"
                          />
                          <Button
                            type="button"
                            size="sm"
                            className="w-full gap-2"
                            disabled={movingId === opportunity.id}
                            onClick={() => handleMove(opportunity)}
                          >
                            <MoveRight className="h-4 w-4" />
                            {movingId === opportunity.id ? "Moving..." : "Move"}
                          </Button>
                        </div>
                      </article>
                    );
                  })}
                </div>
              </section>
            );
          })}
        </div>
      </div>
    </div>
  );
}
