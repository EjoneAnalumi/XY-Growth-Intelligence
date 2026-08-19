import json
import logging
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from fastapi import FastAPI, Request


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        for key in [
            "event",
            "domain",
            "approved",
            "demo_mode",
            "result_statuses",
            "duration_ms",
            "report_id",
            "status",
            "method",
            "path",
            "status_code",
        ]:
            if hasattr(record, key):
                payload[key] = getattr(record, key)

        return json.dumps(payload)


def configure_logging(log_level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def register_request_logging(app: FastAPI) -> None:
    logger = logging.getLogger("app.main")

    @app.middleware("http")
    async def log_request_completion(request: Request, call_next):
        started_at = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        finally:
            logger.info(
                "request_completed",
                extra={
                    "event": "request_completed",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round((perf_counter() - started_at) * 1000, 2),
                },
            )
        return response
