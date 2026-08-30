from httpx import AsyncClient


async def test_switches_disabled_without_config(client: AsyncClient) -> None:
    assert (await client.get("/api/ha/switches")).status_code == 503


async def test_switches_lists_only_the_configured_two(
    ha_client: AsyncClient, ha_stub: dict[str, int]
) -> None:
    body = (await ha_client.get("/api/ha/switches")).json()
    assert [s["entity_id"] for s in body] == ["switch.extraplug", "switch.shelf"]
    assert body[0]["name"] == "ExtraPlug"
    assert body[1]["state"] == "off"


async def test_toggle_calls_ha_and_returns_state(
    ha_client: AsyncClient, ha_stub: dict[str, int]
) -> None:
    r = await ha_client.post("/api/ha/switch.extraplug/toggle")
    assert r.status_code == 200
    assert r.json() == {"entity_id": "switch.extraplug", "state": "off"}
    assert ha_stub["toggle"] == 1


async def test_toggle_rejects_entities_off_the_dashboard(
    ha_client: AsyncClient, ha_stub: dict[str, int]
) -> None:
    assert (await ha_client.post("/api/ha/light.chandelure/toggle")).status_code == 403
    assert (await ha_client.post("/api/ha/sensor.temp/toggle")).status_code == 400
    assert ha_stub["toggle"] == 0
