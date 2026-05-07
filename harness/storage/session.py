import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_timestamp() -> str:
    return datetime.now().strftime("%y%m%d%H%M%S")


def _slugify_title(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")[:40]


def _atomic_write(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".tmp_{path.name}"
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def _make_session_dir_name(timestamp: str, title: str | None) -> str:
    if title:
        slug = _slugify_title(title)
        if slug:
            return f"{timestamp}_{slug}"
    return timestamp


def _find_session_dir(sessions_dir: str, game_id: str) -> str:
    """Return the directory name for a given game_id. Scans only when needed."""
    base = Path(sessions_dir)
    # Fast path: old UUID-based dirs
    if (base / game_id).is_dir():
        return game_id
    # Scan for YYMMDDHHMMSS* dirs
    for d in sorted(base.iterdir(), reverse=True):
        if d.is_dir():
            f = d / "state.json"
            if f.exists():
                try:
                    data = json.loads(f.read_text())
                    if data.get("game_id") == game_id:
                        return d.name
                except Exception:
                    continue
    return game_id  # fallback


def new_session(sessions_dir: str, title: str | None = None, constraint_envelope: dict | None = None) -> dict:
    game_id = str(uuid.uuid4())
    timestamp = _session_timestamp()
    session_dir = _make_session_dir_name(timestamp, title)

    state = {
        "game_id": game_id,
        "session_dir": session_dir,
        "timestamp": timestamp,
        "title": title,
        "concept": None,
        "design_doc": None,
        "design_round": 0,
        "stage": "INIT",
        "round": 0,
        "milestone": None,
        "constraint_envelope": constraint_envelope or {},
        "spec_id": None,
        "spec_version": 0,
        "spec_lineage": [],
        "retry_counts": {"DESIGN": 0, "BLOCKING": 0, "MAJOR": 0, "MINOR": 0},
        "issues_by_severity": {"BLOCKING": 0, "MAJOR": 0, "MINOR": 0},
        "fitness_scores": {},
        "fitness_history": [],
        "blocking_resolved": False,
        "major_resolved": False,
        "minor_resolved": False,
        "created_at": _now(),
        "updated_at": _now(),
        "current_game_path": None,
        "rounds_completed": [],
    }
    save_session(sessions_dir, state)
    return state


def _session_root(sessions_dir: str, state: dict) -> Path:
    """Resolve the session root directory."""
    session_dir = state.get("session_dir") or _find_session_dir(sessions_dir, state["game_id"])
    return Path(sessions_dir) / session_dir


def rename_session_dir(sessions_dir: str, state: dict) -> None:
    """Rename session dir to YYMMDDHHMMSS_title when title becomes available."""
    current_dir = state.get("session_dir") or state["game_id"]
    timestamp = state.get("timestamp") or current_dir[:12]
    title = state.get("title") or state.get("concept")
    if not title:
        return

    desired = _make_session_dir_name(timestamp, title)
    if desired == current_dir:
        return

    old_path = Path(sessions_dir) / current_dir
    new_path = Path(sessions_dir) / desired
    if old_path.exists() and not new_path.exists():
        old_path.rename(new_path)
        state["session_dir"] = desired
        if state.get("current_game_path"):
            state["current_game_path"] = state["current_game_path"].replace(
                str(old_path), str(new_path)
            )


def load_session(sessions_dir: str, game_id: str) -> dict:
    session_dir = _find_session_dir(sessions_dir, game_id)
    path = Path(sessions_dir) / session_dir / "state.json"
    return json.loads(path.read_text())


def save_session(sessions_dir: str, state: dict):
    state["updated_at"] = _now()
    path = _session_root(sessions_dir, state) / "state.json"
    _atomic_write(path, state)


def list_sessions(sessions_dir: str) -> list[dict]:
    base = Path(sessions_dir)
    sessions = []
    for d in base.iterdir():
        if d.is_dir():
            f = d / "state.json"
            if f.exists():
                try:
                    sessions.append(json.loads(f.read_text()))
                except Exception:
                    continue
    return sorted(sessions, key=lambda s: s["updated_at"], reverse=True)


def save_round(sessions_dir: str, game_id: str, round_n: int, data: dict):
    session_dir = _find_session_dir(sessions_dir, game_id)
    path = Path(sessions_dir) / session_dir / "rounds" / f"{round_n:04d}.json"
    _atomic_write(path, data)


def load_round(sessions_dir: str, game_id: str, round_n: int) -> dict:
    session_dir = _find_session_dir(sessions_dir, game_id)
    path = Path(sessions_dir) / session_dir / "rounds" / f"{round_n:04d}.json"
    return json.loads(path.read_text())


def save_design_review(sessions_dir: str, game_id: str, design_round: int, data: dict):
    session_dir = _find_session_dir(sessions_dir, game_id)
    path = Path(sessions_dir) / session_dir / "design" / f"{design_round:04d}.json"
    _atomic_write(path, data)


def get_game_dir(sessions_dir: str, game_id: str) -> Path:
    session_dir = _find_session_dir(sessions_dir, game_id)
    return Path(sessions_dir) / session_dir / "game"


def get_screenshots_dir(sessions_dir: str, game_id: str, round_n: int) -> Path:
    session_dir = _find_session_dir(sessions_dir, game_id)
    return Path(sessions_dir) / session_dir / "rounds" / f"{round_n:04d}_screenshots"
