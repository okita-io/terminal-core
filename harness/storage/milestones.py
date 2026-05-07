from datetime import datetime, timezone
from pathlib import Path

from harness.storage.session import _atomic_write

MILESTONES = ["concept", "alpha", "beta", "preview", "release"]

_CRITERIA = {
    "concept": lambda s: s.get("design_doc") is not None,
    "alpha":   lambda s: s.get("current_game_path") is not None,
    "beta":    lambda s: s["blocking_resolved"],
    "preview": lambda s: s["blocking_resolved"] and s["major_resolved"],
    "release": lambda s: s["blocking_resolved"] and s["major_resolved"] and s["minor_resolved"],
}

_LABELS = {
    "concept": "Design document approved",
    "alpha":   "First playable render",
    "beta":    "All BLOCKING issues resolved",
    "preview": "All BLOCKING + MAJOR resolved",
    "release": "All BLOCKING + MAJOR + MINOR resolved",
}


def check_and_record(sessions_dir: str, state: dict) -> str | None:
    """Advance to the highest earned milestone and persist it. Returns new name or None."""
    reached = None
    for name in MILESTONES:
        if _CRITERIA[name](state):
            reached = name

    current = state.get("milestone")
    if not reached or reached == current:
        return None

    # Only advance, never downgrade
    if current and MILESTONES.index(reached) <= MILESTONES.index(current):
        return None

    state["milestone"] = reached
    path = Path(sessions_dir) / state["game_id"] / "milestones" / f"{reached}.json"
    _atomic_write(path, {
        "milestone": reached,
        "label": _LABELS[reached],
        "game_id": state["game_id"],
        "round": state["round"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "issues_at_milestone": state.get("issues_by_severity", {}),
    })
    return reached
