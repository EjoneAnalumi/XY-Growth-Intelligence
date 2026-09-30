from datetime import UTC, datetime, timedelta

import pytest
from app.core.config import Settings
from app.main import app
from app.services.administration import DEFAULT_WEIGHTS, administration_repository
from app.services.growth_repository import repository
from app.services.pipeline_repository import pipeline_repository
from fastapi.testclient import TestClient

client = TestClient(app)
ADMIN = {"Authorization": "Bearer dev-admin"}
WRITER = {"Authorization": "Bearer dev-business-development"}
READER = {"Authorization": "Bearer dev-read-only"}


@pytest.fixture(autouse=True)
def reset():
    repository.reset()
    pipeline_repository.reset()
    administration_repository.reset()
    yield
    administration_repository.reset()


def test_hosted_environment_refuses_development_tokens(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("AUTH_MODE", "local")
    with pytest.raises(RuntimeError, match="forbidden"):
        Settings()
    monkeypatch.setenv("AUTH_MODE", "supabase")
    assert Settings().auth_mode == "supabase"


def test_configurable_icp_is_stored_and_role_protected():
    company = client.post(
        "/companies",
        headers=WRITER,
        json={
            "name": "Synthetic Rule Company",
            "industry": "Financial Services",
        },
    ).json()
    before = client.post(f"/companies/{company['id']}/calculate-icp", headers=WRITER).json()
    weights = {**DEFAULT_WEIGHTS, "industry_fit": 40, "company_size": 5}
    assert client.put("/icp-rules", headers=WRITER, json={"weights": weights}).status_code == 403
    assert (
        client.put("/icp-rules", headers=ADMIN, json={"weights": {"industry_fit": 100}}).status_code
        == 422
    )
    assert client.put("/icp-rules", headers=ADMIN, json={"weights": weights}).status_code == 200
    after = client.post(f"/companies/{company['id']}/calculate-icp", headers=WRITER).json()
    assert after["score"] > before["score"]
    assert sum(r["max_points"] for r in after["explanations"]) == 100
    assert after["explanations"][0]["points"] == 40
    timeline = client.get(f"/companies/{company['id']}/timeline", headers=READER).json()
    assert timeline["score"]["score"] == after["score"]


def test_service_catalogue_requires_admin_for_changes():
    payload = {"name": "Synthetic Service", "description": "Demo only", "active": True}
    assert client.post("/services", headers=READER, json=payload).status_code == 403
    created = client.post("/services", headers=ADMIN, json=payload)
    assert created.status_code == 201
    result = client.put(
        f"/services/{created.json()['id']}", headers=ADMIN, json={**payload, "active": False}
    )
    assert result.status_code == 200
    assert result.json()["active"] is False


def test_csv_validation_is_atomic_and_export_neutralizes_formulas():
    company = client.post("/companies", headers=WRITER, json={"name": "Synthetic CSV"}).json()
    valid = f"company_id,first_name,last_name\n{company['id']},=SUM(1),Demo\n"
    headers = {**WRITER, "Content-Type": "text/csv"}
    invalid = valid + f"{company['id']},,Invalid\n"
    assert client.post("/data/contacts/import", headers=headers, content=invalid).status_code == 422
    assert client.get("/contacts", headers=READER).json()["total"] == 0
    assert (
        client.post(
            "/data/contacts/import", headers={**READER, "Content-Type": "text/csv"}, content=valid
        ).status_code
        == 403
    )
    response = client.post("/data/contacts/import", headers=headers, content=valid)
    assert response.status_code == 201
    exported = client.get("/data/contacts/export", headers=READER)
    assert "'=SUM(1)" in exported.text
    assert (
        client.post("/data/contacts/import", headers=headers, content=exported.content).status_code
        == 201
    )
    assert client.get("/contacts", headers=READER).json()["items"][1]["first_name"] == "=SUM(1)"


def test_priority_displays_responsible_owner_action_due_date_and_new_factors():
    company = client.post(
        "/companies",
        headers=WRITER,
        json={
            "name": "Synthetic Priority",
            "strategic_importance": 4,
        },
    ).json()
    deal = client.post(
        "/opportunities",
        headers=WRITER,
        json={
            "name": "Synthetic Deal",
            "company_id": company["id"],
            "stage_id": "30000000-0000-4000-8000-000000000010",
            "expected_close_date": (datetime.now(UTC) + timedelta(days=5)).date().isoformat(),
        },
    ).json()
    task = client.post(
        "/tasks",
        headers=WRITER,
        json={
            "title": "Confirm mock scope",
            "company_id": company["id"],
            "opportunity_id": deal["id"],
            "due_at": (datetime.now(UTC) + timedelta(days=2)).isoformat(),
        },
    ).json()
    priority = client.get("/dashboard/summary", headers=READER).json()["priority_opportunities"][0]
    assert priority["owner_id"] == task["owner_id"]
    assert priority["next_action"] == task["title"]
    assert priority["due_at"] == task["due_at"]
    assert priority["priority_score"] == 29  # due 15 + strategic 4 + close 5 + stage 5
    assert "strategic importance (+4)" in priority["reason"]


def test_recommendations_are_server_side_and_respect_inactive_services():
    company = client.post(
        "/companies",
        headers=WRITER,
        json={
            "name": "Synthetic Recommendation",
            "cloud_usage": ["Synthetic cloud"],
        },
    ).json()
    endpoint = f"/companies/{company['id']}/recommendations"
    assert client.get(endpoint, headers=READER).status_code == 409
    client.post(f"/companies/{company['id']}/calculate-icp", headers=WRITER)
    assert client.get(endpoint, headers=READER).json()["primary"] == "Cloud Security Assessment"
    service = next(
        s for s in administration_repository.services if s["name"] == "Cloud Security Assessment"
    )
    service["active"] = False
    assert client.get(endpoint, headers=READER).json()["primary"] == "Compliance Readiness Review"


def test_task_completion_is_idempotent_and_reopening_clears_timestamp():
    task = client.post("/tasks", headers=WRITER, json={"title": "Synthetic follow-up"}).json()
    assert task["owner_id"] == "00000000-0000-4000-8000-000000000003"
    endpoint = f"/tasks/{task['id']}"
    assert client.patch(endpoint, headers=READER, json={"status": "completed"}).status_code == 403
    completed = client.patch(
        endpoint, headers=WRITER, json={"status": "completed", "outcome": "Discussed mock scope"}
    ).json()
    assert completed["completed_at"]
    assert completed["outcome"] == "Discussed mock scope"
    repeated = client.patch(endpoint, headers=WRITER, json={"status": "completed"}).json()
    assert repeated["completed_at"] == completed["completed_at"]
    reopened = client.patch(endpoint, headers=WRITER, json={"status": "open"}).json()
    assert reopened["completed_at"] is None


def test_profile_fields_and_timeline_are_persisted_without_cross_company_records():
    company = client.post("/companies", headers=WRITER, json={"name": "Synthetic A"}).json()
    other = client.post("/companies", headers=WRITER, json={"name": "Synthetic B"}).json()
    endpoint = f"/companies/{company['id']}"
    response = client.patch(
        endpoint,
        headers=WRITER,
        json={
            "employee_count": 600,
            "cloud_usage": ["Synthetic cloud"],
            "regulatory_context": ["SOC 2"],
            "next_action": "Review mock scope",
            "strategic_importance": 4,
        },
    )
    assert response.status_code == 200
    assert client.get(endpoint, headers=READER).json()["employee_count"] == 600
    assert client.patch(endpoint, headers=WRITER, json={"name": None}).status_code == 422
    for item in (company, other):
        client.post(
            "/tasks", headers=WRITER, json={"title": item["name"], "company_id": item["id"]}
        )
    timeline = client.get(f"{endpoint}/timeline", headers=READER).json()
    assert [t["title"] for t in timeline["tasks"]] == ["Synthetic A"]


def test_analytics_reconcile_known_values_and_exclude_archived_deals():
    company = client.post(
        "/companies",
        headers=WRITER,
        json={
            "name": "Synthetic Analytics",
            "headquarters_country": "Germany",
            "industry": "SaaS",
        },
    ).json()
    stage = "30000000-0000-4000-8000-000000000001"
    won = "30000000-0000-4000-8000-000000000013"
    for name, value, probability, stage_id in [
        ("Open", 1000, 50, stage),
        ("Won", 2000, 100, won),
        ("Archived", 9000, 50, stage),
    ]:
        response = client.post(
            "/opportunities",
            headers=WRITER,
            json={
                "name": name,
                "company_id": company["id"],
                "stage_id": stage_id,
                "value_eur": value,
                "probability": probability,
                "expected_close_date": "2026-12-01",
            },
        )
        assert response.status_code == 201
        if name == "Archived":
            client.delete(f"/opportunities/{response.json()['id']}", headers=WRITER)
    client.post(
        "/tasks",
        headers=WRITER,
        json={
            "title": "Already complete",
            "status": "completed",
            "due_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
        },
    )
    data = client.get("/dashboard/analytics", headers=READER).json()
    assert data["forecast"] == [{"label": "2026-12", "count": 1, "value": 1000, "weighted": 500}]
    assert data["pipeline_groups"]["headquarters_country"][0]["label"] == "Germany"
    assert data["conversion_percent"] == 100
    assert data["average_deal_value"] == 1500
    assert data["due_today"] == []
    assert client.get("/dashboard/analytics").status_code == 401
