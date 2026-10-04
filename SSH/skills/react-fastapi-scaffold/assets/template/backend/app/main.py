from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine

from app.api.routes import router
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        config = settings or Settings()
        app.state.engine = create_engine(config.database_url, pool_pre_ping=True)
        try:
            yield
        finally:
            app.state.engine.dispose()

    application = FastAPI(title="App API", lifespan=lifespan)
    application.include_router(router)
    return application


app = create_app()
