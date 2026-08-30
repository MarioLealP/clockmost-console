from pathlib import Path

import pytest
from httpx import AsyncClient


async def test_apps_returns_the_baked_default_list(client: AsyncClient) -> None:
    apps = (await client.get("/api/apps")).json()
    names = {a["name"] for a in apps}
    assert "Immich" in names
    assert "twitch-mario" in names
    assert {a["group"] for a in apps} == {"apps", "streams", "ops"}
    # order is preserved from the file
    assert apps[0]["name"] == "Immich"


async def test_apps_override_file_wins(
    client: AsyncClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    override = tmp_path / "apps.json"
    override.write_text('{"apps": [{"name": "Only This", "url": "https://x"}]}')
    monkeypatch.setenv("CM_APPS_FILE", str(override))

    from app import config

    config.get_settings.cache_clear()
    apps = (await client.get("/api/apps")).json()
    assert apps == [{"name": "Only This", "url": "https://x", "group": "apps"}]
