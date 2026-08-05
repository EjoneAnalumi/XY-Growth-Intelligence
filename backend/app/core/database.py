from functools import lru_cache
from os import getenv
from typing import Any


class SupabaseUnavailableError(RuntimeError):
    pass


@lru_cache
def get_supabase_client() -> Any:
    supabase_url = getenv("SUPABASE_URL")
    supabase_key = getenv("SUPABASE_ANON_KEY") or getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise SupabaseUnavailableError("Supabase environment variables are not configured.")

    try:
        from supabase import create_client
    except ModuleNotFoundError as exc:
        raise SupabaseUnavailableError("Supabase dependency is not installed.") from exc

    return create_client(supabase_url, supabase_key)
