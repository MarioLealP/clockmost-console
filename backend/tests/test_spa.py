from httpx import AsyncClient


async def test_serves_the_spa_and_falls_back_on_client_routes(spa_client: AsyncClient) -> None:
    assert (await spa_client.get("/")).text.startswith("<!doctype html>")
    deep = await spa_client.get("/settings/whatever")
    assert deep.status_code == 200
    assert "<title>console</title>" in deep.text


async def test_api_routes_still_win_and_unknown_api_is_json_404(spa_client: AsyncClient) -> None:
    assert (await spa_client.get("/api/health")).json() == {"ok": True}

    r = await spa_client.get("/api/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")


async def test_api_client_errors_are_not_masked_by_the_spa_fallback(
    spa_client: AsyncClient,
) -> None:
    # HA is unconfigured on this client → 503, not a 200 index.html and not a 500
    assert (await spa_client.get("/api/ha/switches")).status_code == 503


async def test_built_assets_are_served(spa_client: AsyncClient) -> None:
    assert (await spa_client.get("/assets/app.js")).status_code == 200
