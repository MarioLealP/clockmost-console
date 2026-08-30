from httpx import AsyncClient


async def test_prefs_roundtrip_per_user(client: AsyncClient) -> None:
    # unknown user starts empty
    r = await client.get("/api/prefs", headers={"X-Authentik-Username": "mario"})
    assert r.json() == {"username": "mario", "prefs": {}}

    # save
    r = await client.put(
        "/api/prefs",
        headers={"X-Authentik-Username": "mario"},
        json={"prefs": {"order": ["deploy", "alerts"], "collapsed": ["notify"]}},
    )
    assert r.json()["prefs"]["order"] == ["deploy", "alerts"]

    # persists, and is scoped to the user
    r = await client.get("/api/prefs", headers={"X-Authentik-Username": "mario"})
    assert r.json()["prefs"]["collapsed"] == ["notify"]
    r = await client.get("/api/prefs", headers={"X-Authentik-Username": "someone-else"})
    assert r.json()["prefs"] == {}


async def test_prefs_without_header_uses_local(client: AsyncClient) -> None:
    r = await client.get("/api/prefs")
    assert r.json()["username"] == "local"
