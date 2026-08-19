"""Local Supabase RLS allow/deny probes for Week 2 Day 10.

Requires a running local database (`supabase start` / after `supabase db reset`).
Skipped automatically when the database is unreachable.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from uuid import uuid4

import pytest

psycopg = pytest.importorskip("psycopg")

DATABASE_URL = os.getenv(
    "SUPABASE_DB_URL",
    "postgresql://postgres:postgres@127.0.0.1:54322/postgres",
)

ADMIN_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1"
BD_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1"
RO_ID = "cccccccc-cccc-4ccc-8ccc-ccccccccccc1"
TA_ID = "dddddddd-dddd-4ddd-8ddd-ddddddddddd1"


def _connect():
    try:
        return psycopg.connect(DATABASE_URL, autocommit=False, connect_timeout=5)
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Local Supabase database unavailable: {exc}")


@pytest.fixture(scope="module")
def db() -> Iterator:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.icp_rules')")
            icp_rules = cursor.fetchone()[0]
            cursor.execute("SELECT to_regclass('public.opportunities')")
            opportunities = cursor.fetchone()[0]
            if icp_rules is None or opportunities is None:
                connection.rollback()
                connection.close()
                pytest.skip("Required Week 2 tables missing after migrations")

            for user_id, email, role, full_name in [
                (ADMIN_ID, "admin-rls@example.com", "admin", "Admin RLS"),
                (BD_ID, "bd-rls@example.com", "business_development", "BD RLS"),
                (RO_ID, "ro-rls@example.com", "read_only", "RO RLS"),
                (TA_ID, "ta-rls@example.com", "technical_analyst", "TA RLS"),
            ]:
                cursor.execute(
                    """
                    INSERT INTO auth.users (
                        id, instance_id, aud, role, email, encrypted_password,
                        email_confirmed_at, raw_app_meta_data, raw_user_meta_data,
                        created_at, updated_at
                    )
                    VALUES (
                        %s::uuid,
                        '00000000-0000-0000-0000-000000000000',
                        'authenticated',
                        'authenticated',
                        %s,
                        crypt('pass', gen_salt('bf')),
                        now(),
                        '{"provider":"email","providers":["email"]}'::jsonb,
                        '{}'::jsonb,
                        now(),
                        now()
                    )
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (user_id, email),
                )
                cursor.execute(
                    """
                    INSERT INTO public.profiles (id, full_name, role, active)
                    VALUES (%s::uuid, %s, %s, true)
                    ON CONFLICT (id) DO UPDATE
                    SET role = EXCLUDED.role,
                        active = true,
                        full_name = EXCLUDED.full_name
                    """,
                    (user_id, full_name, role),
                )
        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        raise

    yield connection
    connection.close()


def _as_role(cursor, user_id: str | None, role: str) -> None:
    cursor.execute("RESET ROLE")
    if user_id is None:
        cursor.execute("SELECT set_config('request.jwt.claim.sub', '', true)")
        cursor.execute("SELECT set_config('request.jwt.claims', '{}', true)")
    else:
        claims = f'{{"sub":"{user_id}","role":"authenticated"}}'
        cursor.execute(
            "SELECT set_config('request.jwt.claim.sub', %s, true)",
            (user_id,),
        )
        cursor.execute(
            "SELECT set_config('request.jwt.claims', %s, true)",
            (claims,),
        )
        cursor.execute(
            "SELECT set_config('request.jwt.claim.role', %s, true)",
            ("authenticated",),
        )
    cursor.execute(f"SET LOCAL ROLE {role}")


def _expect_denied(connection, cursor, sql: str, params: tuple | None = None) -> None:
    cursor.execute("SAVEPOINT rls_deny_probe")
    try:
        cursor.execute(sql, params)
    except psycopg.Error:
        cursor.execute("ROLLBACK TO SAVEPOINT rls_deny_probe")
        return
    cursor.execute("ROLLBACK TO SAVEPOINT rls_deny_probe")
    pytest.fail("Expected RLS denial, but statement succeeded")


