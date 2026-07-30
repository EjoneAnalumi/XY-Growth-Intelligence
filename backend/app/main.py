from fastapi import FastAPI

from app.api.companies import router as companies_router
from app.api.contacts import router as contacts_router
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(contacts_router)
