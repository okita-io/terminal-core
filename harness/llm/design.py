import json
import re
from pathlib import Path

from harness.llm.router import get_client_for_role
from harness.schema import spec as spec_schema


def _parse_json(text: str) -> dict:
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {}


def _build_design_prompt(prompt_dir: str, game_id: str, envelope: dict) -> str:
    template = (Path(prompt_dir) / "design_system.md").read_text()
    envelope_str = json.dumps(envelope, indent=2) if envelope else "No constraints — full creative freedom."
    return (
        template
        .replace("{{CONSTRAINT_ENVELOPE}}", envelope_str)
        .replace("{{GAME_ID}}", game_id)
    )


def _build_review_system(prompt_dir: str) -> str:
    template = (Path(prompt_dir) / "design_review_system.md").read_text()
    schell_path = Path(prompt_dir) / "game_designer.md"
    schell = schell_path.read_text() if schell_path.exists() else ""
    return template.replace("{{SCHELL_FRAMEWORK}}", schell)


def generate_gdd(
    config: dict,
    prompt_dir: str,
    game_id: str,
    constraint_envelope: dict | None = None,
    prior_gdd: dict | None = None,
    designer_guidance: str | None = None,
    action: str = "REWRITE",
) -> dict:
    """
    Generate or revise an AGX-1 Game Spec.
    Returns parsed spec dict (may be partial if LLM output is malformed).
    """
    client, role_cfg = get_client_for_role("generator", config)
    system = _build_design_prompt(prompt_dir, game_id, constraint_envelope or {})

    if action == "REWRITE" or not prior_gdd:
        user = "Design an original game spec conforming exactly to the AGX-1 schema."
        if designer_guidance:
            user += f"\n\nThe previous concept was rejected. Avoid these problems:\n{designer_guidance}"
    else:
        user = (
            f"Revise this AGX-1 Game Spec based on the following feedback:\n\n"
            f"{designer_guidance or 'Improve completeness, novelty, and clarity.'}\n\n"
            f"Current spec:\n```json\n{json.dumps(prior_gdd, indent=2)}\n```\n\n"
            "Output the complete revised spec as a JSON object. Preserve the game_id."
        )

    response = client.chat.completions.create(
        model=role_cfg["model"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=role_cfg.get("temperature", 0.9),
        max_tokens=6000,
    )

    gdd = _parse_json(response.choices[0].message.content)

    # Ensure game_id is preserved
    if not gdd.get("game_id"):
        gdd["game_id"] = game_id

    # Run schema validation — errors become MAJOR issues attached to the spec
    is_valid, errors = spec_schema.validate(gdd)
    if not is_valid:
        gdd["_validation_errors"] = errors

    return gdd


def review_gdd(
    config: dict,
    prompt_dir: str,
    gdd: dict,
    design_round: int,
    design_retries: int,
    max_retries: int,
) -> dict:
    """
    Grade a GDD using the editorial LLM with Schell + AGX-1 validation.
    Returns {schell_analysis, action, verdict, issues, summary, designer_guidance}.
    """
    client, role_cfg = get_client_for_role("editorial", config)
    system = _build_review_system(prompt_dir)

    # Inject any schema validation errors as pre-classified MAJOR issues
    validation_errors = gdd.pop("_validation_errors", [])
    pre_issues = [
        {
            "severity": "MAJOR",
            "field": err.split(":")[1].strip() if ":" in err else "schema",
            "description": err,
            "suggestion": "Fix the AGX-1 schema field to match the required format.",
        }
        for err in validation_errors
    ]

    user = (
        f"Review this AGX-1 Game Spec (design round {design_round}, "
        f"retries used: {design_retries}/{max_retries}):\n\n"
        f"```json\n{json.dumps(gdd, indent=2)}\n```\n\n"
    )
    if pre_issues:
        user += (
            f"Schema validation found these issues (treat as MAJOR):\n"
            + "\n".join(f"- {e['description']}" for e in pre_issues)
            + "\n\n"
        )
    user += "Output your review as a single JSON object."

    response = client.chat.completions.create(
        model=role_cfg["model"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=role_cfg.get("temperature", 0.2),
        max_tokens=4000,
    )

    result = _parse_json(response.choices[0].message.content)

    # Merge pre-classified schema issues
    all_issues = pre_issues + result.get("issues", [])
    result["issues"] = all_issues

    # Hard-enforce action
    severities = {i.get("severity") for i in all_issues}
    if "BLOCKING" in severities:
        result["action"] = "REWRITE"
    elif "MAJOR" in severities:
        result["action"] = "REWRITE" if design_retries >= max_retries else "REVISE"
    else:
        result["action"] = "APPROVE"

    return result
