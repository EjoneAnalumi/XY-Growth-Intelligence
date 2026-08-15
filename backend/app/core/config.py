from functools import lru_cache
from os import getenv


class Settings:
    app_name: str
    app_env: str
    auth_mode: str
    log_level: str
    cors_origins: list[str]

    def __init__(self) -> None:
        self.app_name = getenv("APP_NAME", "XY CYBER Growth Intelligence API")
        self.app_env = getenv("APP_ENV", "local")
        self.auth_mode = getenv("AUTH_MODE", "local")
        self.log_level = getenv("LOG_LEVEL", "INFO")
        self.database_url = getenv("DATABASE_URL")
        self.supabase_url = getenv("SUPABASE_URL")
        self.supabase_service_role_key = getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.cors_origins = [
            origin.strip()
            for origin in getenv(
                "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
            ).split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
