"""
AGX-1 Game Spec Schema — canonical contract for the arcade engine.

All agents that produce or consume a game spec reference this module.
Validation is tolerant: failures are returned as issue lists, not exceptions,
so the design iteration loop can correct them via REVISE rather than crashing.
"""

from __future__ import annotations

# ── Enum values ─────────────────────────────────────────────────────────────

GENRES = {"micro_arcade", "puzzle", "platformer", "rhythm", "tactics", "survival", "experimental"}
INPUT_MODELS = {"one_button", "two_button", "keyboard_arrows", "mouse_only", "touch_swipe", "hybrid"}
INTENDED_PLAYERS = {"human_only", "ai_only", "human_vs_ai", "co_play"}
WIN_CONDITION_TYPES = {"score_threshold", "survive_duration", "reach_goal", "defeat_enemy", "puzzle_solved"}
LOSE_CONDITION_TYPES = {"hit_obstacle", "timer_expired", "resource_depleted", "enemy_collision"}
COLLISION_MODELS = {"aabb", "circle", "pixel"}
SCALING_CURVES = {"linear", "exponential", "step", "none"}
INTERACTION_TYPES = {"collision", "proximity", "input_trigger", "timed"}
NPC_BEHAVIORS = {"static", "patrol", "chase", "flee", "random"}
AI_PROFILES = {"dumb", "average", "optimal", "chaotic"}
OBJECT_TYPES = {"obstacle", "collectible", "projectile", "trigger"}
LAYOUT_TYPES = {"grid", "freeform", "procedural"}
SCROLLING = {"none", "vertical", "horizontal"}
DIFFICULTY_LEVELS = {"easy", "normal", "hard", "extreme"}
ADJUST_ON = {"player_score", "survival_time", "error_rate"}
DIFFICULTY_CURVES = {"linear", "sigmoid", "staircase"}
PLAYER_ABILITIES = {"move", "jump", "dash", "shoot", "interact"}
PHASER_PHYSICS = {"arcade", "matter", "none"}
FITNESS_FUNCTIONS = {"human_engagement", "ai_win_rate", "difficulty_balance", "novelty"}
MUTATION_POINTS = {
    "spawn_rate", "enemy_speed", "layout", "scoring", "win_condition",
    "gravity", "friction", "timer_length", "hitbox_size", "npc_behavior",
}

# ── Required field paths ─────────────────────────────────────────────────────

_REQUIRED = [
    "game_id",
    "version",
    "metadata.title",
    "metadata.genre",
    "metadata.session_length_seconds",
    "metadata.input_model",
    "metadata.intended_players",
    "design.core_loop.summary",
    "design.core_loop.steps",
    "design.win_condition.type",
    "design.lose_condition.type",
    "mechanics.physics.gravity",
    "mechanics.physics.collision_model",
    "entities.player",
    "levels",
    "difficulty.base_difficulty",
    "aesthetics.color_palette",
    "aesthetics.theme",
    "implementation.engine",
    "evolution.mutation_points",
    "evolution.fitness_functions",
]

# ── Validation ───────────────────────────────────────────────────────────────

def _get_path(obj: dict, path: str):
    parts = path.split(".")
    cur = obj
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def validate(spec: dict) -> tuple[bool, list[str]]:
    """
    Validate a spec dict against AGX-1 schema.
    Returns (is_valid, list_of_error_strings).
    Errors are suitable for injecting as MAJOR issues into the design review.
    """
    errors: list[str] = []

    for path in _REQUIRED:
        val = _get_path(spec, path)
        if val is None:
            errors.append(f"Missing required field: {path}")
        elif val == [] or val == "":
            errors.append(f"Empty required field: {path}")

    # Enum checks
    _check_enum(spec, "metadata.genre", GENRES, errors)
    _check_enum(spec, "metadata.input_model", INPUT_MODELS, errors)
    _check_enum(spec, "metadata.intended_players", INTENDED_PLAYERS, errors)
    _check_enum(spec, "design.win_condition.type", WIN_CONDITION_TYPES, errors)
    _check_enum(spec, "design.lose_condition.type", LOSE_CONDITION_TYPES, errors)
    _check_enum(spec, "mechanics.physics.collision_model", COLLISION_MODELS, errors)
    _check_enum(spec, "difficulty.base_difficulty", DIFFICULTY_LEVELS, errors)

    # Palette check
    palette = _get_path(spec, "aesthetics.color_palette")
    if isinstance(palette, list) and len(palette) < 3:
        errors.append("aesthetics.color_palette must have at least 3 colors")

    # Levels check
    levels = _get_path(spec, "levels")
    if isinstance(levels, list) and len(levels) == 0:
        errors.append("levels must contain at least one level definition")

    # Session length sanity
    sl = _get_path(spec, "metadata.session_length_seconds")
    if sl is not None and isinstance(sl, (int, float)) and (sl < 10 or sl > 600):
        errors.append(f"metadata.session_length_seconds={sl} is outside 10–600 range")

    return len(errors) == 0, errors


