from datetime import datetime
from uuid import UUID


class PipelineStage:
    def __init__(
        self,
        id: UUID,
        name: str,
        sort_order: int,
        default_probability: int = 0,
        is_won: bool = False,
        is_lost: bool = False,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id
        self.name = name
        self.sort_order = sort_order
        self.default_probability = default_probability
        self.is_won = is_won
        self.is_lost = is_lost
        self.created_at = created_at
        self.updated_at = updated_at