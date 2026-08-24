from contextlib import closing
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.schemas.companies import CompanyCreate, CompanyResponse
from app.schemas.contacts import ContactCreate, ContactResponse
from app.schemas.icp import IcpScoreResponse
from app.schemas.users import CurrentUser
from app.scoring.icp import IcpScore


class PostgresGrowthRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connection(self):
        return closing(psycopg.connect(self.database_url, row_factory=dict_row))

    def list_companies(self, limit: int, offset: int) -> list[CompanyResponse]:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "select * from public.companies where archived_at is null "
                "order by lower(name), id limit %s offset %s",
                (limit, offset),
            )
            return [CompanyResponse.model_validate(row) for row in cursor.fetchall()]

    def count_companies(self) -> int:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "select count(*) as count from public.companies where archived_at is null"
            )
            return cursor.fetchone()["count"]

    def find_company_duplicates(self, companies: list[CompanyCreate]) -> list[str]:
        names = [item.name.casefold() for item in companies]
        domains = [item.domain.casefold() for item in companies if item.domain]
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "select lower(name) name, lower(domain) domain from public.companies "
                "where archived_at is null and (lower(name) = any(%s) or lower(domain) = any(%s))",
                (names, domains),
            )
            fields = set()
            for row in cursor.fetchall():
                if row["name"] in names:
                    fields.add("name")
                if row["domain"] in domains:
                    fields.add("domain")
            return sorted(fields)

    def get_company_fit_scores(self) -> dict[str, int | None]:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute("select id, fit_score from public.companies where archived_at is null")
            return {str(row["id"]): row["fit_score"] for row in cursor.fetchall()}

    def create_company(self, payload: CompanyCreate, current_user: CurrentUser) -> CompanyResponse:
        values = payload.model_dump(mode="json")
        columns = [*values, "created_by", "updated_by"]
        params = [*values.values(), current_user.id, current_user.id]
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"insert into public.companies ({', '.join(columns)}) values "
                f"({', '.join(['%s'] * len(columns))}) returning *",
                params,
            )
            row = cursor.fetchone()
            connection.commit()
            return CompanyResponse.model_validate(row)

    def get_company(self, company_id: UUID) -> CompanyResponse | None:
        return self._get("companies", company_id, CompanyResponse)

    def update_company(self, company_id: UUID, payload: dict, user: CurrentUser):
        return self._update("companies", company_id, payload, user, CompanyResponse)

    def archive_company(self, company_id: UUID, user: CurrentUser):
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "update public.companies set archived_at=now(), status='inactive', "
                "updated_by=%s where id=%s and archived_at is null returning *",
                (user.id, company_id),
            )
            row = cursor.fetchone()
            if row:
                for table in ("contacts", "opportunities", "activities", "tasks", "notes"):
                    cursor.execute(
                        f"update public.{table} set archived_at=now(), updated_by=%s "
                        "where company_id=%s and archived_at is null",
                        (user.id, company_id),
                    )
            connection.commit()
        return CompanyResponse.model_validate(row) if row else None

    def list_contacts(self, company_id: UUID | None, limit: int, offset: int):
        where = "archived_at is null"
        params: list[object] = []
        if company_id:
            where += " and company_id = %s"
            params.append(company_id)
        params.extend([limit, offset])
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"select * from public.contacts where {where} order by lower(last_name), "
                "lower(first_name), id limit %s offset %s",
                params,
            )
            return [ContactResponse.model_validate(row) for row in cursor.fetchall()]

    def count_contacts(self, company_id: UUID | None) -> int:
        query = "select count(*) count from public.contacts where archived_at is null"
        params = ()
        if company_id:
            query += " and company_id = %s"
            params = (company_id,)
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()["count"]

    def create_contact(self, payload: ContactCreate, current_user: CurrentUser):
        if self.get_company(payload.company_id) is None:
            return None
        values = payload.model_dump(mode="json")
        columns = [*values, "owner_id", "created_by", "updated_by"]
        params = [*values.values(), current_user.id, current_user.id, current_user.id]
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"insert into public.contacts ({', '.join(columns)}) values "
                f"({', '.join(['%s'] * len(columns))}) returning *",
                params,
            )
            row = cursor.fetchone()
            connection.commit()
            return ContactResponse.model_validate(row)

    def get_contact(self, contact_id: UUID):
        return self._get("contacts", contact_id, ContactResponse)

    def update_contact(self, contact_id: UUID, payload: dict, user: CurrentUser):
        if payload.get("company_id") and self.get_company(payload["company_id"]) is None:
            return None
        return self._update("contacts", contact_id, payload, user, ContactResponse)

    def archive_contact(self, contact_id: UUID, user: CurrentUser):
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "update public.contacts set archived_at=now(), updated_by=%s "
                "where id=%s and archived_at is null returning *",
                (user.id, contact_id),
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "update public.opportunities set contact_id=null, updated_by=%s "
                    "where contact_id=%s and archived_at is null",
                    (user.id, contact_id),
                )
                cursor.execute(
                    "update public.activities set contact_id=null, updated_by=%s "
                    "where contact_id=%s and archived_at is null",
                    (user.id, contact_id),
                )
                cursor.execute(
                    "update public.notes set contact_id=null, updated_by=%s "
                    "where contact_id=%s and archived_at is null",
                    (user.id, contact_id),
                )
            connection.commit()
        return ContactResponse.model_validate(row) if row else None

    def save_icp_score(self, company_id: UUID, score: IcpScore, current_user: CurrentUser):
        company = self.get_company(company_id)
        if company is None:
            return None
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "insert into public.icp_scores (company_id, score, max_score, tier, explanations, "
                "calculated_by) values (%s,%s,%s,%s,%s,%s) returning *",
                (
                    company_id,
                    score.score,
                    score.max_score,
                    score.tier,
                    psycopg.types.json.Jsonb(score.explanations),
                    current_user.id,
                ),
            )
            result = cursor.fetchone()
            cursor.execute(
                "update public.companies set fit_score=%s, updated_by=%s where id=%s",
                (score.score, current_user.id, company_id),
            )
            connection.commit()
            return IcpScoreResponse.model_validate(result)

    def get_latest_icp_score(self, company_id: UUID):
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "select * from public.icp_scores where company_id=%s "
                "order by calculated_at desc limit 1",
                (company_id,),
            )
            row = cursor.fetchone()
            return IcpScoreResponse.model_validate(row) if row else None

    def _get(self, table, record_id, model):
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"select * from public.{table} where id=%s and archived_at is null", (record_id,)
            )
            row = cursor.fetchone()
            return model.model_validate(row) if row else None

    def _update(self, table, record_id, payload, user, model):
        if not payload:
            return self._get(table, record_id, model)
        payload = {**payload, "updated_by": user.id}
        assignments = ", ".join(f"{key}=%s" for key in payload)
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"update public.{table} set {assignments} "
                "where id=%s and archived_at is null returning *",
                (*payload.values(), record_id),
            )
            row = cursor.fetchone()
            connection.commit()
            return model.model_validate(row) if row else None
