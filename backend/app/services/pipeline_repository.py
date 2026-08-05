from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.users import CurrentUser

DEFAULT_PIPELINE_STAGES = [
    ("30000000-0000-4000-8000-000000000001", "Identified", 10, 5, False, False),
    ("30000000-0000-4000-8000-000000000002", "Researching", 20, 10, False, False),
    ("30000000-0000-4000-8000-000000000003", "Contacted", 30, 15, False, False),
    ("30000000-0000-4000-8000-000000000004", "Meeting Scheduled", 40, 25, False, False),
    ("30000000-0000-4000-8000-000000000005", "Discovery Completed", 50, 35, False, False),
    ("30000000-0000-4000-8000-000000000006", "Qualified", 60, 45, False, False),
    ("30000000-0000-4000-8000-000000000007", "Assessment Offered", 70, 50, False, False),
    ("30000000-0000-4000-8000-000000000008", "Pilot Proposed", 80, 60, False, False),
    ("30000000-0000-4000-8000-000000000009", "Pilot Active", 90, 70, False, False),
    ("30000000-0000-4000-8000-000000000010", "Proposal Sent", 100, 75, False, False),
    ("30000000-0000-4000-8000-000000000011", "Negotiation", 110, 85, False, False),
    ("30000000-0000-4000-8000-000000000012", "Contract Review", 120, 90, False, False),
    ("30000000-0000-4000-8000-000000000013", "Won", 130, 100, True, False),
    ("30000000-0000-4000-8000-000000000014", "Lost", 140, 0, False, True),
    ("30000000-0000-4000-8000-000000000015", "On Hold", 150, 0, False, False),
]


class InMemoryPipelineRepository:
    def __init__(self) -> None:
        self._opportunities: dict[str, dict] = {}
        self._pipeline_stages: dict[str, dict] = {}
        self._activities: dict[str, dict] = {}
        self._tasks: dict[str, dict] = {}
        self._notes: dict[str, dict] = {}
        self._stage_history: dict[str, dict] = {}
        self.reset()

    def reset(self) -> None:
        self._opportunities.clear()
        self._pipeline_stages.clear()
        self._activities.clear()
        self._tasks.clear()
        self._notes.clear()
        self._stage_history.clear()

        now = datetime.now(UTC)
        for stage_id, name, sort_order, probability, is_won, is_lost in DEFAULT_PIPELINE_STAGES:
            self._pipeline_stages[stage_id] = {
                "id": stage_id,
                "name": name,
                "sort_order": sort_order,
                "default_probability": probability,
                "is_won": is_won,
                "is_lost": is_lost,
                "created_at": now,
                "updated_at": now,
            }

    def list_records(self, collection: str) -> list[dict]:
        records = list(self._collection(collection).values())
        active_records = [record for record in records if record.get("archived_at") is None]
        return sorted(active_records, key=lambda record: record.get("created_at", datetime.min))

    def get_record(self, collection: str, record_id: str) -> dict | None:
        record = self._collection(collection).get(record_id)

        if record is None or record.get("archived_at") is not None:
            return None

        return record

    def create_record(self, collection: str, payload: dict, current_user: CurrentUser) -> dict:
        now = datetime.now(UTC)
        user_id = current_user.id
        record = {
            **payload,
            "id": str(uuid4()),
            "created_by": user_id,
            "updated_by": user_id,
            "archived_at": None,
            "created_at": now,
            "updated_at": now,
        }

        if collection == "opportunities":
            record = self._with_weighted_value(record)

        self._collection(collection)[record["id"]] = record
        return record

    def update_record(
        self,
        collection: str,
        record_id: str,
        payload: dict,
        current_user: CurrentUser,
    ) -> dict | None:
        current = self.get_record(collection, record_id)

        if current is None:
            return None

        updated = {
            **current,
            **payload,
            "updated_by": current_user.id,
            "updated_at": datetime.now(UTC),
        }

        if collection == "opportunities":
            updated = self._with_weighted_value(updated)

        self._collection(collection)[record_id] = updated
        return updated

    def archive_record(
        self,
        collection: str,
        record_id: str,
        current_user: CurrentUser,
    ) -> dict | None:
        current = self.get_record(collection, record_id)

        if current is None:
            return None

        now = datetime.now(UTC)
        current["archived_at"] = now
        current["updated_at"] = now
        current["updated_by"] = current_user.id
        return current

    def move_opportunity_stage(
        self,
        opportunity_id: str,
        to_stage_id: str,
        note: str | None,
        current_user: CurrentUser,
    ) -> tuple[dict, dict] | None:
        opportunity = self.get_record("opportunities", opportunity_id)

        if opportunity is None:
            return None

        from_stage_id = opportunity["stage_id"]
        updated = self.update_record(
            "opportunities",
            opportunity_id,
            {"stage_id": to_stage_id},
            current_user,
        )
        history = self.create_stage_history(
            {
                "opportunity_id": opportunity_id,
                "from_stage_id": from_stage_id,
                "to_stage_id": to_stage_id,
                "note": note,
            },
            current_user,
        )

        return updated, history

    def create_stage_history(self, payload: dict, current_user: CurrentUser) -> dict:
        now = datetime.now(UTC)
        history = {
            **payload,
            "id": str(uuid4()),
            "changed_by": current_user.id,
            "changed_at": now,
        }
        self._stage_history[history["id"]] = history
        return history

    def list_stage_history(self, opportunity_id: str) -> list[dict]:
        records = [
            record
            for record in self._stage_history.values()
            if record["opportunity_id"] == opportunity_id
        ]
        return sorted(records, key=lambda record: record["changed_at"])

    def stage_exists(self, stage_id: str | UUID) -> bool:
        return str(stage_id) in self._pipeline_stages

    def _collection(self, collection: str) -> dict[str, dict]:
        return {
            "opportunities": self._opportunities,
            "pipeline_stages": self._pipeline_stages,
            "activities": self._activities,
            "tasks": self._tasks,
            "notes": self._notes,
        }[collection]

    def _with_weighted_value(self, data: dict) -> dict:
        value = data.get("value_usd")
        probability = data.get("probability")

        if value is None or probability is None:
            data["weighted_value_usd"] = None
            return data

        data["weighted_value_usd"] = round(float(value) * int(probability) / 100, 2)
        return data


pipeline_repository = InMemoryPipelineRepository()


def get_pipeline_repository() -> InMemoryPipelineRepository:
    return pipeline_repository
