from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IcpRuleExplanation(BaseModel):
    rule_id: str
    label: str
    points: int
    max_points: int
    explanation: str


class IcpScoreResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "90000000-0000-4000-8000-000000000001",
                    "company_id": "10000000-0000-4000-8000-000000000001",
                    "score": 88,
                    "max_score": 100,
                    "tier": "strong_fit",
                    "explanations": [
                        {
                            "rule_id": "industry_fit",
                            "label": "Industry fit",
                            "points": 25,
                            "max_points": 25,
                            "explanation": (
                                "Financial Services is a highly regulated target industry."
                            ),
                        }
                    ],
                    "calculated_by": "00000000-0000-4000-8000-000000000003",
                    "calculated_at": "2026-08-06T09:00:00Z",
                }
            ]
        }
    )

    id: UUID
    company_id: UUID
    score: int
    max_score: int = 100
    tier: str
    explanations: list[IcpRuleExplanation]
    calculated_by: UUID
    calculated_at: datetime