def _check_enum(spec: dict, path: str, valid: set, errors: list):
    val = _get_path(spec, path)
    if val is not None and val not in valid:
        errors.append(f"{path}='{val}' is not a valid value (expected one of: {sorted(valid)})")


# ── Minimal spec template ────────────────────────────────────────────────────

def empty_spec(game_id: str, envelope: dict | None = None) -> dict:
    """Return a minimal valid spec skeleton seeded from the constraint envelope."""
    env = envelope or {}
    return {
        "game_id": game_id,
        "version": "0.1.0",
        "parent_spec_id": None,
        "metadata": {
            "title": "",
            "description": "",
            "genre": env.get("genre", "experimental"),
            "session_length_seconds": env.get("session_length_seconds", 60),
            "input_model": env.get("input_model", "keyboard_arrows"),
            "intended_players": env.get("intended_players", "human_vs_ai"),
            "constraints": {
                "max_entities": 50,
                "max_level_size": 800,
                "performance_budget_ms": env.get("performance_budget_ms", 16),
            },
        },
        "design": {
            "core_loop": {"summary": "", "steps": []},
            "win_condition": {"type": "score_threshold", "parameters": {}},
            "lose_condition": {"type": "hit_obstacle", "parameters": {}},
            "scoring": {"score_events": []},
        },
        "mechanics": {
            "physics": {"gravity": 300.0, "friction": 0.0, "max_speed": 400.0, "collision_model": "aabb"},
            "timers": {"tick_rate_hz": 60, "global_timer_seconds": env.get("session_length_seconds", 60)},
            "spawning": {"spawn_rules": []},
            "interactions": [],
        },
        "entities": {
            "player": {"hitbox": {"w": 32, "h": 32}, "speed": 200.0, "abilities": ["move"], "health": 3},
            "npcs": [],
            "objects": [],
        },
        "levels": [
            {
                "level_id": "level_01",
                "layout_type": "freeform",
                "dimensions": {"width": 800, "height": 600},
                "initial_entities": [],
                "environmental_rules": {"scrolling": "none", "hazards": []},
            }
        ],
        "difficulty": {
            "base_difficulty": env.get("difficulty_target", "normal"),
            "scaling_rules": {
                "spawn_rate_multiplier": 1.0,
                "enemy_speed_multiplier": 1.0,
                "score_threshold_multiplier": 1.0,
            },
            "adaptive_rules": {"enabled": False, "adjust_on": "player_score", "adjustments": []},
        },
        "aesthetics": {
            "theme": "",
            "color_palette": [],
            "camera": {"zoom": 1.0, "follow_player": False},
        },
        "implementation": {
            "engine": "phaser_js",
            "render_scale": 1.0,
            "code_generation": {"language": "javascript", "modules": ["physics", "input", "rendering"]},
        },
        "telemetry_contract": {
            "events": [],
            "session_metrics": ["time_alive", "score", "inputs_per_second", "retries"],
            "ai_metrics": ["reaction_time"],
        },
        "evolution": {
            "mutation_points": list(MUTATION_POINTS)[:5],
            "mutation_rules": {"rate": 0.1, "bounds": {}},
            "fitness_functions": ["human_engagement", "novelty", "difficulty_balance"],
        },
    }
