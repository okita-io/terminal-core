"""
Copies game HTML + screenshot into web/public/games/{slug}/{milestone}/
and updates web/public/games/index.json on each milestone.
"""

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from harness.storage.session import _atomic_write


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug or "untitled"


def publish_milestone(
    state: dict,
    sessions_dir: str,
    web_dir: str,
    milestone: str,
) -> None:
    title = state.get("title") or state.get("concept") or "Untitled"
    slug = slugify(title)
    game_id = state["game_id"]

    dest = Path(web_dir) / "public" / "games" / slug / milestone
    dest.mkdir(parents=True, exist_ok=True)

    # Copy game HTML
    src_html = state.get("current_game_path")
    if src_html and Path(src_html).exists():
        shutil.copy2(src_html, dest / "index.html")

    # Copy latest screenshot (most recent round)
    screenshot_dest = None
    if state.get("rounds_completed"):
        last_round = state["rounds_completed"][-1]
        shots_dir = Path(sessions_dir) / game_id / "rounds" / f"{last_round:04d}_screenshots"
        screenshots = sorted(shots_dir.glob("screenshot_*.png")) if shots_dir.exists() else []
        if screenshots:
            shutil.copy2(screenshots[0], dest / "screenshot.png")
            screenshot_dest = f"/games/{slug}/{milestone}/screenshot.png"

    _update_manifest(state, slug, milestone, screenshot_dest, web_dir)


def _update_manifest(
    state: dict,
    slug: str,
    milestone: str,
    screenshot: str | None,
    web_dir: str,
) -> None:
    manifest_path = Path(web_dir) / "public" / "games" / "index.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        manifest = json.loads(manifest_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        manifest = {"games": [], "updated_at": _now()}

    games = manifest.get("games", [])
    existing = next((g for g in games if g["slug"] == slug), None)

    fitness = state.get("fitness_scores", {})
    title = state.get("title") or state.get("concept") or "Untitled"
    gdd = state.get("design_doc") or {}
    description = (
        (gdd.get("metadata") or {}).get("description")
        or (gdd.get("metadata") or {}).get("short_description")
        or ""
    )
    genre = (
        state.get("constraint_envelope", {}).get("genre")
        or (gdd.get("metadata") or {}).get("genre")
        or "experimental"
    )

    milestones_order = ["concept", "alpha", "beta", "preview", "release"]

    if existing:
        if milestone not in existing.get("milestones", []):
            existing["milestones"].append(milestone)
            existing["milestones"].sort(key=lambda m: milestones_order.index(m) if m in milestones_order else 99)
        existing["milestone"] = milestone
        if screenshot:
            existing["screenshot"] = screenshot
        existing["fitness"] = fitness
        existing["updated_at"] = _now()
        if description:
            existing["description"] = description
    else:
        entry = {
            "slug": slug,
            "title": title,
            "description": description,
            "genre": genre,
            "milestone": milestone,
            "milestones": [milestone],
            "fitness": fitness,
            "game_id": state["game_id"],
            "session_dir": state.get("session_dir", ""),
            "screenshot": screenshot,
            "tags": _extract_tags(state),
            "created_at": state.get("created_at", _now()),
            "updated_at": _now(),
        }
        games.append(entry)

    manifest["games"] = games
    manifest["updated_at"] = _now()
    _atomic_write(manifest_path, manifest)


def _extract_tags(state: dict) -> list[str]:
    tags = []
    gdd = state.get("design_doc") or {}
    envelope = state.get("constraint_envelope") or {}

    genre = envelope.get("genre") or (gdd.get("metadata") or {}).get("genre")
    if genre:
        tags.append(genre)

    input_model = envelope.get("input_model") or (gdd.get("design") or {}).get("input_model")
    if input_model:
        tags.append(input_model)

    tags.append("ai_generated")
    return list(dict.fromkeys(tags))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
