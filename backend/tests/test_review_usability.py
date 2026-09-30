from datetime import UTC, datetime, timedelta

import pytest
from app.api.inbox import memory_reads
from app.main import app
from app.services.note_visibility import memory_hidden
from app.services.pipeline_repository import pipeline_repository
from fastapi.testclient import TestClient

client = TestClient(app)
ADMIN = {"Authorization": "Bearer dev-admin"}
ANALYST = {"Authorization": "Bearer dev-technical-analyst"}
READER = {"Authorization": "Bearer dev-read-only"}
ADMIN_ID = "00000000-0000-4000-8000-000000000001"
ANALYST_ID = "00000000-0000-4000-8000-000000000004"
READER_ID = "00000000-0000-4000-8000-000000000005"


@pytest.fixture(autouse=True)
def isolated():
    pipeline_repository.reset()
    memory_reads.clear()
    memory_hidden.clear()


def task(owner=ANALYST_ID):
    response = client.post(
        "/tasks",
        headers=ADMIN,
        json={
            "title": "Review snapshot evidence",
            "owner_id": owner,
            "due_at": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        },
    )
    assert response.status_code == 201
    return response.json()


def test_task_assignment_permissions_and_analyst_completion():
    assert (
        client.post(
            "/tasks", headers=ADMIN, json={"title": "Denied", "owner_id": READER_ID}
        ).status_code
        == 422
    )
    own = task()
    assert own["assigned_by"] == ADMIN_ID and own["assigned_at"]
    endpoint = f"/tasks/{own['id']}"
    assert client.patch(endpoint, headers=ANALYST, json={"title": "No"}).status_code == 403
    assert client.patch(endpoint, headers=ADMIN, json={"owner_id": READER_ID}).status_code == 422
    assert client.patch(endpoint, headers=READER, json={"status": "completed"}).status_code == 403
    assert (
        client.patch(
            endpoint, headers=ANALYST, json={"status": "completed", "outcome": "Reviewed"}
        ).status_code
        == 200
    )
    other = task(ADMIN_ID)
    assert (
        client.patch(
            f"/tasks/{other['id']}", headers=ANALYST, json={"status": "completed"}
        ).status_code
        == 403
    )
    assert task(None)["owner_id"] is None


def test_task_receipts_are_personal_and_reassignment_is_unread():
    record = task()
    endpoint = f"/inbox/tasks/{record['id']}/read"
    inbox = client.get("/inbox", headers=ANALYST).json()
    assert inbox["unread_task_ids"] == [record["id"]]
    assert inbox["due_soon_tasks"] == 1
    assert client.post(endpoint, headers=ADMIN).status_code == 403
    assert client.post(endpoint, headers=ANALYST).status_code == 200
    assert client.get("/inbox", headers=ANALYST).json()["unread_task_ids"] == []
    for owner in (ADMIN_ID, ANALYST_ID):
        assert (
            client.patch(
                f"/tasks/{record['id']}", headers=ADMIN, json={"owner_id": owner}
            ).status_code
            == 200
        )
    assert client.get("/inbox", headers=ANALYST).json()["unread_task_ids"] == [record["id"]]
    client.patch(f"/tasks/{record['id']}", headers=ANALYST, json={"status": "completed"})
    assert client.get("/inbox", headers=ANALYST).json()["due_soon_tasks"] == 0


def test_note_receipts_and_analyst_ownership():
    note = client.post("/notes", headers=ANALYST, json={"body": "Snapshot observations"}).json()
    assert client.get("/inbox", headers=ANALYST).json()["unread_note_ids"] == []
    assert client.get("/inbox", headers=ADMIN).json()["unread_note_ids"] == [note["id"]]
    assert client.post(f"/inbox/notes/{note['id']}/read", headers=ADMIN).status_code == 200
    assert client.get("/inbox", headers=ADMIN).json()["unread_note_ids"] == []
    assert client.get("/inbox", headers=READER).json()["unread_note_ids"] == [note["id"]]
    assert (
        client.patch(f"/notes/{note['id']}", headers=ANALYST, json={"body": "Updated"}).status_code
        == 200
    )
    assert client.get("/inbox", headers=ADMIN).json()["unread_note_ids"] == [note["id"]]
    other = client.post("/notes", headers=ADMIN, json={"body": "Management context"}).json()
    assert (
        client.patch(f"/notes/{other['id']}", headers=ANALYST, json={"body": "Denied"}).status_code
        == 403
    )
    assert client.delete(f"/notes/{other['id']}", headers=ANALYST).status_code == 403
    assert client.delete(f"/notes/{note['id']}", headers=ANALYST).status_code == 200
    assert client.get("/inbox").status_code == 401


