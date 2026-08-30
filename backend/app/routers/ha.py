from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.config import Settings, get_settings
from app.services import ha

router = APIRouter(prefix="/api/ha", tags=["ha"])

SettingsDep = Annotated[Settings, Depends(get_settings)]


def _require_ha(s: SettingsDep) -> Settings:
    if not s.ha_enabled:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Home Assistant not configured")
    return s


HADep = Annotated[Settings, Depends(_require_ha)]

EntityId = Annotated[str, Path(pattern=r"^[a-z_]+\.[a-z0-9_]+$")]


@router.get("/switches")
async def switches(s: HADep) -> list[dict[str, str]]:
    try:
        return await ha.list_switches(s)
    except ha.HAError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc


@router.post("/{entity_id}/toggle")
async def toggle(entity_id: EntityId, s: HADep) -> dict[str, str]:
    if not ha.is_toggleable(entity_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{entity_id} is not toggle-able")
    if s.ha_switches and entity_id not in s.ha_switches:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"{entity_id} is not on the dashboard")
    try:
        return {"entity_id": entity_id, "state": await ha.toggle(s, entity_id)}
    except ha.HAError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
