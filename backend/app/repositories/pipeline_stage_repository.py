from app.core.database import supabase


class PipelineStageRepository:
    def create(self, data: dict):
        response = supabase.table("pipeline_stages").insert(data).execute()
        return response.data[0] if response.data else None

    def get_all(self):
        response = (
            supabase
            .table("pipeline_stages")
            .select("*")
            .order("sort_order")
            .execute()
        )
        return response.data

    def get_by_id(self, stage_id: str):
        response = (
            supabase
            .table("pipeline_stages")
            .select("*")
            .eq("id", stage_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def update(self, stage_id: str, data: dict):
        response = (
            supabase
            .table("pipeline_stages")
            .update(data)
            .eq("id", stage_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def delete(self, stage_id: str):
        response = (
            supabase
            .table("pipeline_stages")
            .delete()
            .eq("id", stage_id)
            .execute()
        )
        return response.data
