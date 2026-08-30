import httpx

from app.config import Settings

TOGGLE_DOMAINS = ("switch", "light", "input_boolean", "fan")

# device-config sub-entities we never want as "switches" on the dashboard
_NOISE = ("_child_lock", "_led_enable", "_led", "_display", "permit_join", "_beeper")


class HAError(RuntimeError):
    pass


def _client(s: Settings) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=s.ha_url.rstrip("/"),
        headers={"Authorization": f"Bearer {s.ha_token}"},
        timeout=8.0,
    )


def _domain(entity_id: str) -> str:
    return entity_id.split(".", 1)[0]


def is_toggleable(entity_id: str) -> bool:
    return _domain(entity_id) in TOGGLE_DOMAINS


async def list_switches(s: Settings) -> list[dict[str, str]]:
    """Toggle-able entities. Honours `ha_switches` (exact list, in order) if set,
    otherwise every switch/light minus the config noise."""
    async with _client(s) as c:
        r = await c.get("/api/states")
    if r.status_code != httpx.codes.OK:
        raise HAError(f"HA /api/states → {r.status_code}")
    by_id = {e["entity_id"]: e for e in r.json()}

    if s.ha_switches:
        wanted = [by_id[eid] for eid in s.ha_switches if eid in by_id]
    else:
        wanted = [
            e
            for eid, e in by_id.items()
            if _domain(eid) in ("switch", "light") and not any(n in eid for n in _NOISE)
        ]

    return [
        {
            "entity_id": e["entity_id"],
            "name": e["attributes"].get("friendly_name") or e["entity_id"],
            "state": e["state"],
            "domain": _domain(e["entity_id"]),
        }
        for e in wanted
    ]


async def toggle(s: Settings, entity_id: str) -> str:
    """Flip an entity; return its resulting state."""
    domain = _domain(entity_id)
    async with _client(s) as c:
        r = await c.post(
            f"/api/services/{domain}/toggle",
            json={"entity_id": entity_id},
        )
        if r.status_code != httpx.codes.OK:
            raise HAError(f"HA toggle {entity_id} → {r.status_code}")
        st = await c.get(f"/api/states/{entity_id}")
    return str(st.json().get("state", "unknown")) if st.status_code == httpx.codes.OK else "unknown"
