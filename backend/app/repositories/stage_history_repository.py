from app.core.database import supabase


class StageHistoryRepository:
    def create(self, data: dict):
        payload = {
            "opportunity_id": data["opportunity_id"],
            "from_stage_id": data.get("from_stage_id"),
            "to_stage_id": data["to_stage_id"],
            "note": data.get("note"),
        }

        if data.get("changed_at"):
            payload["changed_at"] = data["changed_at"]

        response = supabase.table("opportunity_stage_history").insert(payload).execute()

        return response.data[0]
