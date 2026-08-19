from app.main import app
from app.services.pipeline_repository import pipeline_repository
from fastapi.testclient import TestClient

client = TestClient(app)

writer_headers = {"Authorization": "Bearer dev-business-development"}
manager_headers = {"Authorization": "Bearer dev-management"}
reader_headers = {"Authorization": "Bearer dev-read-only"}

company_id = "10000000-0000-4000-8000-000000000001"
contact_id = "20000000-0000-4000-8000-000000000001"
identified_stage_id = "30000000-0000-4000-8000-000000000001"
contacted_stage_id = "30000000-0000-4000-8000-000000000003"


def setup_function() -> None:
    pipeline_repository.reset()


def test_pipeline_stages_require_authentication() -> None:
    response = client.get("/pipeline-stages")

    assert response.status_code == 401


def test_list_pipeline_stages_returns_default_brief_stages() -> None:
    response = client.get("/pipeline-stages", headers=writer_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 15
    assert body["items"][0]["name"] == "Identified"
    assert body["items"][-1]["name"] == "On Hold"


def test_business_development_cannot_create_pipeline_stage() -> None:
    response = client.post(
        "/pipeline-stages",
        headers=writer_headers,
        json={"name": "Custom Stage", "sort_order": 160, "default_probability": 20},
    )

    assert response.status_code == 403


def test_management_can_create_pipeline_stage() -> None:
    response = client.post(
        "/pipeline-stages",
        headers=manager_headers,
        json={"name": "Custom Stage", "sort_order": 160, "default_probability": 20},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Custom Stage"


def test_create_update_archive_opportunity_and_weighted_value() -> None:
    created = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "contact_id": contact_id,
            "stage_id": identified_stage_id,
            "name": "Managed SOC Pilot",
            "service": "Managed SOC",
            "value_usd": 50000,
            "probability": 40,
            "expected_close_date": "2026-09-30",
            "next_action": "Schedule pilot planning call",
        },
    )

    assert created.status_code == 201
    opportunity = created.json()
    assert opportunity["weighted_value_usd"] == 20000

    updated = client.patch(
        f"/opportunities/{opportunity['id']}",
        headers=writer_headers,
        json={"value_usd": 60000, "probability": 50},
    )

    assert updated.status_code == 200
    assert updated.json()["weighted_value_usd"] == 30000

    listed = client.get("/opportunities", headers=writer_headers)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    archived = client.delete(f"/opportunities/{opportunity['id']}", headers=writer_headers)
    assert archived.status_code == 200
    assert archived.json()["archived_at"] is not None

    listed_after_archive = client.get("/opportunities", headers=writer_headers)
    assert listed_after_archive.json()["total"] == 0


def test_create_opportunity_rejects_unknown_stage() -> None:
    response = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "stage_id": "30000000-0000-4000-8000-000000009999",
            "name": "Invalid Stage Deal",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["detail"] == "Pipeline stage not found."


def test_read_only_user_cannot_create_opportunity() -> None:
    response = client.post(
        "/opportunities",
        headers=reader_headers,
        json={
            "company_id": company_id,
            "stage_id": identified_stage_id,
            "name": "Read Only Attempt",
        },
    )

    assert response.status_code == 403


def test_move_opportunity_stage_records_history() -> None:
    created = client.post(
        "/opportunities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "stage_id": identified_stage_id,
            "name": "Pipeline Movement Deal",
        },
    ).json()

    response = client.patch(
        f"/opportunities/{created['id']}/move-stage",
        headers=writer_headers,
        json={"to_stage_id": contacted_stage_id, "note": "Prospect replied to outreach."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["opportunity"]["stage_id"] == contacted_stage_id
    assert body["history"]["from_stage_id"] == identified_stage_id
    assert body["history"]["to_stage_id"] == contacted_stage_id
    assert body["history"]["changed_by"] == "00000000-0000-4000-8000-000000000003"

    history = client.get(
        f"/opportunities/{created['id']}/stage-history",
        headers=writer_headers,
    )

    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["note"] == "Prospect replied to outreach."


def test_activity_task_and_note_crud() -> None:
    activity = client.post(
        "/activities",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "activity_type": "meeting",
            "subject": "Discovery meeting",
            "notes": "Reviewed SOC monitoring priorities.",
        },
    )
    assert activity.status_code == 201
    assert activity.json()["subject"] == "Discovery meeting"

    task = client.post(
        "/tasks",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "title": "Send pilot checklist",
            "priority": "high",
            "status": "open",
        },
    )
    assert task.status_code == 201
    task_id = task.json()["id"]

    completed_task = client.patch(
        f"/tasks/{task_id}",
        headers=writer_headers,
        json={"status": "completed", "outcome": "Checklist sent"},
    )
    assert completed_task.status_code == 200
    assert completed_task.json()["status"] == "completed"

    note = client.post(
        "/notes",
        headers=writer_headers,
        json={"company_id": company_id, "body": "Client asked for compliance references."},
    )
    assert note.status_code == 201
    assert note.json()["body"] == "Client asked for compliance references."


def test_openapi_documents_pipeline_endpoints() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    for path in [
        "/opportunities",
        "/opportunities/{opportunity_id}",
        "/opportunities/{opportunity_id}/move-stage",
        "/opportunities/{opportunity_id}/stage-history",
        "/pipeline-stages",
        "/activities",
        "/tasks",
        "/notes",
    ]:
        assert path in paths
