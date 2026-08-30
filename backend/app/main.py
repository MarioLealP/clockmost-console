import contextlib
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db import dispose_engine
from app.routers import ha, health, infra, prefs
from app.services.poller import lifespan_poller

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # schema is applied out-of-band: the container entrypoint runs
    # `alembic upgrade head`; the test suite calls SQLModel.metadata.create_all.
    async with lifespan_poller():
        yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="clockmost-console", lifespan=lifespan, docs_url="/api/docs")

    app.include_router(health.router)
    app.include_router(infra.router)
    app.include_router(prefs.router)
    app.include_router(ha.router)

    index = settings.dist_dir / "index.html"
    if index.is_file():
        app.mount("/assets", StaticFiles(directory=settings.dist_dir / "assets"), name="assets")

        # everything the API didn't match is the SPA — except unknown /api/* paths,
        # which stay as JSON 404s
        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa(full_path: str) -> FileResponse:
            if full_path.startswith(("api/", "assets/")):
                raise HTTPException(status.HTTP_404_NOT_FOUND)
            return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return app


app = create_app()
