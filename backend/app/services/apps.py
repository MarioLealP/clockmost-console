import json
from pathlib import Path

from app.schemas import AppLink

DEFAULT_FILE = Path(__file__).resolve().parent.parent / "apps.default.json"


def load(override: Path) -> list[AppLink]:
    """The launcher list. Uses `override` (bind-mounted `/data/apps.json`) if it
    exists, else the baked-in default. Never raises."""
    src = override if override.is_file() else DEFAULT_FILE
    try:
        data = json.loads(src.read_text())
        return [AppLink.model_validate(a) for a in data.get("apps", [])]
    except (OSError, ValueError):
        return []
