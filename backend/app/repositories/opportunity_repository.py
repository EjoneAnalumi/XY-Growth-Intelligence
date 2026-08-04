from app.core.database import supabase


class OpportunityRepository:
    def create(self, data: dict):
        data = self._with_weighted_value(data)

        response = supabase.table("opportunities").insert(data).execute()

        return response.data[0]

    def get_all(self):
        response = supabase.table("opportunities").select("*").is_("archived_at", "null").execute()

        return response.data

    def get_by_id(self, opportunity_id: str):
        response = supabase.table("opportunities").select("*").eq("id", opportunity_id).execute()

        if response.data:
            return response.data[0]

        return None

    def update(self, opportunity_id: str, data: dict):
        current = self.get_by_id(opportunity_id)

        if not current:
            return None

        merged = {**current, **data}
        data = self._with_weighted_value(data, merged)

        response = supabase.table("opportunities").update(data).eq("id", opportunity_id).execute()

        if response.data:
            return response.data[0]

        return None

    def delete(self, opportunity_id: str):
        response = supabase.table("opportunities").delete().eq("id", opportunity_id).execute()

        return response.data

    def _with_weighted_value(self, data: dict, source: dict | None = None):
        if "value_usd" not in data and "probability" not in data:
            return data

        source = source or data
        value = source.get("value_usd")
        probability = source.get("probability")

        if value is None or probability is None:
            data["weighted_value_usd"] = None
            return data

        data["weighted_value_usd"] = round(float(value) * int(probability) / 100, 2)
        return data
