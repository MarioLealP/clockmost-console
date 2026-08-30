import contextlib
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.db import dispose_engine
from app.routers import health, infra, prefs
from app.services.poller import lifespan_poller

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # schema is applied out-of-band: the container entrypoint / `just dev` runs
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

    dist = settings.dist_dir
    index = dist / "index.html"
    if index.is_file():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.exception_handler(StarletteHTTPException)
        async def spa_fallback(request, exc):  # type: ignore[no-untyped-def]
            if exc.status_code == status.HTTP_404_NOT_FOUND and not request.url.path.startswith(
                "/api"
            ):
                return FileResponse(index, headers={"Cache-Control": "no-cache"})
            raise exc

        @app.get("/", include_in_schema=False)
        async def root() -> FileResponse:
            return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return app


app = create_app()
