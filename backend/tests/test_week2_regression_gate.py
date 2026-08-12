from datetime import UTC, datetime, timedelta

import pytest
from app.main import app
from app.services.growth_repository import repository as growth_repository
from app.services.pipeline_repository import pipeline_repository
from fastapi.testclient import TestClient

client = TestClient(app)

writer_headers = {"Authorization": "Bearer dev-business-development"}
read_only_headers = {"Authorization": "Bearer dev-read-only"}
analyst_headers = {"Authorization": "Bearer dev-technical-analyst"}

identified_stage_id = "30000000-0000-4000-8000-000000000001"
contacted_stage_id = "30000000-0000-4000-8000-000000000003"


def setup_function() -> None:
    growth_repository.reset()
    pipeline_repository.reset()


def _create_company_and_contact() -> tuple[dict, dict]:
    company = client.post(
        "/companies",
        headers=writer_headers,
        json={
            "name": "Day Ten Finance",
            "domain": "day-ten-finance.example",
            "industry": "Financial Services",
            "employee_count": 700,
            "annual_revenue_usd": 80_000_000,
            "headquarters_country": "United States",
            "cloud_usage": ["AWS", "Azure"],
            "regulatory_context": ["PCI DSS", "SOX"],
            "lead_source": "partner referral",
            "status": "qualified",
            "lifecycle_stage": "qualified",
        },
    ).json()

    contact = client.post(
        "/contacts",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "first_name": "Rina",
            "last_name": "Cole",
            "email": "rina.cole@day-ten-finance.example",
            "decision_category": "champion",
        },
    ).json()

    return company, contact


def test_week2_sales_workflow_gate_updates_dashboard() -> None:
    company, contact = _create_company_and_contact()

    score = client.post(
        f"/companies/{company['id']}/calculate-icp",
        headers=writer_headers,
    )
    assert score.status_code == 201
    assert score.json()["tier"] == "strong_fit"

    opportunity = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "contact_id": contact["id"],
            "stage_id": identified_stage_id,
            "name": "Week 2 Regression Managed SOC Pilot",
            "service": "Managed SOC",
            "value_usd": 100000,
            "probability": 50,
            "expected_close_date": "2026-09-30",
            "next_action": "Schedule technical discovery",
        },
    )
    assert opportunity.status_code == 201
    opportunity_body = opportunity.json()
    assert opportunity_body["weighted_value_usd"] == 50000

    moved = client.patch(
        f"/opportunities/{opportunity_body['id']}/move-stage",
        headers=writer_headers,
        json={"to_stage_id": contacted_stage_id, "note": "Prospect accepted meeting."},
    )
    assert moved.status_code == 200
    assert moved.json()["history"]["from_stage_id"] == identified_stage_id
    assert moved.json()["history"]["to_stage_id"] == contacted_stage_id

    activity = client.post(
        "/activities",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "contact_id": contact["id"],
            "opportunity_id": opportunity_body["id"],
            "activity_type": "meeting",
            "subject": "Week 2 demo discovery meeting",
        },
    )
    assert activity.status_code == 201

    task = client.post(
        "/tasks",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "contact_id": contact["id"],
            "opportunity_id": opportunity_body["id"],
            "title": "Send discovery recap",
            "priority": "high",
            "status": "open",
            "due_at": (datetime.now(UTC) + timedelta(days=2)).isoformat(),
        },
    )
    assert task.status_code == 201

    dashboard = client.get("/dashboard/summary", headers=writer_headers)

    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["total_opportunities"] == 1
    assert body["open_opportunities"] == 1
    assert body["pipeline_value_usd"] == 100000
    assert body["weighted_pipeline_value_usd"] == 50000
    assert body["activities_count"] == 1
    assert body["open_tasks"] == 1
    assert body["due_this_week_tasks"] == 1
    assert body["high_priority_opportunities"] == 1
    assert body["priority_opportunities"][0]["opportunity_id"] == opportunity_body["id"]


@pytest.mark.parametrize("headers", [read_only_headers, analyst_headers])
def test_week2_non_writer_roles_cannot_mutate_sales_workflow(headers: dict[str, str]) -> None:
    company, contact = _create_company_and_contact()
    opportunity = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "contact_id": contact["id"],
            "stage_id": identified_stage_id,
            "name": "Permission Baseline Deal",
        },
    ).json()
    activity = client.post(
        "/activities",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "activity_type": "email",
            "subject": "Permission baseline email",
        },
    ).json()
    task = client.post(
        "/tasks",
        headers=writer_headers,
        json={"company_id": company["id"], "title": "Permission baseline task"},
    ).json()
    note = client.post(
        "/notes",
        headers=writer_headers,
        json={"company_id": company["id"], "body": "Permission baseline note."},
    ).json()

    denied_requests = [
        client.post("/companies", headers=headers, json={"name": "Denied Company"}),
        client.post(
            "/contacts",
            headers=headers,
            json={"company_id": company["id"], "first_name": "Denied", "last_name": "Contact"},
        ),
        client.post(f"/companies/{company['id']}/calculate-icp", headers=headers),
        client.post(
            "/pipeline-stages",
            headers=headers,
            json={"name": "Denied Stage", "sort_order": 160, "default_probability": 10},
        ),
        client.post(
            "/opportunities",
            headers=headers,
            json={
                "company_id": company["id"],
                "stage_id": identified_stage_id,
                "name": "Denied Opportunity",
            },
        ),
        client.patch(
            f"/opportunities/{opportunity['id']}",
            headers=headers,
            json={"next_action": "Denied update"},
        ),
        client.patch(
            f"/opportunities/{opportunity['id']}/move-stage",
            headers=headers,
            json={"to_stage_id": contacted_stage_id},
        ),
        client.delete(f"/opportunities/{opportunity['id']}", headers=headers),
        client.post(
            "/activities",
            headers=headers,
            json={
                "company_id": company["id"],
                "activity_type": "call",
                "subject": "Denied activity",
            },
        ),
        client.patch(
            f"/activities/{activity['id']}",
            headers=headers,
            json={"subject": "Denied update"},
        ),
        client.delete(f"/activities/{activity['id']}", headers=headers),
        client.post("/tasks", headers=headers, json={"title": "Denied task"}),
        client.patch(
            f"/tasks/{task['id']}",
            headers=headers,
            json={"status": "completed"},
        ),
        client.delete(f"/tasks/{task['id']}", headers=headers),
        client.post("/notes", headers=headers, json={"body": "Denied note."}),
        client.patch(
            f"/notes/{note['id']}",
            headers=headers,
            json={"body": "Denied update."},
        ),
        client.delete(f"/notes/{note['id']}", headers=headers),
    ]

    assert {response.status_code for response in denied_requests} == {403}

    readable_paths = [
        "/companies",
        f"/companies/{company['id']}",
        "/contacts",
        f"/contacts/{contact['id']}",
        "/pipeline-stages",
        "/opportunities",
        f"/opportunities/{opportunity['id']}",
        f"/opportunities/{opportunity['id']}/stage-history",
        "/activities",
        f"/activities/{activity['id']}",
        "/tasks",
        f"/tasks/{task['id']}",
        "/notes",
        f"/notes/{note['id']}",
        "/dashboard/summary",
    ]

    assert {client.get(path, headers=headers).status_code for path in readable_paths} == {200}


def test_business_development_cannot_create_admin_only_pipeline_stage() -> None:
    response = client.post(
        "/pipeline-stages",
        headers=writer_headers,
        json={"name": "BD Admin Only Stage", "sort_order": 160, "default_probability": 10},
    )

    assert response.status_code == 403
