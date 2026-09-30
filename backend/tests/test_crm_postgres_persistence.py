import os
from uuid import uuid4

import pytest
from app.schemas.companies import CompanyCreate
from app.schemas.contacts import ContactCreate
from app.schemas.users import CurrentUser
from app.services.postgres_growth_repository import PostgresGrowthRepository
from app.services.postgres_pipeline_repository import PostgresPipelineRepository

DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.mark.skipif(DATABASE_URL is None, reason="local Supabase PostgreSQL is not configured")
def test_core_crm_records_survive_repository_restart():
    assert DATABASE_URL is not None
    user = CurrentUser(
        id="00000000-0000-4000-8000-000000000001",
        email="admin.demo@example.test",
        full_name="Admin Demo",
        role="admin",
    )
    growth = PostgresGrowthRepository(DATABASE_URL)
    pipeline = PostgresPipelineRepository(DATABASE_URL)
    suffix = uuid4().hex[:10]
    company = growth.create_company(
        CompanyCreate(name=f"Persistence Test {suffix}", domain=f"persistence-{suffix}.example"),
        user,
    )
    contact = growth.create_contact(
        ContactCreate(
            company_id=company.id,
            first_name="Synthetic",
            last_name="Tester",
            email=f"tester-{suffix}@example.test",
        ),
        user,
    )
    assert contact is not None
    stage = pipeline.list_records("pipeline_stages")[0]
    opportunity = pipeline.create_record(
        "opportunities",
        {
            "company_id": str(company.id),
            "contact_id": str(contact.id),
            "stage_id": stage["id"],
            "name": f"Restart-safe opportunity {suffix}",
            "value_eur": 10000,
            "probability": 20,
        },
        user,
    )
    note = pipeline.create_record(
        "notes",
        {
            "company_id": str(company.id),
            "contact_id": str(contact.id),
            "opportunity_id": opportunity["id"],
            "body": "Synthetic persistence verification note.",
        },
        user,
    )

    restarted_growth = PostgresGrowthRepository(DATABASE_URL)
    restarted_pipeline = PostgresPipelineRepository(DATABASE_URL)
    assert restarted_growth.get_company(company.id).name == company.name
    assert restarted_growth.get_contact(contact.id).email == contact.email
    assert (
        restarted_pipeline.get_record("opportunities", opportunity["id"])["name"]
        == opportunity["name"]
    )
    assert restarted_pipeline.get_record("notes", note["id"])["body"] == note["body"]

    restarted_pipeline.archive_record("notes", note["id"], user)
    restarted_pipeline.archive_record("opportunities", opportunity["id"], user)
    restarted_growth.archive_contact(contact.id, user)
    restarted_growth.archive_company(company.id, user)
