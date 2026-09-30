"""Personal note deletion never changes the shared note or another user's view."""

from contextlib import closing
from os import getenv

import psycopg

memory_hidden: set[tuple[str, str]] = set()


def hidden_note_ids(user_id) -> set[str]:
    url = getenv("DATABASE_URL")
    if not url:
        return {note for user, note in memory_hidden if user == str(user_id)}
    with closing(psycopg.connect(url)) as conn:
        return {
            str(row[0])
            for row in conn.execute(
                "select note_id from public.note_dismissals where user_id=%s", (str(user_id),)
            ).fetchall()
        }


def hide_note(user_id, note_id) -> None:
    url = getenv("DATABASE_URL")
    if not url:
        memory_hidden.add((str(user_id), str(note_id)))
        return
    with closing(psycopg.connect(url)) as conn:
        conn.execute(
            "insert into public.note_dismissals(user_id,note_id) values(%s,%s) "
            "on conflict do nothing",
            (str(user_id), str(note_id)),
        )
        conn.commit()
