from contextlib import closing
from decimal import Decimal
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.schemas.users import CurrentUser
from app.services.pipeline_repository import InMemoryPipelineRepository

TABLE_COLUMNS = {
    "pipeline_stages": {"name", "sort_order", "default_probability", "is_won", "is_lost"},
    "opportunities": {
        "company_id",
        "contact_id",
        "stage_id",
        "name",
        "service",
        "value_eur",
        "probability",
        "expected_close_date",
        "owner_id",
        "need",
        "blockers",
        "competitor",
        "next_action",
        "next_action_due_at",
        "lost_reason",
    },
    "activities": {
        "company_id",
        "contact_id",
        "opportunity_id",
        "activity_type",
        "subject",
        "notes",
        "occurred_at",
        "owner_id",
    },
    "tasks": {
        "company_id",
        "opportunity_id",
        "owner_id",
        "title",
        "description",
        "due_at",
        "priority",
        "status",
        "outcome",
        "completed_at",
    },
    "notes": {"company_id", "contact_id", "opportunity_id", "body"},
}


class PostgresPipelineRepository(InMemoryPipelineRepository):
    """Pipeline repository backed by the PostgreSQL database provided by Supabase."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        super().__init__()

    def _connection(self):
        return closing(psycopg.connect(self.database_url, row_factory=dict_row))

    def list_records(self, collection: str) -> list[dict]:
        order = "sort_order" if collection == "pipeline_stages" else "created_at"
        archived_filter = "" if collection == "pipeline_stages" else " where archived_at is null"
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(f"select * from public.{collection}{archived_filter} order by {order}")
            records = [self._normalize(row) for row in cursor.fetchall()]
        if collection == "opportunities":
            self._refresh_supporting_data()
            return [self._with_stage_duration(record) for record in records]
        return records

    def get_record(self, collection: str, record_id: str) -> dict | None:
        archived_filter = "" if collection == "pipeline_stages" else " and archived_at is null"
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"select * from public.{collection} where id=%s{archived_filter}",
                (record_id,),
            )
            row = cursor.fetchone()
        if not row:
            return None
        record = self._normalize(row)
        if collection == "opportunities":
            self._refresh_supporting_data()
            return self._with_stage_duration(record)
        return record

    def create_record(self, collection: str, payload: dict, current_user: CurrentUser) -> dict:
        values = self._clean_values(collection, payload)
        if collection == "opportunities":
            values["weighted_value_eur"] = self._weighted_value(values)
        if collection != "pipeline_stages":
            values.update(created_by=current_user.id, updated_by=current_user.id)
        columns = list(values)
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"insert into public.{collection} ({', '.join(columns)}) values "
                f"({', '.join(['%s'] * len(columns))}) returning *",
                list(values.values()),
            )
            row = cursor.fetchone()
            connection.commit()
        return self._opportunity_duration(collection, self._normalize(row))

    def update_record(
        self, collection: str, record_id: str, payload: dict, current_user: CurrentUser
    ) -> dict | None:
        values = self._clean_values(collection, payload)
        current = self.get_record(collection, record_id)
        if current is None:
            return None
        if collection == "opportunities":
            values["weighted_value_eur"] = self._weighted_value({**current, **values})
        if collection != "pipeline_stages":
            values["updated_by"] = current_user.id
        if not values:
            return current
        assignments = ", ".join(f"{column}=%s" for column in values)
        archived_filter = "" if collection == "pipeline_stages" else " and archived_at is null"
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"update public.{collection} set {assignments} "
                f"where id=%s{archived_filter} returning *",
                [*values.values(), record_id],
            )
            row = cursor.fetchone()
            connection.commit()
        return self._opportunity_duration(collection, self._normalize(row)) if row else None

    def archive_record(
        self, collection: str, record_id: str, current_user: CurrentUser
    ) -> dict | None:
        if collection == "pipeline_stages":
            return None
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"update public.{collection} set archived_at=now(), updated_by=%s "
                "where id=%s and archived_at is null returning *",
                (current_user.id, record_id),
            )
            row = cursor.fetchone()
            connection.commit()
        return self._opportunity_duration(collection, self._normalize(row)) if row else None

    def move_opportunity_stage(
        self, opportunity_id: str, to_stage_id: str, note: str | None, current_user: CurrentUser
    ) -> tuple[dict, dict] | None:
        opportunity = self.get_record("opportunities", opportunity_id)
        if opportunity is None:
            return None
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "update public.opportunities set stage_id=%s, updated_by=%s "
                "where id=%s and archived_at is null returning *",
                (to_stage_id, current_user.id, opportunity_id),
            )
            updated = cursor.fetchone()
            cursor.execute(
                "insert into public.opportunity_stage_history "
                "(opportunity_id, from_stage_id, to_stage_id, changed_by, note) "
                "values (%s,%s,%s,%s,%s) returning *",
                (opportunity_id, opportunity["stage_id"], to_stage_id, current_user.id, note),
            )
            history = cursor.fetchone()
            connection.commit()
        return self._opportunity_duration(
            "opportunities", self._normalize(updated)
        ), self._normalize(history)

    def list_stage_history(self, opportunity_id: str) -> list[dict]:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "select * from public.opportunity_stage_history where opportunity_id=%s "
                "order by changed_at",
                (opportunity_id,),
            )
            return [self._normalize(row) for row in cursor.fetchall()]

    def stage_exists(self, stage_id: str | UUID) -> bool:
        return self.get_record("pipeline_stages", str(stage_id)) is not None

    def list_all_stage_history(self) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute("select * from public.opportunity_stage_history").fetchall()
            return [self._normalize(row) for row in rows]

    def get_dashboard_summary(self, company_fit_scores=None, company_context=None) -> dict:
        self._refresh_all()
        return super().get_dashboard_summary(company_fit_scores, company_context)

    def _refresh_all(self) -> None:
        for collection in TABLE_COLUMNS:
            records = self.list_records(collection)
            self._collection(collection).clear()
            self._collection(collection).update({record["id"]: record for record in records})
        self._refresh_supporting_data()

    def _refresh_supporting_data(self) -> None:
        stages = self.list_records("pipeline_stages")
        self._pipeline_stages = {record["id"]: record for record in stages}
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute("select * from public.opportunity_stage_history")
            history = [self._normalize(row) for row in cursor.fetchall()]
        self._stage_history = {record["id"]: record for record in history}

    def _clean_values(self, collection: str, payload: dict) -> dict:
        return {key: value for key, value in payload.items() if key in TABLE_COLUMNS[collection]}

    def _opportunity_duration(self, collection: str, record: dict) -> dict:
        if collection != "opportunities":
            return record
        self._refresh_supporting_data()
        return self._with_stage_duration(record)

    @staticmethod
    def _weighted_value(values: dict):
        if values.get("value_eur") is None or values.get("probability") is None:
            return None
        return round(float(values["value_eur"]) * int(values["probability"]) / 100, 2)

    def _normalize(self, value):
        if isinstance(value, dict):
            return {key: self._normalize(item) for key, item in value.items()}
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, Decimal):
            return float(value)
        return value