def test_rls_enabled_on_week2_tables(db) -> None:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT relname
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind = 'r'
              AND relname = ANY(%s)
              AND NOT c.relrowsecurity
            ORDER BY 1
            """,
            (
                [
                    "profiles",
                    "companies",
                    "contacts",
                    "pipeline_stages",
                    "opportunities",
                    "opportunity_stage_history",
                    "activities",
                    "tasks",
                    "notes",
                    "icp_rules",
                    "icp_score_results",
                ],
            ),
        )
        missing = [row[0] for row in cursor.fetchall()]
        assert missing == []
    db.commit()


def test_anon_cannot_read_business_tables(db) -> None:
    with db.cursor() as cursor:
        _as_role(cursor, None, "anon")
        _expect_denied(db, cursor, "SELECT COUNT(*) FROM public.companies")
        _expect_denied(db, cursor, "SELECT COUNT(*) FROM public.opportunities")
        _expect_denied(db, cursor, "SELECT COUNT(*) FROM public.activities")
        cursor.execute("RESET ROLE")
    db.rollback()


def test_read_only_can_select_but_cannot_insert_sales_rows(db) -> None:
    with db.cursor() as cursor:
        cursor.execute("SELECT id FROM public.companies LIMIT 1")
        company_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM public.pipeline_stages LIMIT 1")
        stage_id = cursor.fetchone()[0]

        _as_role(cursor, RO_ID, "authenticated")
        cursor.execute("SELECT COUNT(*) FROM public.companies")
        assert cursor.fetchone()[0] > 0
        cursor.execute("SELECT COUNT(*) FROM public.opportunities")
        assert cursor.fetchone()[0] > 0

        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.companies (name, created_by, updated_by)
            VALUES ('RO Denied Company', %s::uuid, %s::uuid)
            """,
            (RO_ID, RO_ID),
        )
        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.opportunities (
                company_id, stage_id, name, created_by, updated_by
            )
            VALUES (%s::uuid, %s::uuid, 'RO Denied Opportunity', %s::uuid, %s::uuid)
            """,
            (company_id, stage_id, RO_ID, RO_ID),
        )
        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.activities (
                company_id, activity_type, subject, created_by, updated_by
            )
            VALUES (%s::uuid, 'call', 'RO Denied Activity', %s::uuid, %s::uuid)
            """,
            (company_id, RO_ID, RO_ID),
        )
        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.tasks (title, created_by, updated_by)
            VALUES ('RO Denied Task', %s::uuid, %s::uuid)
            """,
            (RO_ID, RO_ID),
        )
        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.notes (body, created_by, updated_by)
            VALUES ('RO Denied Note', %s::uuid, %s::uuid)
            """,
            (RO_ID, RO_ID),
        )
        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.pipeline_stages (
                name, sort_order, default_probability
            )
            VALUES ('RO Denied Stage', 991, 10)
            """,
        )
        cursor.execute("RESET ROLE")
    db.rollback()


def test_technical_analyst_cannot_insert_opportunities(db) -> None:
    with db.cursor() as cursor:
        cursor.execute("SELECT id FROM public.companies LIMIT 1")
        company_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM public.pipeline_stages LIMIT 1")
        stage_id = cursor.fetchone()[0]

        _as_role(cursor, TA_ID, "authenticated")
        cursor.execute("SELECT COUNT(*) FROM public.opportunities")
        assert cursor.fetchone()[0] > 0
        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.opportunities (
                company_id, stage_id, name, created_by, updated_by
            )
            VALUES (%s::uuid, %s::uuid, 'TA Denied Opportunity', %s::uuid, %s::uuid)
            """,
            (company_id, stage_id, TA_ID, TA_ID),
        )
        cursor.execute("RESET ROLE")
    db.rollback()


