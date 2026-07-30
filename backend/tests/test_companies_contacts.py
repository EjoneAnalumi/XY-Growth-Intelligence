from uuid import UUID

from app.main import app
from app.services.growth_repository import repository
from fastapi.testclient import TestClient

client = TestClient(app)
writer_headers = {"Authorization": "Bearer dev-business-development"}
read_only_headers = {"Authorization": "Bearer dev-read-only"}


def setup_function() -> None:
    repository.reset()


def test_create_company_with_valid_payload() -> None:
    response = client.post(
        "/companies",
        headers=writer_headers,
        json={
            "name": "Northstar Robotics Labs",
            "domain": "northstar-robotics.example",
            "employee_count": 420,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Northstar Robotics Labs"
    assert body["created_by"] == "00000000-0000-4000-8000-000000000003"
    UUID(body["id"])


def test_create_company_rejects_invalid_payload() -> None:
    response = client.post(
        "/companies",
        headers=writer_headers,
        json={"name": "", "employee_count": -1},
    )

    assert response.status_code == 422


def test_create_company_rejects_read_only_role() -> None:
    response = client.post(
        "/companies",
        headers=read_only_headers,
        json={"name": "Read Only Attempt"},
    )

    assert response.status_code == 403


def test_list_companies_supports_pagination() -> None:
    for name in ["Northstar Robotics Labs", "Blue Harbor Finance"]:
        client.post("/companies", headers=writer_headers, json={"name": name})

    response = client.get("/companies?limit=1&offset=1", headers=writer_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["name"] == "Blue Harbor Finance"


def test_list_companies_rejects_invalid_pagination() -> None:
    response = client.get("/companies?limit=0", headers=writer_headers)

    assert response.status_code == 422


def test_get_company_returns_not_found() -> None:
    response = client.get(
        "/companies/10000000-0000-4000-8000-000000000001",
        headers=writer_headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Company not found."}


def test_list_companies_requires_authentication() -> None:
    response = client.get("/companies")

    assert response.status_code == 401


def test_create_contact_with_valid_payload() -> None:
    company_response = client.post(
        "/companies",
        headers=writer_headers,
        json={"name": "Northstar Robotics Labs"},
    )
    company_id = company_response.json()["id"]

    response = client.post(
        "/contacts",
        headers=writer_headers,
        json={
            "company_id": company_id,
            "first_name": "Mira",
            "last_name": "Vale",
            "email": "mira.vale@northstar-robotics.example",
            "decision_category": "champion",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["company_id"] == company_id
    assert body["first_name"] == "Mira"
    assert body["created_by"] == "00000000-0000-4000-8000-000000000003"


def test_create_contact_rejects_invalid_payload() -> None:
    response = client.post(
        "/contacts",
        headers=writer_headers,
        json={
            "company_id": "not-a-uuid",
            "first_name": "",
            "last_name": "",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422


def test_create_contact_returns_not_found_for_unknown_company() -> None:
    response = client.post(
        "/contacts",
        headers=writer_headers,
        json={
            "company_id": "10000000-0000-4000-8000-000000000001",
            "first_name": "Mira",
            "last_name": "Vale",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Company not found."}


def test_create_contact_rejects_read_only_role() -> None:
    response = client.post(
        "/contacts",
        headers=read_only_headers,
        json={
            "company_id": "10000000-0000-4000-8000-000000000001",
            "first_name": "Mira",
            "last_name": "Vale",
        },
    )

    assert response.status_code == 403


def test_list_contacts_supports_company_filter_and_pagination() -> None:
    first_company = client.post(
        "/companies",
        headers=writer_headers,
        json={"name": "Northstar Robotics Labs"},
    ).json()
    second_company = client.post(
        "/companies",
        headers=writer_headers,
        json={"name": "Blue Harbor Finance"},
    ).json()

    for first_name, company_id in [
        ("Mira", first_company["id"]),
        ("Jon", first_company["id"]),
        ("Elena", second_company["id"]),
    ]:
        client.post(
            "/contacts",
            headers=writer_headers,
            json={
                "company_id": company_id,
                "first_name": first_name,
                "last_name": "Demo",
            },
        )

    response = client.get(
        f"/contacts?company_id={first_company['id']}&limit=1&offset=1",
        headers=writer_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["first_name"] == "Jon"
