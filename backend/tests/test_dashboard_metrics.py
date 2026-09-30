from datetime import UTC, datetime, timedelta

from app.main import app
from app.services.growth_repository import repository
from app.services.pipeline_repository import pipeline_repository
from fastapi.testclient import TestClient

client = TestClient(app)

writer_headers = {"Authorization": "Bearer dev-business-development"}

company_id = "10000000-0000-4000-8000-000000000001"
contact_id = "20000000-0000-4000-8000-000000000001"
identified_stage_id = "30000000-0000-4000-8000-000000000001"
proposal_stage_id = "30000000-0000-4000-8000-000000000010"
won_stage_id = "30000000-0000-4000-8000-000000000013"
lost_stage_id = "30000000-0000-4000-8000-000000000014"


def setup_function() -> None:
    repository.reset()
    pipeline_repository.reset()


def test_dashboard_summary_requires_authentication() -> None:
    response = client.get("/dashboard/summary")

    assert response.status_code == 401


def test_dashboard_summary_returns_verified_pipeline_metrics() -> None:
    now = datetime.now(UTC)

    client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "contact_id": contact_id,
            "stage_id": identified_stage_id,
            "name": "Known open deal",
            "value_eur": 100000,
            "probability": 50,
        },
    )
    client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "stage_id": proposal_stage_id,
            "name": "Known proposal deal",
            "value_eur": 40000,
            "probability": 75,
        },
    )
    client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "stage_id": won_stage_id,
            "name": "Known won deal",
            "value_eur": 25000,
            "probability": 100,
        },
    )
    client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "stage_id": lost_stage_id,
            "name": "Known lost deal",
            "value_eur": 80000,
            "probability": 20,
        },
    )

    client.post(
        "/activities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "activity_type": "meeting",
            "subject": "Discovery meeting",
        },
    )
    client.post(
        "/activities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "activity_type": "email",
            "subject": "Proposal follow-up",
        },
    )

    for title, status, due_at in [
        ("Overdue open task", "open", now - timedelta(days=1)),
        ("Due this week task", "in_progress", now + timedelta(days=2)),
        ("Completed overdue task", "completed", now - timedelta(days=3)),
    ]:
        client.post(
            "/tasks",
            headers=writer_headers,
            json={
                "company_id": company_id,
                "title": title,
                "status": status,
                "due_at": due_at.isoformat(),
            },
        )

    response = client.get("/dashboard/summary", headers=writer_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total_opportunities"] == 4
    assert body["open_opportunities"] == 2
    assert body["won_opportunities"] == 1
    assert body["lost_opportunities"] == 1
    assert body["pipeline_value_eur"] == 140000
    assert body["weighted_pipeline_value_eur"] == 80000
    assert body["open_tasks"] == 2
    assert body["overdue_tasks"] == 1
    assert body["due_this_week_tasks"] == 1
    assert body["activities_count"] == 2
    assert body["inactive_opportunities"] == 0

    identified_summary = next(
        summary
        for summary in body["stage_summaries"]
        if summary["stage_id"] == identified_stage_id
    )
    assert identified_summary["opportunity_count"] == 1
    assert identified_summary["total_value_eur"] == 100000
    assert identified_summary["weighted_value_eur"] == 50000


def test_sales_workflow_updates_dashboard_priority_tasks_and_inactivity() -> None:
    now = datetime.now(UTC)
    company = client.post(
        "/companies",
        headers=writer_headers,
        json={
            "name": "Blue Harbor Finance",
            "industry": "Financial Services",
            "employee_count": 650,
            "annual_revenue_eur": 75000000,
            "headquarters_country": "United States",
            "cloud_usage": ["Azure", "AWS"],
            "regulatory_context": ["PCI DSS", "SOX"],
            "lead_source": "partner referral",
            "status": "qualified",
            "lifecycle_stage": "qualified",
        },
    ).json()
    client.post(
        f"/companies/{company['id']}/calculate-icp",
        headers=writer_headers,
    )
    priority_opportunity = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "stage_id": proposal_stage_id,
            "name": "High priority scored deal",
            "value_eur": 200000,
            "probability": 80,
        },
    ).json()
    inactive_opportunity = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "stage_id": identified_stage_id,
            "name": "Inactive early deal",
            "value_eur": 10000,
            "probability": 10,
        },
    ).json()
    pipeline_repository._opportunities[inactive_opportunity["id"]]["created_at"] = (
        now - timedelta(days=16)
    )
    task = client.post(
        "/tasks",
        headers=writer_headers,
        json={
            "company_id": company["id"],
            "opportunity_id": priority_opportunity["id"],
            "title": "Send commercial follow-up",
            "priority": "high",
            "status": "open",
            "due_at": (now + timedelta(days=2)).isoformat(),
        },
    ).json()

    response = client.get("/dashboard/summary", headers=writer_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["open_tasks"] == 1
    assert body["due_this_week_tasks"] == 1
    assert body["inactive_opportunities"] == 1
    assert body["high_priority_opportunities"] == 1
    assert body["priority_opportunities"][0]["opportunity_id"] == priority_opportunity["id"]
    # Value 30 + ICP 30 + due follow-up 15 + late stage 5.
    assert body["priority_opportunities"][0]["priority_score"] == 80
    assert "late pipeline stage (+5)" in body["priority_opportunities"][0]["reason"]
    assert "strong ICP fit" in body["priority_opportunities"][0]["reason"]
    assert "follow-up due this week" in body["priority_opportunities"][0]["reason"]

    client.patch(
        f"/tasks/{task['id']}",
        headers=writer_headers,
        json={"status": "completed"},
    )
    updated_response = client.get("/dashboard/summary", headers=writer_headers)

    assert updated_response.status_code == 200
    updated_body = updated_response.json()
    assert updated_body["open_tasks"] == 0
    assert updated_body["due_this_week_tasks"] == 0


def test_opportunity_response_includes_stage_duration() -> None:
    created = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "stage_id": identified_stage_id,
            "name": "Aged stage deal",
            "value_eur": 10000,
            "probability": 25,
        },
    ).json()
    pipeline_repository._opportunities[created["id"]]["created_at"] = datetime.now(
        UTC,
    ) - timedelta(days=5)

    response = client.get(f"/opportunities/{created['id']}", headers=writer_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["current_stage_entered_at"] is not None
    assert body["days_in_current_stage"] >= 5


def test_openapi_documents_dashboard_summary_endpoint() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/dashboard/summary" in response.json()["paths"]
