from functools import lru_cache
from os import getenv


class Settings:
    app_name: str
    app_env: str
    auth_mode: str
    log_level: str

    def __init__(self) -> None:
        self.app_name = getenv("APP_NAME", "XY CYBER Growth Intelligence API")
        self.app_env = getenv("APP_ENV", "local")
        self.auth_mode = getenv("AUTH_MODE", "local")
        self.log_level = getenv("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
