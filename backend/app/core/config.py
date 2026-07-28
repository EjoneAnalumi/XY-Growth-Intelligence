from functools import lru_cache
from os import getenv


class Settings:
    app_env: str
    log_level: str

    def __init__(self) -> None:
        self.app_env = getenv("APP_ENV", "local")
        self.log_level = getenv("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
