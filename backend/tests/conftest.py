import json
from collections.abc import AsyncIterator
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


@pytest.fixture
async def client(
    tmp_path: Path, state_file: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[AsyncClient]:
    monkeypatch.setenv("CM_DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("CM_STATE_FILE", str(state_file))
    monkeypatch.setenv("CM_DIST_DIR", str(tmp_path / "no-dist"))
    monkeypatch.setenv("CM_POLL_SECONDS", "3600")  # keep the poller out of the way

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
