import { apiRequest } from "@/lib/api/client";
import type { IcpScore } from "@/types/icp";

type IcpScoreApiResponse = {
  id: string;
  company_id: string;
  score: number;
  max_score: number;
  tier: string;
  explanations: {
    rule_id: string;
    label: string;
    points: number;
    max_points: number;
    explanation: string;
  }[];
  calculated_by: string;
  calculated_at: string;
};

function mapIcpScore(score: IcpScoreApiResponse): IcpScore {
  return {
    id: score.id,
    companyId: score.company_id,
    score: score.score,
    maxScore: score.max_score,
    tier: score.tier,
    explanations: score.explanations.map((explanation) => ({
      ruleId: explanation.rule_id,
      label: explanation.label,
      points: explanation.points,
      maxPoints: explanation.max_points,
      explanation: explanation.explanation,
    })),
    calculatedBy: score.calculated_by,
    calculatedAt: score.calculated_at,
  };
}

export async function calculateIcpScore(companyId: string): Promise<IcpScore> {
  const response = await apiRequest<IcpScoreApiResponse>(`/companies/${companyId}/calculate-icp`, {
    method: "POST",
  });

  return mapIcpScore(response);
}
