from contextlib import closing
from os import getenv

import psycopg
from fastapi import HTTPException


def validate_assignee(owner_id):
    if owner_id is None:
        return
    url = getenv("DATABASE_URL")
    if url:
        with closing(psycopg.connect(url)) as conn:
            valid = conn.execute(
                "select 1 from public.profiles where id=%s and active and role <> 'read_only'",
                (str(owner_id),),
            ).fetchone()
    else:
        from app.core.auth import LOCAL_DEMO_TOKENS

        valid = any(
            str(user.id) == str(owner_id) and user.role != "read_only"
            for user in LOCAL_DEMO_TOKENS.values()
        )
    if not valid:
        raise HTTPException(
            422, "Choose an active staff assignee; Read Only users cannot receive tasks."
        )
