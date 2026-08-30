from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.config import get_settings
from app.db import SessionDep
from app.schemas import HistoryPoint, InfraOut
from app.services import snapshot

router = APIRouter(prefix="/api/infra", tags=["infra"])


@router.get("", response_model=InfraOut)
async def get_infra(session: SessionDep, response: Response) -> InfraOut:
    response.headers["Cache-Control"] = "no-store"
    snap = snapshot.read_state_file(get_settings().state_file)
    await snapshot.ingest(session, snap)
    age = snapshot.age_seconds(snap)
    return InfraOut(
        snapshot=snap,
        stale=age > snapshot.STALE_SECONDS,
        age_seconds=age,
        history=await snapshot.history(session, hours=6, limit=120),
    )


@router.get("/history", response_model=list[HistoryPoint])
async def get_history(
    session: SessionDep,
    hours: Annotated[int, Query(ge=1, le=168)] = 24,
) -> list[HistoryPoint]:
    return await snapshot.history(session, hours=hours)
