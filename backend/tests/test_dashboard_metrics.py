from datetime import UTC, datetime, timedelta

from app.main import app
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
            "value_usd": 100000,
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
            "value_usd": 40000,
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
            "value_usd": 25000,
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
            "value_usd": 80000,
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
    assert body["pipeline_value_usd"] == 140000
    assert body["weighted_pipeline_value_usd"] == 80000
    assert body["overdue_tasks"] == 1
    assert body["due_this_week_tasks"] == 1
    assert body["activities_count"] == 2

    identified_summary = next(
        summary
        for summary in body["stage_summaries"]
        if summary["stage_id"] == identified_stage_id
    )
    assert identified_summary["opportunity_count"] == 1
    assert identified_summary["total_value_usd"] == 100000
    assert identified_summary["weighted_value_usd"] == 50000


def test_opportunity_response_includes_stage_duration() -> None:
    created = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "stage_id": identified_stage_id,
            "name": "Aged stage deal",
            "value_usd": 10000,
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
