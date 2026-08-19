from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.activities import router as activities_router
from app.api.companies import router as companies_router
from app.api.contacts import router as contacts_router
from app.api.dashboard import router as dashboard_router
from app.api.health import router as health_router
from app.api.notes import router as notes_router
from app.api.opportunities import router as opportunities_router
from app.api.pipeline_stages import router as pipeline_stages_router
from app.api.reports import router as reports_router
from app.api.security_scans import router as security_scans_router
from app.api.tasks import router as tasks_router
from app.api.users import router as users_router
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging, register_request_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
register_request_logging(app)
register_error_handlers(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(contacts_router)


app.include_router(opportunities_router)
app.include_router(pipeline_stages_router)
app.include_router(activities_router)
app.include_router(tasks_router)
app.include_router(notes_router)
app.include_router(dashboard_router)
app.include_router(security_scans_router)
app.include_router(reports_router)
