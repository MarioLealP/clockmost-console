from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CM_", env_file=".env", extra="ignore")

    # where the React build lands; the API serves it as the SPA
    dist_dir: Path = Path("dist")

    # the host timer drops the infra snapshot here (bind-mounted read-only)
    state_file: Path = Path("/data/state.json")

    # sqlite by default; point at postgres via CM_DATABASE_URL to scale out
    database_url: str = "sqlite+aiosqlite:////data/console.db"

    # how often the poller ingests a snapshot row
    poll_seconds: float = 20.0

    # Home Assistant (phase 2) — empty disables the HA routes
    ha_url: str = ""
    ha_token: str = Field(default="", repr=False)

    cors_origins: list[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()
