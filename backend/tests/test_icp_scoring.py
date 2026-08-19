from uuid import UUID

from app.main import app
from app.scoring.icp import IcpScoringEngine
from app.services.growth_repository import repository
from fastapi.testclient import TestClient

client = TestClient(app)

writer_headers = {"Authorization": "Bearer dev-business-development"}
read_only_headers = {"Authorization": "Bearer dev-read-only"}


def setup_function() -> None:
    repository.reset()


def _create_strong_fit_company() -> dict:
    response = client.post(
        "/companies",
        headers=writer_headers,
        json={
            "name": "Blue Harbor Finance",
            "domain": "blueharbor-finance.example",
            "industry": "Financial Services",
            "employee_count": 650,
            "annual_revenue_usd": 75_000_000,
            "headquarters_country": "United States",
            "cloud_usage": ["Azure", "AWS"],
            "regulatory_context": ["PCI DSS", "SOX"],
            "lead_source": "partner referral",
            "status": "qualified",
            "lifecycle_stage": "qualified",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_icp_scoring_engine_is_deterministic_for_same_company_input() -> None:
    company = _create_strong_fit_company()
    company_model = repository.get_company(UUID(company["id"]))

    assert company_model is not None

    first_score = IcpScoringEngine().calculate(company_model)
    second_score = IcpScoringEngine().calculate(company_model)

    assert first_score.score == 100
    assert second_score.score == first_score.score
    assert second_score.tier == first_score.tier
    assert second_score.explanations == first_score.explanations


def test_calculate_icp_stores_score_explanations_and_updates_company_fit_score() -> None:
    company = _create_strong_fit_company()

    response = client.post(
        f"/companies/{company['id']}/calculate-icp",
        headers=writer_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["company_id"] == company["id"]
    assert body["score"] == 100
    assert body["max_score"] == 100
    assert body["tier"] == "strong_fit"
    assert len(body["explanations"]) == 8
    assert body["explanations"][0]["rule_id"] == "industry_fit"

    stored_score = repository.get_latest_icp_score(UUID(company["id"]))
    updated_company = repository.get_company(UUID(company["id"]))

    assert stored_score is not None
    assert stored_score.score == 100
    assert updated_company is not None
    assert updated_company.fit_score == 100


def test_calculate_icp_rejects_read_only_user() -> None:
    company = _create_strong_fit_company()

    response = client.post(
        f"/companies/{company['id']}/calculate-icp",
        headers=read_only_headers,
    )

    assert response.status_code == 403


def test_calculate_icp_returns_not_found_for_unknown_company() -> None:
    response = client.post(
        "/companies/10000000-0000-4000-8000-000000000001/calculate-icp",
        headers=writer_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["detail"] == "Company not found."


def test_openapi_documents_icp_scoring_endpoint() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/companies/{company_id}/calculate-icp" in response.json()["paths"]
