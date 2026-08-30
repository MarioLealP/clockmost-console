from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

CsvList = Annotated[list[str], NoDecode]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CM_", env_file=".env", extra="ignore")

    # where the React build lands; the API serves it as the SPA
    dist_dir: Path = Path("dist")

    # the host timer drops the infra snapshot here (bind-mounted read-only)
    state_file: Path = Path("/data/state.json")

    # launcher list override — falls back to app/apps.default.json when absent
    apps_file: Path = Path("/data/apps.json")

    # sqlite by default; point at postgres via CM_DATABASE_URL to scale out
    database_url: str = "sqlite+aiosqlite:////data/console.db"

    # how often the poller ingests a snapshot row
    poll_seconds: float = 20.0

    # Home Assistant — empty `ha_url`/`ha_token` disables the HA routes
    ha_url: str = ""
    ha_token: str = Field(default="", repr=False)
    # entity_ids to surface as toggles, in order. Empty = auto (switch.*/light.*
    # minus the obvious device-config sub-entities). Comma-separated in the env.
    ha_switches: CsvList = []

    cors_origins: CsvList = []

    @field_validator("ha_switches", "cors_origins", mode="before")
    @classmethod
    def _split_csv(cls, v: object) -> object:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @property
    def ha_enabled(self) -> bool:
        return bool(self.ha_url and self.ha_token)


@lru_cache
def get_settings() -> Settings:
    return Settings()
