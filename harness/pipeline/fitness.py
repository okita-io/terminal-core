"""
AGX-1 Fitness Function Suite.

Scores are heuristically approximated from adversarial report data since
live telemetry is not yet available. Each sub-function documents the
telemetry formula it approximates so replacements can be dropped in later.

All scores are normalized 0.0–1.0:
  0.0 = catastrophic failure
  0.5 = neutral / baseline
  1.0 = excellent / evolutionary advantage

Composite thresholds (from design_phases.md):
  > 0.75 → accept (APPROVE path)
  0.50–0.75 → mutate again
  < 0.50 → revert (REWRITE path)
"""

from __future__ import annotations

# Weights from AGX spec (must sum to 1.0)
WEIGHTS: dict[str, float] = {
    "fun":          0.30,
    "novelty":      0.20,
    "balance":      0.15,
    "difficulty":   0.15,
    "exploit_free": 0.10,
    "performance":  0.05,
    "ux_clarity":   0.05,
}

ACCEPT_THRESHOLD = 0.75
MUTATE_THRESHOLD = 0.50


# ── Individual scores ────────────────────────────────────────────────────────

def _fun(report: dict, state: dict) -> float:
    """
    Approximates: F_fun = w1*R + w2*S + w3*C + w4*P
    Without telemetry, proxied by inverse issue density + approval signals.
    """
    issues = report.get("issues", [])
    if not issues:
        return 0.85
    blocking = sum(1 for i in issues if i.get("severity") == "BLOCKING")
    major    = sum(1 for i in issues if i.get("severity") == "MAJOR")
    minor    = sum(1 for i in issues if i.get("severity") == "MINOR")
    # Each blocking tanks fun severely; each major moderately
    penalty = (blocking * 0.30) + (major * 0.12) + (minor * 0.04)
    return max(0.0, min(1.0, 0.85 - penalty))


def _novelty(report: dict, state: dict, envelope: dict) -> float:
    """
    Approximates: F_nov = 1 - similarity(G_new, G_archive)
    Proxied by: novelty_target from envelope, penalized by design review novelty issues.
    """
    base = envelope.get("novelty_target", 0.7)
    issues = report.get("issues", [])
    novelty_hits = sum(
        1 for i in issues
        if any(kw in i.get("description", "").lower() for kw in ("clone", "familiar", "generic", "copy", "similar"))
    )
    return max(0.0, min(1.0, base - (novelty_hits * 0.20)))


def _balance(report: dict, state: dict) -> float:
    """
    Approximates: F_bal = 1 - |W_human - W_ai|
    Proxied by absence of exploit/balance issues in adversarial report.
    """
    issues = report.get("issues", [])
    balance_hits = sum(
        1 for i in issues
        if any(kw in i.get("description", "").lower() for kw in ("exploit", "cheat", "trivial", "infinite", "unbeatable"))
    )
    return max(0.0, min(1.0, 1.0 - (balance_hits * 0.25)))


def _difficulty(report: dict, state: dict, envelope: dict) -> float:
    """
    Approximates: F_diff = 1 - |D_actual - D_target| / D_target
    Proxied by: difficulty signals in issues vs target difficulty.
    """
    target_map = {"easy": 0.25, "normal": 0.50, "hard": 0.75, "extreme": 0.95}
    target = target_map.get(envelope.get("difficulty_target", "normal"), 0.50)

    issues = report.get("issues", [])
    too_hard = sum(1 for i in issues if any(kw in i.get("description", "").lower() for kw in ("too hard", "impossible", "unfair")))
    too_easy = sum(1 for i in issues if any(kw in i.get("description", "").lower() for kw in ("too easy", "trivial", "boring")))

    # Infer actual difficulty signal from BLOCKING + issue count
    blocking = sum(1 for i in issues if i.get("severity") == "BLOCKING")
    inferred = 0.5 + (too_hard * 0.15) - (too_easy * 0.15) + (blocking * 0.10)
    inferred = max(0.0, min(1.0, inferred))

    return max(0.0, 1.0 - abs(inferred - target))


def _exploit_free(report: dict) -> float:
    """
    Approximates: F_exp = 1 - E/E_max
    E_max assumed to be 4 exploit categories.
    """
    issues = report.get("issues", [])
    exploits = sum(
        1 for i in issues
        if any(kw in i.get("description", "").lower() for kw in ("exploit", "loop", "infinite", "skip", "bypass"))
    )
    return max(0.0, 1.0 - (exploits / 4.0))


def _performance(report: dict, state: dict) -> float:
    """
    Approximates: F_perf = FPS_avg / FPS_target (capped at 1.0)
    Proxied by console error count from Playwright render.
    """
    # Find console errors from the most recent round
    console_errors = []
    game_id = state.get("game_id", "")
    if state.get("rounds_completed"):
        # Errors stored in round data — approximate from report if not available
        console_errors = report.get("_console_errors", [])

    error_count = len(console_errors)
    return max(0.0, 1.0 - (error_count * 0.15))


def _ux_clarity(report: dict) -> float:
    """
    Approximates: F_ux = 1 - (alpha*V + beta*H + gamma*C)
    Proxied by UX-tagged issues (contrast, visibility, readability).
    """
    issues = report.get("issues", [])
    ux_hits = sum(
        1 for i in issues
        if any(kw in i.get("description", "").lower() for kw in (
            "contrast", "small", "font", "readable", "visible", "color", "unclear", "hard to see"
        ))
    )
    return max(0.0, min(1.0, 1.0 - (ux_hits * 0.15)))


# ── Composite ────────────────────────────────────────────────────────────────

def compute(
    adversarial_report: dict,
    state: dict,
    constraint_envelope: dict | None = None,
) -> dict:
    """
    Compute all seven fitness scores plus weighted composite.
    Returns a dict suitable for storing in round_data["fitness_scores"].
    """
    env = constraint_envelope or state.get("constraint_envelope") or {}
    scores = {
        "fun":          _fun(adversarial_report, state),
        "novelty":      _novelty(adversarial_report, state, env),
        "balance":      _balance(adversarial_report, state),
        "difficulty":   _difficulty(adversarial_report, state, env),
        "exploit_free": _exploit_free(adversarial_report),
        "performance":  _performance(adversarial_report, state),
        "ux_clarity":   _ux_clarity(adversarial_report),
    }
    scores["composite"] = round(
        sum(scores[k] * WEIGHTS[k] for k in WEIGHTS), 4
    )
    return scores


def verdict(composite: float) -> str:
    if composite >= ACCEPT_THRESHOLD:
        return "accept"
    if composite >= MUTATE_THRESHOLD:
        return "mutate"
    return "revert"


def format_summary(scores: dict) -> str:
    """Human-readable one-line fitness summary."""
    c = scores.get("composite", 0.0)
    v = verdict(c)
    parts = [f"{k[:3].upper()}={scores[k]:.2f}" for k in WEIGHTS]
    return f"composite={c:.2f} [{v.upper()}] | {' '.join(parts)}"
