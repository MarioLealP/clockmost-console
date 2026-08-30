from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.schemas import AppLink
from app.services import apps as apps_svc

router = APIRouter(prefix="/api/apps", tags=["apps"])

SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.get("", response_model=list[AppLink])
async def list_apps(s: SettingsDep) -> list[AppLink]:
    return apps_svc.load(s.apps_file)
