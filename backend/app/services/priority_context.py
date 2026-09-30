from contextlib import closing
from os import getenv

import psycopg


def priority_context(growth):
    companies = growth.list_companies(growth.count_companies(), 0)
    result = {str(c.id): {"strategic_importance": c.strategic_importance} for c in companies}
    url = getenv("DATABASE_URL")
    if url:
        with closing(psycopg.connect(url)) as connection:
            rows = connection.execute(
                "select distinct s.company_id from public.security_scans s "
                "join public.security_findings f on f.security_scan_id=s.id "
                "where s.status='completed' and s.approved=true "
                "and f.finding=true and f.status not in ('error','timeout') "
                "and f.severity in ('medium','high','critical')"
            ).fetchall()
            for row in rows:
                if str(row[0]) in result:
                    result[str(row[0])]["snapshot_observations"] = True
    return result
