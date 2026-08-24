from contextlib import closing

import psycopg
from psycopg.rows import dict_row

from app.schemas.users import AuditLogResponse, CurrentUser, UserProfile, UserRoleUpdate


class UserRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connection(self):
        return closing(psycopg.connect(self.database_url, row_factory=dict_row))

    def get_profile(self, user_id: str, email: str) -> CurrentUser | None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "select id, full_name, role, active from public.profiles where id=%s",
                (user_id,),
            )
            row = cursor.fetchone()
            if not row or not row["active"]:
                return None
            cursor.execute(
                "update public.profiles set last_login_at=now() where id=%s",
                (user_id,),
            )
            connection.commit()
        return CurrentUser(
            id=str(row["id"]),
            email=email,
            full_name=row["full_name"] or email,
            role=row["role"],
        )

    def list_profiles(self) -> list[UserProfile]:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "select p.*, u.email from public.profiles p "
                "join auth.users u on u.id=p.id order by lower(coalesce(p.full_name,u.email))"
            )
            return [
                UserProfile.model_validate({**row, "id": str(row["id"])})
                for row in cursor.fetchall()
            ]

    def update_profile(self, user_id: str, payload: UserRoleUpdate) -> UserProfile | None:
        values = payload.model_dump(exclude_unset=True)
        if not values:
            profiles = [profile for profile in self.list_profiles() if profile.id == user_id]
            return profiles[0] if profiles else None
        assignments = ", ".join(f"{key}=%s" for key in values)
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"update public.profiles set {assignments} where id=%s returning *",
                [*values.values(), user_id],
            )
            row = cursor.fetchone()
            if not row:
                return None
            cursor.execute("select email from auth.users where id=%s", (user_id,))
            email = cursor.fetchone()["email"]
            connection.commit()
        return UserProfile.model_validate({**row, "id": str(row["id"]), "email": email})

    def list_audit_logs(self, limit: int = 100) -> list[AuditLogResponse]:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "select a.*, p.full_name user_name from public.audit_logs a "
                "left join public.profiles p on p.id=a.user_id "
                "order by a.changed_at desc limit %s",
                (limit,),
            )
            return [
                AuditLogResponse.model_validate(
                    {
                        **row,
                        "id": str(row["id"]),
                        "entity_id": str(row["entity_id"]),
                        "user_id": str(row["user_id"]) if row["user_id"] else None,
                    }
                )
                for row in cursor.fetchall()
            ]

    def record_audit(self, actor_id: str, entity_id: str, action: str) -> None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "insert into public.audit_logs (user_id, entity_type, entity_id, action) "
                "values (%s, 'users', %s, %s)",
                (actor_id, entity_id, action),
            )
            connection.commit()
