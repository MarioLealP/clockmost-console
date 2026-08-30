from pathlib import Path

from httpx import AsyncClient


async def test_infra_relays_the_snapshot(client: AsyncClient) -> None:
    r = await client.get("/api/infra")
    assert r.status_code == 200
    body = r.json()

    assert body["snapshot"]["status"] == "warn"
    assert body["snapshot"]["containers"]["down"] == ["factorio"]
    assert body["stale"] is True  # the sample ts is fixed in the past
    assert r.headers["cache-control"] == "no-store"


async def test_infra_persists_history_once(client: AsyncClient) -> None:
    await client.get("/api/infra")
    await client.get("/api/infra")  # same ts — must not double-insert

    hist = (await client.get("/api/infra/history?hours=168")).json()
    assert len(hist) == 1
    assert hist[0]["containers_up"] == 31
    assert hist[0]["alerts_max_sev"] == 3


async def test_infra_unknown_when_file_missing(client: AsyncClient, state_file: Path) -> None:
    state_file.unlink()
    body = (await client.get("/api/infra")).json()
    assert body["snapshot"]["status"] == "unknown"
    assert body["stale"] is True
