from typing import Any

from pydantic import BaseModel


class DeployInfo(BaseModel):
    commit: str = ""
    last: str = ""
    rollback_recent: int = 0


class Containers(BaseModel):
    up: int = 0
    total: int = 0
    down: list[str] = []
    unhealthy: list[str] = []


class Disk(BaseModel):
    root: int = 0
    home: int = 0


class PR(BaseModel):
    n: int
    t: str


class Alert(BaseModel):
    s: int
    n: str


class Note(BaseModel):
    t: int
    ti: str
    m: str
    p: int


class InfraSnapshot(BaseModel):
    """Mirrors `/usr/local/sbin/clockmost-status` output."""

    status: str = "unknown"
    ts: int = 0
    deploy: DeployInfo = DeployInfo()
    containers: Containers = Containers()
    units_failed: list[str] = []
    disk: Disk = Disk()
    updates: dict[str, Any] = {"n": 0, "list": []}
    alerts: dict[str, Any] = {"n": 0, "max_sev": 0, "list": []}
    notify: dict[str, Any] = {"n": 0, "list": []}


class HistoryPoint(BaseModel):
    ts: int
    status: str
    containers_up: int
    containers_total: int
    disk_root: int
    disk_home: int
    alerts_n: int
    alerts_max_sev: int


class InfraOut(BaseModel):
    """What GET /api/infra returns: the live snapshot + a recent history tail."""

    snapshot: InfraSnapshot
    stale: bool
    age_seconds: int
    history: list[HistoryPoint]


class AppLink(BaseModel):
    """A user-facing app for the launcher (GET /api/apps)."""

    name: str
    url: str
    group: str = "apps"