def test_business_development_writer_allow_and_admin_only_deny(db) -> None:
    company_name = f"BD Allowed {uuid4().hex[:8]}"
    opportunity_name = f"BD Opp {uuid4().hex[:8]}"

    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM public.pipeline_stages WHERE name = 'Identified' LIMIT 1"
        )
        stage_id = cursor.fetchone()[0]

        _as_role(cursor, BD_ID, "authenticated")
        cursor.execute("SELECT auth.uid(), public.current_user_role()")
        auth_uid, role = cursor.fetchone()
        assert str(auth_uid) == BD_ID
        assert role == "business_development"

        cursor.execute(
            """
            INSERT INTO public.companies (name, created_by, updated_by)
            VALUES (%s, %s::uuid, %s::uuid)
            RETURNING id
            """,
            (company_name, BD_ID, BD_ID),
        )
        company_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO public.opportunities (
                company_id, stage_id, name, value_usd, probability,
                created_by, updated_by
            )
            VALUES (%s::uuid, %s::uuid, %s, 10000, 20, %s::uuid, %s::uuid)
            RETURNING id
            """,
            (company_id, stage_id, opportunity_name, BD_ID, BD_ID),
        )
        opportunity_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO public.activities (
                company_id, opportunity_id, activity_type, subject,
                created_by, updated_by
            )
            VALUES (
                %s::uuid, %s::uuid, 'meeting', 'BD Allowed Activity',
                %s::uuid, %s::uuid
            )
            """,
            (company_id, opportunity_id, BD_ID, BD_ID),
        )
        cursor.execute(
            """
            INSERT INTO public.tasks (
                company_id, opportunity_id, title, priority, status,
                created_by, updated_by
            )
            VALUES (
                %s::uuid, %s::uuid, 'BD Allowed Task', 'high', 'open',
                %s::uuid, %s::uuid
            )
            """,
            (company_id, opportunity_id, BD_ID, BD_ID),
        )
        cursor.execute(
            """
            INSERT INTO public.notes (company_id, body, created_by, updated_by)
            VALUES (%s::uuid, 'BD Allowed Note', %s::uuid, %s::uuid)
            """,
            (company_id, BD_ID, BD_ID),
        )
        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.pipeline_stages (
                name, sort_order, default_probability
            )
            VALUES (%s, 992, 10)
            """,
            (f"BD AdminOnly {uuid4().hex[:8]}",),
        )
        cursor.execute("RESET ROLE")
    db.commit()


def test_admin_can_insert_pipeline_stage(db) -> None:
    with db.cursor() as cursor:
        _as_role(cursor, ADMIN_ID, "authenticated")
        cursor.execute("SELECT auth.uid(), public.current_user_role()")
        auth_uid, role = cursor.fetchone()
        assert str(auth_uid) == ADMIN_ID
        assert role == "admin"
        cursor.execute(
            """
            INSERT INTO public.pipeline_stages (
                name, sort_order, default_probability
            )
            VALUES (%s, 993, 10)
            """,
            (f"Admin Stage {uuid4().hex[:8]}",),
        )
        cursor.execute("RESET ROLE")
    db.commit()


def test_authenticated_can_read_icp_rules_and_writers_can_insert_scores(db) -> None:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id FROM public.companies
            WHERE name LIKE 'BD Allowed%%'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
        company_row = cursor.fetchone()
        assert company_row is not None
        company_id = company_row[0]

        _as_role(cursor, RO_ID, "authenticated")
        cursor.execute("SELECT COUNT(*) FROM public.icp_rules")
        assert cursor.fetchone()[0] > 0
        cursor.execute("RESET ROLE")

        _as_role(cursor, BD_ID, "authenticated")
        cursor.execute(
            """
            INSERT INTO public.icp_score_results (
                company_id, score, max_score, tier, explanations, calculated_by
            )
            VALUES (%s::uuid, 80, 100, 'strong_fit', '[]'::jsonb, %s::uuid)
            """,
            (company_id, BD_ID),
        )
        cursor.execute("RESET ROLE")

        _as_role(cursor, RO_ID, "authenticated")
        _expect_denied(
            db,
            cursor,
            """
            INSERT INTO public.icp_score_results (
                company_id, score, max_score, tier, explanations, calculated_by
            )
            VALUES (%s::uuid, 10, 100, 'low_fit', '[]'::jsonb, %s::uuid)
            """,
            (company_id, RO_ID),
        )
        cursor.execute("RESET ROLE")
    db.commit()
