from datetime import UTC, datetime

from fastapi import APIRouter

from app.db import SessionDep
from app.deps import CurrentUser
from app.models import UserPref
from app.schemas import PrefsIn, PrefsOut

router = APIRouter(prefix="/api/prefs", tags=["prefs"])


@router.get("", response_model=PrefsOut)
async def get_prefs(user: CurrentUser, session: SessionDep) -> PrefsOut:
    row = await session.get(UserPref, user)
    return PrefsOut(username=user, prefs=row.prefs if row else {})


@router.put("", response_model=PrefsOut)
async def put_prefs(body: PrefsIn, user: CurrentUser, session: SessionDep) -> PrefsOut:
    row = await session.get(UserPref, user)
    if row is None:
        row = UserPref(username=user, prefs=body.prefs)
    else:
        row.prefs = body.prefs
        row.updated_at = datetime.now(UTC)
    session.add(row)
    await session.commit()
    return PrefsOut(username=user, prefs=row.prefs)