def test_opportunity_csv_uses_eur_and_calculates_weighted_value():
    company = client.post("/companies", headers=ADMIN, json={"name": "Euro Fixture"}).json()
    csv = (
        "company_id,stage_id,name,value_eur,probability\n"
        f"{company['id']},30000000-0000-4000-8000-000000000001,Euro opportunity,1000,40\n"
    )
    response = client.post(
        "/data/opportunities/import", headers={**ADMIN, "Content-Type": "text/csv"}, content=csv
    )
    assert response.status_code == 201
    deal = client.get("/opportunities", headers=ADMIN).json()["items"][0]
    assert deal["value_eur"] == 1000 and deal["weighted_value_eur"] == 400
    export = client.get("/data/opportunities/export", headers=ADMIN).text
    assert "value_eur" in export and "usd" not in export.lower()
    assert client.get("/dashboard/summary", headers=ADMIN).json()["pipeline_value_eur"] == 1000


@pytest.mark.parametrize(
    "author", ["dev-management", "dev-business-development", "dev-technical-analyst", "dev-admin"]
)
def test_only_author_or_admin_can_delete_shared_notes(author):
    author_headers = {"Authorization": f"Bearer {author}"}
    for deleter in [
        "dev-management",
        "dev-business-development",
        "dev-technical-analyst",
        "dev-admin",
        "dev-read-only",
    ]:
        note = client.post(
            "/notes", headers=author_headers, json={"body": "Shared synthetic decision"}
        ).json()
        endpoint = f"/notes/{note['id']}"
        allowed = deleter in {author, "dev-admin"}
        result = client.delete(endpoint, headers={"Authorization": f"Bearer {deleter}"})
        assert result.status_code == (200 if allowed else 403)
        assert client.get(endpoint, headers=ADMIN).status_code == (404 if allowed else 200)


@pytest.mark.parametrize(
    "viewer",
    [
        "dev-management",
        "dev-business-development",
        "dev-technical-analyst",
        "dev-admin",
        "dev-read-only",
    ],
)
def test_personal_deletion_preserves_shared_note_and_clears_only_own_inbox(viewer):
    company = client.post("/companies", headers=ADMIN, json={"name": "Visibility fixture"}).json()
    note = client.post(
        "/notes", headers=ADMIN, json={"body": "Shared decision", "company_id": company["id"]}
    ).json()
    headers = {"Authorization": f"Bearer {viewer}"}
    endpoint = f"/notes/{note['id']}"
    assert client.delete(endpoint + "/for-me", headers=headers).status_code == 200
    assert client.delete(endpoint + "/for-me", headers=headers).status_code == 200
    assert client.get(endpoint, headers=headers).status_code == 404
    assert client.get("/notes", headers=headers).json()["items"] == []
    assert client.get("/inbox", headers=headers).json()["unread_note_ids"] == []
    timeline = client.get(f"/companies/{company['id']}/timeline", headers=headers).json()
    assert timeline["notes"] == [] and timeline["timeline"] == []
    other = READER if viewer != "dev-read-only" else ANALYST
    assert client.get(endpoint, headers=other).status_code == 200
    assert client.get("/inbox", headers=other).json()["unread_note_ids"] == [note["id"]]
    client.patch(endpoint, headers=ADMIN, json={"body": "Revised shared decision"})
    assert client.get("/inbox", headers=headers).json()["unread_note_ids"] == []
    assert client.delete(endpoint + "/for-me").status_code == 401
