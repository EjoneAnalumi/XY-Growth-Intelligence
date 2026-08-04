from uuid import UUID

from app.core.database import supabase


class NoteRepository:
    def create(self, data: dict):
        data = self._convert_types(data)

        response = supabase.table("notes").insert(data).execute()

        return response.data[0] if response.data else None

    def get_all(self):
        response = supabase.table("notes").select("*").execute()

        return response.data

    def get_by_id(self, note_id: str):
        response = supabase.table("notes").select("*").eq("id", note_id).execute()

        return response.data[0] if response.data else None

    def update(self, note_id: str, data: dict):
        data = self._convert_types(data)

        response = supabase.table("notes").update(data).eq("id", note_id).execute()

        return response.data[0] if response.data else None

    def delete(self, note_id: str):
        response = supabase.table("notes").delete().eq("id", note_id).execute()

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
