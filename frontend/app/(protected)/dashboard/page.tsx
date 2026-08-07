"use client";

import {
  Activity,
  AlertTriangle,
  CalendarClock,
  RefreshCw,
  Target,
  TrendingUp,
} from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { useDashboardSummary } from "@/hooks/use-dashboard-summary";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function formatCurrency(value: number) {
  return currencyFormatter.format(value);
}

export default function DashboardPage() {
  const { summary, loading, error, refreshSummary } = useDashboardSummary();

  const kpis = [
    {
      label: "Open pipeline",
      value: summary ? formatCurrency(summary.pipelineValueUsd) : "-",
      detail: `${summary?.openOpportunities ?? 0} active opportunities`,
      icon: TrendingUp,
    },
    {
      label: "Weighted pipeline",
      value: summary ? formatCurrency(summary.weightedPipelineValueUsd) : "-",
      detail: `${summary?.highPriorityOpportunities ?? 0} high-priority deals`,
      icon: Target,
    },
    {
      label: "Follow-ups",
      value: String(summary?.openTasks ?? 0),
      detail: `${summary?.overdueTasks ?? 0} overdue, ${
        summary?.dueThisWeekTasks ?? 0
      } due this week`,
      icon: CalendarClock,
    },
    {
      label: "Inactive deals",
      value: String(summary?.inactiveOpportunities ?? 0),
      detail: "Open deals needing activity or task coverage",
      icon: AlertTriangle,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Sales workflow</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal sm:text-3xl">
            Growth Intelligence dashboard
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Live summary of pipeline value, scoring priority, follow-up tasks, and inactivity risk.
          </p>
        </div>

        <Button type="button" variant="outline" onClick={refreshSummary} className="w-fit gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {error ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((item) => {
          const Icon = item.icon;

          return (
            <article key={item.label} className="rounded-md border bg-card p-4 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">{item.label}</p>
                  <p className="mt-2 text-2xl font-semibold tracking-normal sm:text-3xl">
                    {loading ? "..." : item.value}
                  </p>
                </div>
                <div className="flex size-10 items-center justify-center rounded-md bg-muted text-primary">
                  <Icon className="size-5" aria-hidden="true" />
                </div>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{item.detail}</p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1fr_0.9fr]">
        <article className="rounded-md border bg-card p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Target className="size-5" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-lg font-semibold tracking-normal">Priority Opportunities</h2>
              <p className="text-sm text-muted-foreground">
                Ranked by ICP score, weighted value, tasks, and inactivity.
              </p>
            </div>
          </div>

          {!loading && summary?.priorityOpportunities.length === 0 ? (
            <p className="mt-4 rounded-md border bg-background px-4 py-3 text-sm text-muted-foreground">
              No active priority opportunities yet.
            </p>
          ) : null}

          <div className="mt-5 space-y-3">
            {summary?.priorityOpportunities.map((opportunity) => (
              <Link
                key={opportunity.opportunityId}
                href={`/opportunities/${opportunity.opportunityId}`}
                className="block rounded-md border bg-background p-4 transition hover:border-primary"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 className="text-sm font-semibold">{opportunity.name}</h3>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {opportunity.stageName} - {opportunity.daysInCurrentStage} days in stage
                    </p>
                  </div>
                  <span className="w-fit rounded-md bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                    Priority {opportunity.priorityScore}
                  </span>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{opportunity.reason}</p>
                <p className="mt-2 text-sm font-medium">
                  {formatCurrency(opportunity.weightedValueUsd)} weighted
                </p>
              </Link>
            ))}
          </div>
        </article>

        <article className="rounded-md border bg-card p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-md bg-muted text-primary">
              <Activity className="size-5" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-lg font-semibold tracking-normal">Pipeline Health</h2>
              <p className="text-sm text-muted-foreground">
                Stage distribution and workflow movement.
              </p>
            </div>
          </div>

          <div className="mt-5 grid gap-3">
            <div className="rounded-md border bg-background p-3">
              <p className="text-sm text-muted-foreground">Average stage duration</p>
              <p className="mt-1 text-2xl font-semibold tracking-normal">
                {loading ? "..." : `${summary?.averageDaysInCurrentStage ?? 0} days`}
              </p>
            </div>
            <div className="rounded-md border bg-background p-3">
              <p className="text-sm text-muted-foreground">Activities recorded</p>
              <p className="mt-1 text-2xl font-semibold tracking-normal">
                {loading ? "..." : summary?.activitiesCount ?? 0}
              </p>
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {summary?.stageSummaries
              .filter((stage) => stage.opportunityCount > 0)
              .map((stage) => (
                <div key={stage.stageId} className="rounded-md border bg-background p-3">
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <p className="font-medium">{stage.stageName}</p>
                    <p className="text-muted-foreground">{stage.opportunityCount}</p>
                  </div>
                  <p className="mt-2 text-xs text-muted-foreground">
                    {formatCurrency(stage.weightedValueUsd)} weighted
                  </p>
                </div>
              ))}
          </div>
        </article>
      </section>
    </div>
  );
}
