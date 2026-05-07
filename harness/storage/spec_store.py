"""Versioned AGX-1 spec persistence and lineage tracking."""

import uuid
from datetime import datetime, timezone
from pathlib import Path

from harness.storage.session import _atomic_write


def save_spec(sessions_dir: str, game_id: str, spec: dict, parent_spec_id: str | None = None) -> str:
    """
    Persist a spec, assign a spec_id, attach version metadata.
    Returns the new spec_id.
    """
    spec_id = str(uuid.uuid4())
    versioned = {
        **spec,
        "spec_id": spec_id,
        "parent_spec_id": parent_spec_id,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    path = Path(sessions_dir) / game_id / "specs" / f"{spec_id}.json"
    _atomic_write(path, versioned)
    return spec_id


def load_spec(sessions_dir: str, game_id: str, spec_id: str) -> dict:
    import json
    path = Path(sessions_dir) / game_id / "specs" / f"{spec_id}.json"
    return json.loads(path.read_text())


def list_specs(sessions_dir: str, game_id: str) -> list[dict]:
    """Return all specs ordered by saved_at ascending."""
    import json
    specs_dir = Path(sessions_dir) / game_id / "specs"
    if not specs_dir.exists():
        return []
    specs = []
    for f in specs_dir.glob("*.json"):
        try:
            specs.append(json.loads(f.read_text()))
        except Exception:
            pass
    return sorted(specs, key=lambda s: s.get("saved_at", ""))


def get_lineage(sessions_dir: str, game_id: str, spec_id: str) -> list[str]:
    """Walk parent_spec_id pointers back to root. Returns [root, ..., spec_id]."""
    all_specs = {s["spec_id"]: s for s in list_specs(sessions_dir, game_id)}
    lineage = []
    cur = spec_id
    visited = set()
    while cur and cur not in visited:
        visited.add(cur)
        lineage.append(cur)
        parent = all_specs.get(cur, {}).get("parent_spec_id")
        cur = parent
    lineage.reverse()
    return lineage
