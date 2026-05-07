import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".tmp_{path.name}"
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def new_session(sessions_dir: str, title: str | None = None, constraint_envelope: dict | None = None) -> dict:
    game_id = str(uuid.uuid4())
    state = {
        "game_id": game_id,
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


def load_session(sessions_dir: str, game_id: str) -> dict:
    path = Path(sessions_dir) / game_id / "state.json"
    return json.loads(path.read_text())


def save_session(sessions_dir: str, state: dict):
    state["updated_at"] = _now()
    path = Path(sessions_dir) / state["game_id"] / "state.json"
    _atomic_write(path, state)


def list_sessions(sessions_dir: str) -> list[dict]:
    base = Path(sessions_dir)
    sessions = []
    for d in base.iterdir():
        if d.is_dir():
            f = d / "state.json"
            if f.exists():
                sessions.append(json.loads(f.read_text()))
    return sorted(sessions, key=lambda s: s["updated_at"], reverse=True)


def save_round(sessions_dir: str, game_id: str, round_n: int, data: dict):
    path = Path(sessions_dir) / game_id / "rounds" / f"{round_n:04d}.json"
    _atomic_write(path, data)


def load_round(sessions_dir: str, game_id: str, round_n: int) -> dict:
    path = Path(sessions_dir) / game_id / "rounds" / f"{round_n:04d}.json"
    return json.loads(path.read_text())


def save_design_review(sessions_dir: str, game_id: str, design_round: int, data: dict):
    path = Path(sessions_dir) / game_id / "design" / f"{design_round:04d}.json"
    _atomic_write(path, data)


def get_game_dir(sessions_dir: str, game_id: str) -> Path:
    return Path(sessions_dir) / game_id / "game"


def get_screenshots_dir(sessions_dir: str, game_id: str, round_n: int) -> Path:
    return Path(sessions_dir) / game_id / "rounds" / f"{round_n:04d}_screenshots"
