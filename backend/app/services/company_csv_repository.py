from __future__ import annotations

from contextlib import closing
from os import getenv

import psycopg
from psycopg.rows import dict_row

from app.schemas.companies import CompanyCreate
from app.schemas.users import CurrentUser
from app.services.company_csv import CANONICAL_COLUMNS


class CompanyCsvPersistenceError(RuntimeError):
    pass


class CompanyCsvDuplicateError(RuntimeError):
    def __init__(self, fields: list[str]) -> None:
        self.fields = fields
        super().__init__("Duplicate companies.")


class PostgresCompanyCsvRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def import_companies(self, companies: list[CompanyCreate], current_user: CurrentUser) -> int:
        names = [company.name.casefold() for company in companies]
        domains = [company.domain.casefold() for company in companies if company.domain]
        try:
            with (
                closing(psycopg.connect(self.database_url)) as connection,
                connection.cursor() as cursor,
            ):
                cursor.execute(
                    """
                    select lower(name) as name, lower(domain) as domain
                    from public.companies
                    where archived_at is null
                      and (lower(name) = any(%s) or lower(domain) = any(%s))
                    """,
                    (names, domains),
                )
                duplicate_fields: set[str] = set()
                for name, domain in cursor.fetchall():
                    if name in names:
                        duplicate_fields.add("name")
                    if domain in domains:
                        duplicate_fields.add("domain")
                if duplicate_fields:
                    raise CompanyCsvDuplicateError(sorted(duplicate_fields))

                columns = ", ".join((*CANONICAL_COLUMNS, "created_by", "updated_by"))
                placeholders = ", ".join(["%s"] * (len(CANONICAL_COLUMNS) + 2))
                statement = f"insert into public.companies ({columns}) values ({placeholders})"
                user_id = current_user.id
                cursor.executemany(
                    statement,
                    [
                        (*company.model_dump().values(), user_id, user_id)
                        for company in companies
                    ],
                )
                connection.commit()
                return len(companies)
        except CompanyCsvDuplicateError:
            raise
        except psycopg.errors.UniqueViolation as exc:
            raise CompanyCsvDuplicateError(["name_or_domain"]) from exc
        except psycopg.Error as exc:
            raise CompanyCsvPersistenceError("CSV persistence is unavailable.") from exc

    def export_companies(self) -> list[CompanyCreate]:
        columns = ", ".join(CANONICAL_COLUMNS)
        try:
            with closing(psycopg.connect(self.database_url, row_factory=dict_row)) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"select {columns} from public.companies "
                        "where archived_at is null order by lower(name), id"
                    )
                    return [CompanyCreate.model_validate(row) for row in cursor.fetchall()]
        except psycopg.Error as exc:
            raise CompanyCsvPersistenceError("CSV persistence is unavailable.") from exc


def get_postgres_company_csv_repository() -> PostgresCompanyCsvRepository | None:
    database_url = getenv("DATABASE_URL")
    return PostgresCompanyCsvRepository(database_url) if database_url else None
