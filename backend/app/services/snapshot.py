import json
import time
from pathlib import Path

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Snapshot
from app.schemas import HistoryPoint, InfraSnapshot

STALE_SECONDS = 75


def read_state_file(path: Path) -> InfraSnapshot:
    """Parse the host snapshot. Never raises — a missing/broken file is `unknown`."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return InfraSnapshot()
    try:
        return InfraSnapshot.model_validate(data)
    except ValueError:
        return InfraSnapshot()


def _row_from(snap: InfraSnapshot) -> Snapshot:
    return Snapshot(
        source_ts=snap.ts,
        status=snap.status,
        containers_up=snap.containers.up,
        containers_total=snap.containers.total,
        containers_down=len(snap.containers.down),
        containers_unhealthy=len(snap.containers.unhealthy),
        units_failed=len(snap.units_failed),
        disk_root=snap.disk.root,
        disk_home=snap.disk.home,
        updates_n=int(snap.updates.get("n", 0)),
        alerts_n=int(snap.alerts.get("n", 0)),
        alerts_max_sev=int(snap.alerts.get("max_sev", 0)),
        raw=snap.model_dump(),
    )


async def ingest(session: AsyncSession, snap: InfraSnapshot) -> bool:
    """Persist a snapshot row if its `ts` is new. Returns True if a row was added."""
    if snap.ts <= 0:
        return False
    exists = await session.scalar(select(Snapshot.id).where(Snapshot.source_ts == snap.ts))
    if exists is not None:
        return False
    session.add(_row_from(snap))
    await session.commit()
    return True


async def history(session: AsyncSession, hours: int, limit: int = 720) -> list[HistoryPoint]:
    since = int(time.time()) - hours * 3600
    rows = (
        await session.exec(
            select(Snapshot)
            .where(Snapshot.source_ts >= since)
            .order_by(Snapshot.source_ts)  # type: ignore[arg-type]
            .limit(limit)
        )
    ).all()
    return [
        HistoryPoint(
            ts=r.source_ts,
            status=r.status,
            containers_up=r.containers_up,
            containers_total=r.containers_total,
            disk_root=r.disk_root,
            disk_home=r.disk_home,
            alerts_n=r.alerts_n,
            alerts_max_sev=r.alerts_max_sev,
        )
        for r in rows
    ]


def age_seconds(snap: InfraSnapshot) -> int:
    return max(0, int(time.time()) - snap.ts) if snap.ts > 0 else 10**9
