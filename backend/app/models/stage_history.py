from datetime import datetime
from uuid import UUID


class StageHistory:
    def __init__(
        self,
        id: UUID,
        opportunity_id: UUID,
        to_stage_id: UUID,
        from_stage_id: UUID | None = None,
        changed_by: UUID | None = None,
        note: str | None = None,
        changed_at: datetime | None = None,
    ):
        self.id = id
        self.opportunity_id = opportunity_id
        self.from_stage_id = from_stage_id
        self.to_stage_id = to_stage_id
        self.changed_by = changed_by
        self.note = note
        self.changed_at = changed_at
