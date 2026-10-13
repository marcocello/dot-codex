import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine

from app.api.routes import router
from app.log import configure_logging, request_id
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        config = settings or Settings()
        configure_logging(config.log_level, config.log_format)
        app.state.engine = create_engine(config.database_url, pool_pre_ping=True)
        try:
            yield
        finally:
            app.state.engine.dispose()

    application = FastAPI(title="App API", lifespan=lifespan)

    @application.middleware("http")
    async def request_log(request, call_next):
        token = request_id.set(uuid.uuid4().hex)
        started = time.monotonic()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id.get()
            return response
        finally:
            route = request.scope.get("route")
            logging.getLogger("api.request").log(
                logging.ERROR if status >= 500 else logging.INFO,
                "request_completed",
                extra={
                    "details": {
                        "method": request.method,
                        "route": getattr(route, "path", "unmatched"),
                        "status": status,
                        "elapsed_ms": round((time.monotonic() - started) * 1000),
                    }
                },
            )
            request_id.reset(token)

    application.include_router(router)
    return application


app = create_app()
