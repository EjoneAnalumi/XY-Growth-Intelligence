"""Small persisted service catalogue and configurable ICP weights."""

from contextlib import closing
from os import getenv
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

DEFAULT_WEIGHTS = {
    "industry_fit": 25,
    "company_size": 20,
    "revenue_fit": 15,
    "regulatory_context": 15,
    "cloud_usage": 10,
    "geography": 5,
    "lead_source": 5,
    "lifecycle": 5,
}
DEFAULT_SERVICES = [
    "Cloud Security Assessment",
    "Compliance Readiness Review",
    "Managed SOC",
    "Cyber Risk Snapshot",
    "External Attack Surface Review",
    "Executive Security Workshop",
    "Security Discovery Workshop",
]


class AdministrationRepository:
    def __init__(self):
        self.reset()

    def reset(self):
        self.weights = dict(DEFAULT_WEIGHTS)
        self.services = [
            {"id": str(uuid4()), "name": name, "description": "", "active": True}
            for name in DEFAULT_SERVICES
        ]

    def get_weights(self):
        url = getenv("DATABASE_URL")
        if not url:
            return dict(self.weights)
        with closing(psycopg.connect(url, row_factory=dict_row)) as conn:
            rows = conn.execute("select rule_key, max_points from public.icp_rules").fetchall()
            return {row["rule_key"]: row["max_points"] for row in rows}

    def save_weights(self, weights, actor):
        url = getenv("DATABASE_URL")
        if not url:
            self.weights = dict(weights)
            return
        with closing(psycopg.connect(url)) as conn:
            # Serialize whole-rule-set writes; readers see either committed configuration.
            conn.execute("lock table public.icp_rules in exclusive mode")
            for key, weight in weights.items():
                row = conn.execute(
                    "update public.icp_rules set max_points=%s where rule_key=%s returning id",
                    (weight, key),
                ).fetchone()
                self._audit(conn, actor, "icp_rules", row[0], "updated")
            conn.commit()

    def list_services(self):
        url = getenv("DATABASE_URL")
        if not url:
            return list(self.services)
        with closing(psycopg.connect(url, row_factory=dict_row)) as conn:
            return conn.execute("select * from public.services order by name").fetchall()

    def save_service(self, values, actor, service_id=None):
        url = getenv("DATABASE_URL")
        if not url:
            if service_id:
                item = next((s for s in self.services if s["id"] == str(service_id)), None)
                if item is None:
                    return None
                item.update(values)
                return item
            item = {"id": str(uuid4()), **values}
            self.services.append(item)
            return item
        with closing(psycopg.connect(url, row_factory=dict_row)) as conn:
            if service_id:
                row = conn.execute(
                    "update public.services set name=%s, description=%s, active=%s, "
                    "updated_at=now() where id=%s returning *",
                    (values["name"], values["description"], values["active"], service_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "insert into public.services(name, description, active) "
                    "values (%s,%s,%s) returning *",
                    (values["name"], values["description"], values["active"]),
                ).fetchone()
            if row:
                self._audit(
                    conn, actor, "services", row["id"], "updated" if service_id else "created"
                )
            conn.commit()
            return row

    @staticmethod
    def _audit(conn, actor, entity, entity_id, action):
        conn.execute(
            "insert into public.audit_logs(user_id, entity_type, entity_id, action) "
            "values (%s,%s,%s,%s)",
            (actor.id, entity, entity_id, action),
        )


administration_repository = AdministrationRepository()
