from datetime import datetime
from uuid import UUID


class Task:
    def __init__(
        self,
        id: UUID,
        title: str,
        opportunity_id: UUID | None = None,
        company_id: UUID | None = None,
        description: str | None = None,
        priority: str = "medium",
        status: str = "open",
        due_at: datetime | None = None,
    ):
        self.id = id
        self.title = title
        self.opportunity_id = opportunity_id
        self.company_id = company_id
        self.description = description
        self.priority = priority
        self.status = status
        self.due_at = due_at
