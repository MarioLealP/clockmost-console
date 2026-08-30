from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel

JsonDict = dict[str, Any]


def _now() -> datetime:
    return datetime.now(UTC)


class Snapshot(SQLModel, table=True):
    """One ingest of `clockmost-status`. Flat columns for cheap history queries;
    the untouched payload is kept in `raw` for anything the UI wants later."""

    __tablename__ = "snapshot"

    id: int | None = Field(default=None, primary_key=True)
    # `ts` from the snapshot itself — unique so the poller is idempotent
    source_ts: int = Field(index=True, unique=True)
    ingested_at: datetime = Field(default_factory=_now)

    status: str = Field(index=True)
    containers_up: int = 0
    containers_total: int = 0
    containers_down: int = 0
    containers_unhealthy: int = 0
    units_failed: int = 0
    disk_root: int = 0
    disk_home: int = 0
    updates_n: int = 0
    alerts_n: int = 0
    alerts_max_sev: int = 0

    raw: JsonDict = Field(default_factory=dict, sa_column=Column(JSON))


class UserPref(SQLModel, table=True):
    """Per-Authentik-user UI state (panel order, collapsed sections, favourites)."""

    __tablename__ = "user_pref"

    username: str = Field(primary_key=True)
    prefs: JsonDict = Field(default_factory=dict, sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=_now)
