from dataclasses import dataclass

from app.schemas.companies import CompanyResponse
from app.schemas.icp import IcpRuleExplanation


@dataclass(frozen=True)
class IcpScore:
    score: int
    max_score: int
    tier: str
    explanations: list[IcpRuleExplanation]


class IcpScoringEngine:
    max_score = 100

    def calculate(self, company: CompanyResponse) -> IcpScore:
        explanations = [
            self._score_industry(company),
            self._score_company_size(company),
            self._score_revenue(company),
            self._score_regulatory_context(company),
            self._score_cloud_usage(company),
            self._score_country(company),
            self._score_lead_source(company),
            self._score_lifecycle(company),
        ]
        score = sum(item.points for item in explanations)
        return IcpScore(
            score=score,
            max_score=self.max_score,
            tier=self._tier(score),
            explanations=explanations,
        )

    def _score_industry(self, company: CompanyResponse) -> IcpRuleExplanation:
        industry = (company.industry or "").lower()
        high_fit = {"financial services", "healthcare", "energy"}
        medium_fit = {
            "biotechnology",
            "cloud services",
            "legal services",
            "manufacturing technology",
        }

        if industry in high_fit:
            points = 25
            reason = f"{company.industry} is a highly regulated target industry."
        elif industry in medium_fit:
            points = 18
            reason = f"{company.industry} has meaningful security and compliance pressure."
        elif industry:
            points = 10
            reason = f"{company.industry} is relevant but not a top ICP industry."
        else:
            points = 0
            reason = "Industry is missing, so industry fit cannot be confirmed."

        return self._explanation("industry_fit", "Industry fit", points, 25, reason)

    def _score_company_size(self, company: CompanyResponse) -> IcpRuleExplanation:
        employee_count = company.employee_count

        if employee_count is None:
            points = 5
            reason = "Employee count is missing, so size confidence is limited."
        elif employee_count >= 500:
            points = 20
            reason = "Company has enterprise scale and likely security complexity."
        elif employee_count >= 100:
            points = 16
            reason = "Company is mid-market or growth-stage with enough complexity."
        elif employee_count >= 50:
            points = 10
            reason = "Company has some scale but may have limited security budget."
        else:
            points = 4
            reason = "Company is small, which lowers current ICP fit."

        return self._explanation("company_size", "Company size", points, 20, reason)

    def _score_revenue(self, company: CompanyResponse) -> IcpRuleExplanation:
        revenue = company.annual_revenue_usd

        if revenue is None:
            points = 5
            reason = "Revenue is missing, so budget fit is uncertain."
        elif revenue >= 50_000_000:
            points = 15
            reason = "Revenue suggests budget capacity for security services."
        elif revenue >= 20_000_000:
            points = 11
            reason = "Revenue suggests possible budget for a focused engagement."
        elif revenue >= 5_000_000:
            points = 7
            reason = "Revenue is moderate, so deal size should be qualified early."
        else:
            points = 2
            reason = "Revenue is low for the target ICP."

        return self._explanation("revenue_fit", "Revenue fit", points, 15, reason)

    def _score_regulatory_context(self, company: CompanyResponse) -> IcpRuleExplanation:
        contexts = {item.lower() for item in company.regulatory_context}
        strong_signals = {"pci dss", "hipaa", "sox", "nerc cip", "itar", "iso 27001", "soc 2"}
        matches = sorted(contexts.intersection(strong_signals))

        if len(matches) >= 2:
            points = 15
            reason = f"Multiple compliance drivers are present: {', '.join(matches)}."
        elif len(matches) == 1:
            points = 11
            reason = f"Compliance driver present: {matches[0]}."
        else:
            points = 0
            reason = "No strong compliance driver is recorded."

        return self._explanation(
            "regulatory_context",
            "Regulatory context",
            points,
            15,
            reason,
        )

    def _score_cloud_usage(self, company: CompanyResponse) -> IcpRuleExplanation:
        cloud_usage = {item.lower() for item in company.cloud_usage}

        if len(cloud_usage) >= 2:
            points = 10
            reason = "Multiple cloud environments increase security complexity."
        elif len(cloud_usage) == 1:
            points = 7
            reason = "Cloud usage creates a clear security review surface."
        else:
            points = 0
            reason = "No cloud usage is recorded."

        return self._explanation("cloud_usage", "Cloud usage", points, 10, reason)

    def _score_country(self, company: CompanyResponse) -> IcpRuleExplanation:
        country = (company.headquarters_country or "").lower()

        if country in {"united states", "usa", "germany", "united kingdom", "uk"}:
            points = 5
            reason = "Company is in a supported commercial geography."
        elif country:
            points = 2
            reason = "Company has a known geography but not a priority market."
        else:
            points = 0
            reason = "Headquarters country is missing."

        return self._explanation("geography", "Geography", points, 5, reason)

    def _score_lead_source(self, company: CompanyResponse) -> IcpRuleExplanation:
        lead_source = (company.lead_source or "").lower()

        if lead_source in {"partner referral", "web inquiry", "conference", "industry event"}:
            points = 5
            reason = "Lead source indicates stronger commercial intent."
        elif lead_source:
            points = 2
            reason = "Lead source is known but not a high-intent channel."
        else:
            points = 0
            reason = "Lead source is missing."

        return self._explanation("lead_source", "Lead source", points, 5, reason)

    def _score_lifecycle(self, company: CompanyResponse) -> IcpRuleExplanation:
        if company.lifecycle_stage == "qualified" or company.status == "qualified":
            points = 5
            reason = "Company is already marked as qualified."
        elif company.lifecycle_stage == "prospect" or company.status == "prospect":
            points = 3
            reason = "Company is an active prospect."
        else:
            points = 0
            reason = "Company is not currently an active qualified prospect."

        return self._explanation("lifecycle", "Lifecycle signal", points, 5, reason)

    def _tier(self, score: int) -> str:
        if score >= 80:
            return "strong_fit"
        if score >= 60:
            return "good_fit"
        if score >= 40:
            return "possible_fit"
        return "low_fit"

    def _explanation(
        self,
        rule_id: str,
        label: str,
        points: int,
        max_points: int,
        explanation: str,
    ) -> IcpRuleExplanation:
        return IcpRuleExplanation(
            rule_id=rule_id,
            label=label,
            points=points,
            max_points=max_points,
            explanation=explanation,
        )
