from datetime import date, datetime
from uuid import UUID


class Opportunity:
    def __init__(
        self,
        id: UUID,
        company_id: UUID,
        stage_id: UUID,
        name: str,
        contact_id: UUID | None = None,
        service: str | None = None,
        value_eur: float | None = None,
        probability: int = 0,
        weighted_value_eur: float | None = None,
        expected_close_date: date | None = None,
        owner_id: UUID | None = None,
        need: str | None = None,
        blockers: str | None = None,
        competitor: str | None = None,
        next_action: str | None = None,
        next_action_due_at: datetime | None = None,
        lost_reason: str | None = None,
        created_by: UUID | None = None,
        updated_by: UUID | None = None,
        archived_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id
        self.company_id = company_id
        self.contact_id = contact_id
        self.stage_id = stage_id
        self.name = name
        self.service = service
        self.value_eur = value_eur
        self.probability = probability
        self.weighted_value_eur = weighted_value_eur
        self.expected_close_date = expected_close_date
        self.owner_id = owner_id
        self.need = need
        self.blockers = blockers
        self.competitor = competitor
        self.next_action = next_action
        self.next_action_due_at = next_action_due_at
        self.lost_reason = lost_reason
        self.created_by = created_by
        self.updated_by = updated_by
        self.archived_at = archived_at
        self.created_at = created_at
        self.updated_at = updated_at
