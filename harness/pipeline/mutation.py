"""
AGX Mutation Operator Library.

Each operator targets a specific AGX-1 spec path, addresses one or more
fitness dimensions, and renders to a prompt fragment the generator can follow.

Operators are selected based on which fitness scores are below threshold.
Selection is weighted by the composite fitness weight of each dimension.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from harness.pipeline.fitness import WEIGHTS

SELECTION_THRESHOLD = 0.65  # fitness score below this triggers operator selection


@dataclass
class Operator:
    name: str
    category: str          # scalar | structural | layout | behavioral | rule | hybrid
    spec_path: str         # AGX-1 field path this targets
    fitness_addresses: list[str]   # which fitness dimensions this improves
    trigger_below: float   # only select if relevant fitness score < this
    prompt_fragment: str   # instruction fragment for the generator LLM


# ── Registry ─────────────────────────────────────────────────────────────────

REGISTRY: list[Operator] = [
    # ── Scalar ──────────────────────────────────────────────────────────────
    Operator(
        name="scalar_spawn_rate_increase",
        category="scalar",
        spec_path="mechanics.spawning.spawn_rules[*].interval_seconds",
        fitness_addresses=["difficulty", "fun"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [scalar_spawn_rate_increase]: Reduce the spawn interval for enemies/obstacles "
            "by 15–25% to increase pressure and engagement. Update mechanics.spawning.spawn_rules accordingly."
        ),
    ),
    Operator(
        name="scalar_spawn_rate_decrease",
        category="scalar",
        spec_path="mechanics.spawning.spawn_rules[*].interval_seconds",
        fitness_addresses=["difficulty", "fun"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [scalar_spawn_rate_decrease]: Increase the spawn interval by 20–30% to reduce "
            "frustration and improve approachability. Update mechanics.spawning.spawn_rules accordingly."
        ),
    ),
    Operator(
        name="scalar_entity_speed",
        category="scalar",
        spec_path="entities.npcs[*].speed",
        fitness_addresses=["difficulty", "balance"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [scalar_entity_speed]: Adjust NPC speeds by ±20% to better match the "
            "target difficulty curve. Update entities.npcs[*].speed values."
        ),
    ),
    Operator(
        name="scalar_hitbox_forgiveness",
        category="scalar",
        spec_path="entities.*.hitbox",
        fitness_addresses=["difficulty", "ux_clarity"],
        trigger_below=0.65,
        prompt_fragment=(
            "MUTATION [scalar_hitbox_forgiveness]: Reduce player and obstacle hitboxes by 15–20% "
            "to improve perceived fairness. Ensure hitboxes are visually distinct from sprites."
        ),
    ),
    Operator(
        name="scalar_timer_length",
        category="scalar",
        spec_path="mechanics.timers.global_timer_seconds",
        fitness_addresses=["fun", "difficulty"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [scalar_timer_length]: Adjust the session timer to better fit the pacing. "
            "A session that feels too short is low-fun; too long is low-engagement."
        ),
    ),

    # ── Structural ───────────────────────────────────────────────────────────
    Operator(
        name="add_npc_behavior",
        category="structural",
        spec_path="entities.npcs[*].behavior",
        fitness_addresses=["novelty", "fun"],
        trigger_below=0.65,
        prompt_fragment=(
            "MUTATION [add_npc_behavior]: Introduce a new NPC behavior type (e.g. dash_attack, "
            "oscillate, split_on_hit). Add a new NPC variant with this behavior to entities.npcs."
        ),
    ),
    Operator(
        name="add_scoring_event",
        category="structural",
        spec_path="design.scoring.score_events",
        fitness_addresses=["fun", "balance"],
        trigger_below=0.65,
        prompt_fragment=(
            "MUTATION [add_scoring_event]: Add a new scoring event (e.g. combo multiplier, "
            "near-miss bonus, speed kill). Add it to design.scoring.score_events and implement "
            "the reward feedback visually in the game."
        ),
    ),
    Operator(
        name="add_micro_goal",
        category="structural",
        spec_path="design.win_condition",
        fitness_addresses=["fun"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [add_micro_goal]: Introduce a visible micro-goal the player can achieve "
            "within 10–15 seconds (e.g. 'collect 5 in a row', 'survive a wave'). Display it "
            "prominently in the HUD."
        ),
    ),
    Operator(
        name="add_hazard_type",
        category="structural",
        spec_path="levels[*].environmental_rules.hazards",
        fitness_addresses=["difficulty", "novelty"],
        trigger_below=0.65,
        prompt_fragment=(
            "MUTATION [add_hazard_type]: Add a new environmental hazard type to the level "
            "(e.g. moving barrier, timed floor, shrinking safe zone). Add to "
            "levels[*].environmental_rules.hazards and implement it programmatically."
        ),
    ),

    # ── Layout ───────────────────────────────────────────────────────────────
    Operator(
        name="layout_platform_shift",
        category="layout",
        spec_path="levels[*].initial_entities",
        fitness_addresses=["difficulty", "fun"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [layout_platform_shift]: Reorganize platform/obstacle initial positions "
            "to create new routing options and timing windows. "
            "Update levels[*].initial_entities positions."
        ),
    ),
    Operator(
        name="layout_hazard_density",
        category="layout",
        spec_path="levels[*].environmental_rules.hazards",
        fitness_addresses=["difficulty"],
        trigger_below=0.55,
        prompt_fragment=(
            "MUTATION [layout_hazard_density]: Adjust the density of environmental hazards. "
            "Too many creates frustration; too few reduces tension."
        ),
    ),

    # ── Behavioral ───────────────────────────────────────────────────────────
    Operator(
        name="behavior_swap",
        category="behavioral",
        spec_path="entities.npcs[*].behavior",
        fitness_addresses=["novelty", "balance"],
        trigger_below=0.65,
        prompt_fragment=(
            "MUTATION [behavior_swap]: Change one or more NPC behavior profiles "
            "(e.g. patrol → chase, random → optimal). Update entities.npcs[*].behavior "
            "and adjust the implementation to match."
        ),
    ),
    Operator(
        name="aggression_curve",
        category="behavioral",
        spec_path="difficulty.scaling_rules",
        fitness_addresses=["fun", "difficulty"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [aggression_curve]: Introduce a mid-game difficulty spike by tuning "
            "difficulty.scaling_rules.spawn_rate_multiplier and enemy_speed_multiplier. "
            "Ensure the curve ramps, not flatlines."
        ),
    ),

    # ── Rule ─────────────────────────────────────────────────────────────────
    Operator(
        name="win_condition_mutation",
        category="rule",
        spec_path="design.win_condition",
        fitness_addresses=["novelty", "fun"],
        trigger_below=0.65,
        prompt_fragment=(
            "MUTATION [win_condition_mutation]: Change or augment the win condition to add "
            "a new dimension of challenge (e.g. from score_threshold to survive_duration+reach_goal). "
            "Update design.win_condition and the HUD to reflect the new goal clearly."
        ),
    ),
    Operator(
        name="lose_condition_tightening",
        category="rule",
        spec_path="design.lose_condition",
        fitness_addresses=["fun", "balance"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [lose_condition_tightening]: Make the lose condition more nuanced "
            "(e.g. add a resource depletion track alongside collision death). "
            "This adds strategic tension without pure frustration."
        ),
    ),
    Operator(
        name="exploit_patch",
        category="rule",
        spec_path="mechanics.interactions",
        fitness_addresses=["exploit_free", "balance"],
        trigger_below=0.70,
        prompt_fragment=(
            "MUTATION [exploit_patch]: Identify and close degenerate strategies: "
            "infinite loops, trivial wins, corner-camping, or moves that make the game unplayable. "
            "Update mechanics.interactions to eliminate these paths."
        ),
    ),

    # ── UX ───────────────────────────────────────────────────────────────────
    Operator(
        name="ux_contrast_palette",
        category="hybrid",
        spec_path="aesthetics.color_palette",
        fitness_addresses=["ux_clarity"],
        trigger_below=0.65,
        prompt_fragment=(
            "MUTATION [ux_contrast_palette]: Revise aesthetics.color_palette to ensure "
            "player, enemies, UI, and background are visually distinct. "
            "Minimum contrast ratio 4.5:1 between interactive elements and background."
        ),
    ),
    Operator(
        name="ux_hud_prominence",
        category="hybrid",
        spec_path="aesthetics",
        fitness_addresses=["ux_clarity", "fun"],
        trigger_below=0.65,
        prompt_fragment=(
            "MUTATION [ux_hud_prominence]: Make score/timer/objective HUD elements larger "
            "(min 18px), higher contrast, and permanently visible. "
            "Move any instructions that overlap gameplay into a pre-game overlay."
        ),
    ),

    # ── Novelty ──────────────────────────────────────────────────────────────
    Operator(
        name="core_loop_step_mutation",
        category="rule",
        spec_path="design.core_loop.steps",
        fitness_addresses=["novelty"],
        trigger_below=0.60,
        prompt_fragment=(
            "MUTATION [core_loop_step_mutation]: Add a new step to the core loop that "
            "introduces a twist the player hasn't seen in this genre. "
            "Update design.core_loop.steps and implement the new mechanic."
        ),
    ),
]

_BY_NAME = {op.name: op for op in REGISTRY}


# ── Selection ─────────────────────────────────────────────────────────────────

def select(
    fitness_scores: dict,
    issues: list[dict],
    action: str,
    constraint_envelope: dict | None = None,
) -> list[Operator]:
    """
    Select operators based on which fitness scores are below threshold.
    On REWRITE, return empty list (full redesign, no incremental mutations).
    Prioritised by composite weight of the fitness dimension addressed.
    """
    if action == "REWRITE":
        return []

    low_dims = {
        dim for dim, score in fitness_scores.items()
        if dim != "composite" and score < SELECTION_THRESHOLD
    }

    # Always include exploit_patch if exploit issues are present
    has_exploits = any(
        "exploit" in i.get("description", "").lower() or
        "infinite" in i.get("description", "").lower()
        for i in issues
    )
    if has_exploits:
        low_dims.add("exploit_free")

    # Score each candidate operator
    candidates: list[tuple[float, Operator]] = []
    for op in REGISTRY:
        relevance = sum(
            WEIGHTS.get(dim, 0.0) * (SELECTION_THRESHOLD - fitness_scores.get(dim, 0.5))
            for dim in op.fitness_addresses
            if dim in low_dims
        )
        if relevance > 0:
            candidates.append((relevance, op))

    # Sort by relevance descending, cap at 4 operators per pass
    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = [op for _, op in candidates[:4]]

    return selected


def to_guidance(operators: list[Operator], issues: list[dict]) -> str:
    """Render selected operators into a structured guidance string for the generator."""
    if not operators:
        return ""

    lines = ["Apply the following targeted mutations to improve the game:"]
    for op in operators:
        lines.append(f"\n{op.prompt_fragment}")

    # Append any issue-specific suggestions not covered by operators
    addressed_keywords = " ".join(op.prompt_fragment.lower() for op in operators)
    unaddressed = [
        i for i in issues
        if i.get("suggestion") and i.get("suggestion", "").lower()[:20] not in addressed_keywords
    ]
    if unaddressed:
        lines.append("\nAdditional specific fixes:")
        for i in unaddressed[:3]:
            lines.append(f"  - [{i.get('severity')}] {i.get('suggestion', '')}")

    return "\n".join(lines)


def operator_names(operators: list[Operator]) -> list[str]:
    return [op.name for op in operators]
