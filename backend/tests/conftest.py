import json
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel

SAMPLE = {
    "status": "warn",
    "ts": 1_788_000_000,
    "deploy": {
        "commit": "abc1234 feat: thing",
        "last": "OK — deployed caddy",
        "rollback_recent": 0,
    },
    "containers": {"up": 31, "total": 32, "down": ["factorio"], "unhealthy": []},
    "units_failed": [],
    "disk": {"root": 17, "home": 24},
    "updates": {"n": 2, "list": [{"n": 7, "t": "bump caddy"}]},
    "alerts": {"n": 1, "max_sev": 3, "list": [{"s": 3, "n": "TLS expiring"}]},
    "notify": {"n": 1, "list": [{"t": 1_788_000_000, "ti": "clockmost", "m": "backup ok", "p": 3}]},
}


@pytest.fixture
def state_file(tmp_path: Path) -> Path:
    p = tmp_path / "state.json"
    p.write_text(json.dumps(SAMPLE))
    return p


async def _build_client(
    tmp_path: Path, state_file: Path, monkeypatch: pytest.MonkeyPatch, env: dict[str, str]
) -> AsyncIterator[AsyncClient]:
    monkeypatch.setenv("CM_DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("CM_STATE_FILE", str(state_file))
    monkeypatch.setenv("CM_DIST_DIR", str(tmp_path / "no-dist"))
    monkeypatch.setenv("CM_POLL_SECONDS", "3600")  # keep the poller out of the way
    for k, v in env.items():
        monkeypatch.setenv(k, v)

    from app import config, db

    config.get_settings.cache_clear()
    await db.dispose_engine()

    from app.main import create_app

    app = create_app()
    async with db.engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await db.dispose_engine()


@pytest.fixture
async def client(
    tmp_path: Path, state_file: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[AsyncClient]:
    async for c in _build_client(tmp_path, state_file, monkeypatch, {}):
        yield c


@pytest.fixture
async def spa_client(
    tmp_path: Path, state_file: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[AsyncClient]:
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>console</title>")
    (dist / "assets" / "app.js").write_text("// built")
    async for c in _build_client(tmp_path, state_file, monkeypatch, {"CM_DIST_DIR": str(dist)}):
        yield c


@pytest.fixture
async def ha_client(
    tmp_path: Path, state_file: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[AsyncClient]:
    env = {
        "CM_HA_URL": "http://ha.test",
        "CM_HA_TOKEN": "test-token",
        "CM_HA_SWITCHES": "switch.extraplug,switch.shelf",
    }
    async for c in _build_client(tmp_path, state_file, monkeypatch, env):
        yield c


@pytest.fixture
def ha_stub(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, int]]:
    """Fake the Home Assistant REST API. `calls` counts toggle POSTs."""
    import httpx

    from app.services import ha

    states = [
        {
            "entity_id": "switch.extraplug",
            "state": "on",
            "attributes": {"friendly_name": "ExtraPlug"},
        },
        {"entity_id": "switch.shelf", "state": "off", "attributes": {"friendly_name": "Shelf"}},
        {
            "entity_id": "switch.shelf_child_lock",
            "state": "off",
            "attributes": {"friendly_name": "Shelf Child lock"},
        },
        {
            "entity_id": "light.chandelure",
            "state": "on",
            "attributes": {"friendly_name": "Chandelure"},
        },
        {"entity_id": "sensor.temp", "state": "21", "attributes": {}},
    ]
    calls = {"toggle": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/states":
            return httpx.Response(200, json=states)
        if path.startswith("/api/services/") and path.endswith("/toggle"):
            calls["toggle"] += 1
            return httpx.Response(200, json=[])
        if path.startswith("/api/states/"):
            eid = path.removeprefix("/api/states/")
            return httpx.Response(200, json={"entity_id": eid, "state": "off"})
        return httpx.Response(404)

    def fake_client(_s: object) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url="http://ha.test", transport=httpx.MockTransport(handler))

    monkeypatch.setattr(ha, "_client", fake_client)
    yield calls
