from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routes_admin import router as admin_router
from app.routes_public import router as public_router


def create_app(seed_database: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        init_db(seed_database=seed_database)
        yield

    app = FastAPI(title="Tanning Salon API", lifespan=lifespan)

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}
    #
    app.include_router(public_router)
    app.include_router(admin_router)
    return app


app = create_app()
