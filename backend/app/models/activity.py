from datetime import datetime
from uuid import UUID


class Activity:
    def __init__(
        self,
        id: UUID,
        company_id: UUID,
        activity_type: str,
        subject: str,
        opportunity_id: UUID | None = None,
        contact_id: UUID | None = None,
        notes: str | None = None,
        occurred_at: datetime | None = None,
        owner_id: UUID | None = None,
        created_by: UUID | None = None,
        updated_by: UUID | None = None,
        archived_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id

        self.company_id = company_id
        self.contact_id = contact_id
        self.opportunity_id = opportunity_id

        self.activity_type = activity_type
        self.subject = subject
        self.notes = notes

        self.occurred_at = occurred_at
        self.owner_id = owner_id

        self.created_by = created_by
        self.updated_by = updated_by
        self.archived_at = archived_at

        self.created_at = created_at
        self.updated_at = updated_at