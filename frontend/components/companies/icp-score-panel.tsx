"use client";

import { BarChart3, Lightbulb, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { calculateIcpScore } from "@/lib/api/icp";
import type { Company } from "@/types/company";
import type { IcpScore, ServiceRecommendation } from "@/types/icp";

type IcpScorePanelProps = {
  companies: Company[];
};

function formatTier(tier: string) {
  return tier.replaceAll("_", " ");
}

function buildRecommendation(score: IcpScore | null): ServiceRecommendation | null {
  if (!score) {
    return null;
  }

  const positiveRules = score.explanations
    .filter((explanation) => explanation.points > 0)
    .map((explanation) => explanation.ruleId);

  if (positiveRules.includes("regulatory_context") || positiveRules.includes("cloud_usage")) {
    return {
      primary: "Cloud Security Assessment",
      secondary: ["Compliance Readiness Review", "Managed SOC"],
      reason: "The strongest score signals point to regulated cloud and control assurance needs.",
      nextStep: "Schedule a discovery call focused on cloud environment, compliance scope, and evidence gaps.",
    };
  }

  if (positiveRules.includes("industry_fit") || score.score >= 80) {
    return {
      primary: "Cyber Risk Snapshot",
      secondary: ["External Attack Surface Review", "Executive Security Workshop"],
      reason: "The company is a strong-fit prospect and should receive a concise executive risk view.",
      nextStep: "Prepare a scoped snapshot and confirm the approved demo domain before outreach.",
    };
  }

  if (score.score >= 60) {
    return {
      primary: "Security Discovery Workshop",
      secondary: ["Cyber Risk Snapshot", "Compliance Readiness Review"],
      reason: "The prospect has enough fit signals to justify qualification before a technical proposal.",
      nextStep: "Book a qualification workshop and capture budget, timeline, and decision-maker details.",
    };
  }

  return {
    primary: "Nurture Follow-up",
    secondary: ["Introductory Security Briefing"],
    reason: "The current ICP score needs stronger commercial or technical signals before proposal work.",
    nextStep: "Create a low-effort follow-up task and gather missing qualification information.",
  };
}

export default function IcpScorePanel({ companies }: IcpScorePanelProps) {
  const [selectedCompanyId, setSelectedCompanyId] = useState(companies[0]?.id ?? "");
  const [score, setScore] = useState<IcpScore | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedCompany = useMemo(
    () => companies.find((company) => company.id === selectedCompanyId) ?? null,
    [companies, selectedCompanyId],
  );
  const recommendation = buildRecommendation(score);

  useEffect(() => {
    if (!selectedCompanyId && companies.length > 0) {
      setSelectedCompanyId(companies[0].id);
    }
  }, [companies, selectedCompanyId]);

  async function handleCalculate() {
    if (!selectedCompanyId) {
      setError("Select a company before calculating ICP.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await calculateIcpScore(selectedCompanyId);
      setScore(result);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to calculate ICP score.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-md border bg-card p-5 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
              <BarChart3 className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="font-semibold">ICP Score Breakdown</h2>
              <p className="text-sm text-muted-foreground">
                Calculate a deterministic score and review rule contributions.
              </p>
            </div>
          </div>
        </div>

        <div className="flex w-full flex-col gap-3 sm:flex-row lg:w-auto">
          <select
            className="h-10 rounded-md border bg-background px-3 text-sm"
            value={selectedCompanyId}
            onChange={(event) => {
              setSelectedCompanyId(event.target.value);
              setScore(null);
            }}
            disabled={companies.length === 0}
          >
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
          <Button
            type="button"
            onClick={handleCalculate}
            disabled={loading || companies.length === 0}
            className="gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            {loading ? "Calculating..." : "Calculate"}
          </Button>
        </div>
      </div>

      {companies.length === 0 ? (
        <p className="mt-4 rounded-md border bg-background px-4 py-3 text-sm text-muted-foreground">
          Add a company before calculating ICP.
        </p>
      ) : null}

      {error ? (
        <p className="mt-4 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      {score ? (
        <div className="mt-5 grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
          <div className="rounded-md border bg-background p-4">
            <p className="text-sm text-muted-foreground">{selectedCompany?.name}</p>
            <div className="mt-3 flex items-end gap-2">
              <span className="text-4xl font-semibold tracking-normal">{score.score}</span>
              <span className="pb-1 text-sm text-muted-foreground">/ {score.maxScore}</span>
            </div>
            <p className="mt-2 w-fit rounded-md bg-muted px-2.5 py-1 text-xs font-medium capitalize text-muted-foreground">
              {formatTier(score.tier)}
            </p>
            <p className="mt-3 text-xs text-muted-foreground">Calculated {score.calculatedAt}</p>

            {recommendation ? (
              <div className="mt-5 rounded-md border p-3">
                <div className="flex items-center gap-2">
                  <Lightbulb className="h-4 w-4 text-primary" />
                  <h3 className="text-sm font-semibold">Service Recommendation</h3>
                </div>
                <p className="mt-3 text-sm font-medium">{recommendation.primary}</p>
                <p className="mt-2 text-sm text-muted-foreground">{recommendation.reason}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {recommendation.secondary.map((service) => (
                    <span
                      key={service}
                      className="rounded-md bg-muted px-2.5 py-1 text-xs text-muted-foreground"
                    >
                      {service}
                    </span>
                  ))}
                </div>
                <p className="mt-3 text-sm">
                  <span className="font-medium">Next step:</span> {recommendation.nextStep}
                </p>
              </div>
            ) : null}
          </div>

          <div className="rounded-md border bg-background p-4">
            <h3 className="text-sm font-semibold">Rule Contributions</h3>
            <div className="mt-4 space-y-4">
              {score.explanations.map((explanation) => {
                const width = `${Math.round((explanation.points / explanation.maxPoints) * 100)}%`;

                return (
                  <div key={explanation.ruleId}>
                    <div className="flex items-center justify-between gap-3 text-sm">
                      <p className="font-medium">{explanation.label}</p>
                      <p className="text-muted-foreground">
                        {explanation.points}/{explanation.maxPoints}
                      </p>
                    </div>
                    <div className="mt-2 h-2 rounded-full bg-muted">
                      <div className="h-2 rounded-full bg-primary" style={{ width }} />
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {explanation.explanation}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
