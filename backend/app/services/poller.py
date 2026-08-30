import asyncio
import contextlib
import logging

from app.config import get_settings
from app.db import get_session
from app.services.snapshot import ingest, read_state_file

log = logging.getLogger("clockmost.poller")


async def _tick() -> None:
    settings = get_settings()
    snap = read_state_file(settings.state_file)
    async for session in get_session():
        added = await ingest(session, snap)
        if added:
            log.info("ingested snapshot ts=%s status=%s", snap.ts, snap.status)


async def run() -> None:
    """Background loop: ingest a snapshot row every `poll_seconds`."""
    interval = get_settings().poll_seconds
    while True:
        try:
            await _tick()
        except Exception:
            log.exception("poller tick failed")  # the loop must survive any one bad tick
        await asyncio.sleep(interval)


@contextlib.asynccontextmanager
async def lifespan_poller():  # type: ignore[no-untyped-def]
    task = asyncio.create_task(run(), name="clockmost-poller")
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
