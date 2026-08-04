from uuid import UUID

from app.core.database import supabase


class ActivityRepository:
    def create(self, data: dict):
        data = self._convert_types(data)

        response = supabase.table("activities").insert(data).execute()

        return response.data[0] if response.data else None

    def get_all(self):
        response = supabase.table("activities").select("*").execute()

        return response.data

    def get_by_id(self, activity_id: str):
        response = supabase.table("activities").select("*").eq("id", activity_id).execute()

        return response.data[0] if response.data else None

    def update(self, activity_id: str, data: dict):
        data = self._convert_types(data)

        response = supabase.table("activities").update(data).eq("id", activity_id).execute()

        return response.data[0] if response.data else None

    def delete(self, activity_id: str):
        response = supabase.table("activities").delete().eq("id", activity_id).execute()

        return response.data

    def _convert_types(self, data: dict):
        converted = {}

        for key, value in data.items():
            if isinstance(value, UUID):
                converted[key] = str(value)

            elif hasattr(value, "isoformat"):
                converted[key] = value.isoformat()

            else:
                converted[key] = value

        return converted
