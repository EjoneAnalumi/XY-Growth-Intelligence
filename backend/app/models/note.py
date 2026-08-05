from datetime import datetime
from uuid import UUID


class Note:
    def __init__(
        self,
        id: UUID,
        body: str,
        opportunity_id: UUID | None = None,
        company_id: UUID | None = None,
        contact_id: UUID | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.body = body
        self.opportunity_id = opportunity_id
        self.company_id = company_id
        self.contact_id = contact_id
        self.created_at = created_at
