from datetime import UTC, datetime, timedelta
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
        if collection == "opportunities":
            active_records = [self._with_stage_duration(record) for record in active_records]

        return sorted(active_records, key=lambda record: record.get("created_at", datetime.min))

    def get_record(self, collection: str, record_id: str) -> dict | None:
        record = self._get_raw_record(collection, record_id)

        if record is None or record.get("archived_at") is not None:
            return None

        if collection == "opportunities":
            return self._with_stage_duration(record)

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
        if collection == "opportunities":
            return self._with_stage_duration(record)

        return record

    def update_record(
        self,
        collection: str,
        record_id: str,
        payload: dict,
        current_user: CurrentUser,
    ) -> dict | None:
        current = self._get_raw_record(collection, record_id)

        if current is None or current.get("archived_at") is not None:
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
        if collection == "opportunities":
            return self._with_stage_duration(updated)

        return updated

    def archive_record(
        self,
        collection: str,
        record_id: str,
        current_user: CurrentUser,
    ) -> dict | None:
        current = self._get_raw_record(collection, record_id)

        if current is None or current.get("archived_at") is not None:
            return None

        now = datetime.now(UTC)
        current["archived_at"] = now
        current["updated_at"] = now
        current["updated_by"] = current_user.id
        if collection == "opportunities":
            return self._with_stage_duration(current)

        return current

    def move_opportunity_stage(
        self,
        opportunity_id: str,
        to_stage_id: str,
        note: str | None,
        current_user: CurrentUser,
    ) -> tuple[dict, dict] | None:
        opportunity = self._get_raw_record("opportunities", opportunity_id)

        if opportunity is None or opportunity.get("archived_at") is not None:
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

    def get_dashboard_summary(self) -> dict:
        now = datetime.now(UTC)
        opportunities = [
            self._with_stage_duration(record, now)
            for record in self._opportunities.values()
            if record.get("archived_at") is None
        ]
        tasks = [
            record
            for record in self._tasks.values()
            if record.get("archived_at") is None
            and record.get("status") not in {"completed", "cancelled"}
        ]
        activities = [
            record for record in self._activities.values() if record.get("archived_at") is None
        ]

        open_opportunities = [
            opportunity
            for opportunity in opportunities
            if self._is_open_stage(opportunity.get("stage_id"))
        ]
        won_opportunities = [
            opportunity
            for opportunity in opportunities
            if self._stage_flag(opportunity.get("stage_id"), "is_won")
        ]
        lost_opportunities = [
            opportunity
            for opportunity in opportunities
            if self._stage_flag(opportunity.get("stage_id"), "is_lost")
        ]

        seven_days_from_now = now + timedelta(days=7)
        overdue_tasks = [
            task for task in tasks if self._parse_datetime(task.get("due_at")) is not None
            and self._parse_datetime(task.get("due_at")) < now
        ]
        due_this_week_tasks = [
            task
            for task in tasks
            if self._parse_datetime(task.get("due_at")) is not None
            and now <= self._parse_datetime(task.get("due_at")) <= seven_days_from_now
        ]

        return {
            "total_opportunities": len(opportunities),
            "open_opportunities": len(open_opportunities),
            "won_opportunities": len(won_opportunities),
            "lost_opportunities": len(lost_opportunities),
            "pipeline_value_usd": self._sum_money(open_opportunities, "value_usd"),
            "weighted_pipeline_value_usd": self._sum_money(
                open_opportunities,
                "weighted_value_usd",
            ),
            "overdue_tasks": len(overdue_tasks),
            "due_this_week_tasks": len(due_this_week_tasks),
            "activities_count": len(activities),
            "average_days_in_current_stage": self._average_stage_duration(open_opportunities),
            "stage_summaries": self._stage_summaries(opportunities),
        }

    def _collection(self, collection: str) -> dict[str, dict]:
        return {
            "opportunities": self._opportunities,
            "pipeline_stages": self._pipeline_stages,
            "activities": self._activities,
            "tasks": self._tasks,
            "notes": self._notes,
        }[collection]

    def _get_raw_record(self, collection: str, record_id: str) -> dict | None:
        return self._collection(collection).get(record_id)

    def _with_weighted_value(self, data: dict) -> dict:
        value = data.get("value_usd")
        probability = data.get("probability")

        if value is None or probability is None:
            data["weighted_value_usd"] = None
            return data

        data["weighted_value_usd"] = round(float(value) * int(probability) / 100, 2)
        return data

    def _with_stage_duration(self, opportunity: dict, now: datetime | None = None) -> dict:
        current_time = now or datetime.now(UTC)
        data = dict(opportunity)
        stage_entered_at = self._stage_entered_at(data)
        data["current_stage_entered_at"] = stage_entered_at
        data["days_in_current_stage"] = max(0, (current_time - stage_entered_at).days)
        return data

    def _stage_entered_at(self, opportunity: dict) -> datetime:
        stage_id = opportunity.get("stage_id")
        histories = [
            history
            for history in self._stage_history.values()
            if history["opportunity_id"] == opportunity["id"]
            and history["to_stage_id"] == stage_id
        ]

        if not histories:
            return self._parse_datetime(opportunity["created_at"]) or datetime.now(UTC)

        latest_history = max(histories, key=lambda history: history["changed_at"])
        return self._parse_datetime(latest_history["changed_at"]) or datetime.now(UTC)

    def _stage_flag(self, stage_id: str | UUID | None, flag: str) -> bool:
        if stage_id is None:
            return False

        stage = self._pipeline_stages.get(str(stage_id))
        return bool(stage and stage.get(flag))

    def _is_open_stage(self, stage_id: str | UUID | None) -> bool:
        return not self._stage_flag(stage_id, "is_won") and not self._stage_flag(
            stage_id,
            "is_lost",
        )

    def _parse_datetime(self, value: datetime | str | None) -> datetime | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=UTC)

            return value

        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)

        return parsed

    def _sum_money(self, records: list[dict], key: str) -> float:
        return round(sum(float(record.get(key) or 0) for record in records), 2)

    def _average_stage_duration(self, opportunities: list[dict]) -> float:
        if not opportunities:
            return 0.0

        total_days = sum(int(opportunity["days_in_current_stage"]) for opportunity in opportunities)
        return round(total_days / len(opportunities), 2)

    def _stage_summaries(self, opportunities: list[dict]) -> list[dict]:
        summaries = []

        for stage in sorted(
            self._pipeline_stages.values(),
            key=lambda item: item["sort_order"],
        ):
            stage_opportunities = [
                opportunity
                for opportunity in opportunities
                if opportunity.get("stage_id") == stage["id"]
            ]
            summaries.append(
                {
                    "stage_id": stage["id"],
                    "stage_name": stage["name"],
                    "opportunity_count": len(stage_opportunities),
                    "total_value_usd": self._sum_money(stage_opportunities, "value_usd"),
                    "weighted_value_usd": self._sum_money(
                        stage_opportunities,
                        "weighted_value_usd",
                    ),
                }
            )

        return summaries


pipeline_repository = InMemoryPipelineRepository()


def get_pipeline_repository() -> InMemoryPipelineRepository:
    return pipeline_repository
