export type IcpRuleExplanation = {
  ruleId: string;
  label: string;
  points: number;
  maxPoints: number;
  explanation: string;
};

export type IcpScore = {
  id: string;
  companyId: string;
  score: number;
  maxScore: number;
  tier: string;
  explanations: IcpRuleExplanation[];
  calculatedBy: string;
  calculatedAt: string;
};

export type ServiceRecommendation = {
  primary: string;
  secondary: string[];
  reason: string;
  nextStep: string;
};
