import { ArrowRight } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import type { Company } from "@/types/company";
import type { Opportunity, PipelineStage } from "@/types/opportunity";

type OpportunityTableProps = {
  opportunities: Opportunity[];
  companies: Company[];
  stages: PipelineStage[];
};

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function OpportunityTable({
  opportunities,
  companies,
  stages,
}: OpportunityTableProps) {
  const companyById = new Map(companies.map((company) => [company.id, company.name]));
  const stageById = new Map(stages.map((stage) => [stage.id, stage.name]));

  return (
    <div className="overflow-hidden rounded-md border bg-card shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[920px] border-collapse text-sm">
          <caption className="sr-only">Opportunities pipeline table</caption>
          <thead className="bg-muted text-left text-xs font-medium uppercase text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Opportunity</th>
              <th className="px-4 py-3">Company</th>
              <th className="px-4 py-3">Stage</th>
              <th className="px-4 py-3">Value</th>
              <th className="px-4 py-3">Probability</th>
              <th className="px-4 py-3">Weighted</th>
              <th className="px-4 py-3">Next action</th>
              <th className="px-4 py-3 text-right">Open</th>
            </tr>
          </thead>
          <tbody>
            {opportunities.map((opportunity) => (
              <tr key={opportunity.id} className="border-t">
                <td className="px-4 py-4 font-medium">{opportunity.name}</td>
                <td className="px-4 py-4 text-muted-foreground">
                  {companyById.get(opportunity.companyId) ?? "Unknown company"}
                </td>
                <td className="px-4 py-4">
                  <span className="rounded-md bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                    {stageById.get(opportunity.stageId) ?? "Unknown stage"}
                  </span>
                </td>
                <td className="px-4 py-4">{currencyFormatter.format(opportunity.valueUsd)}</td>
                <td className="px-4 py-4">{opportunity.probability}%</td>
                <td className="px-4 py-4">
                  {currencyFormatter.format(opportunity.weightedValueUsd)}
                </td>
                <td className="max-w-56 truncate px-4 py-4 text-muted-foreground">
                  {opportunity.nextAction || "No next action"}
                </td>
                <td className="px-4 py-4 text-right">
                  <Button asChild variant="outline" size="sm" className="gap-2">
                    <Link href={`/opportunities/${opportunity.id}`}>
                      Details
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
