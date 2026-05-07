import re
from pathlib import Path

from harness.llm.router import get_client_for_role


def _load_phaser_references(ref_dir: str) -> str:
    parts = []
    for f in sorted(Path(ref_dir).glob("*.md")):
        parts.append(f"### {f.stem}\n\n{f.read_text()}")
    return "\n\n---\n\n".join(parts)


def _build_system_prompt(config: dict, prompt_dir: str) -> str:
    template = (Path(prompt_dir) / "generator_system.md").read_text()
    refs = _load_phaser_references(config["paths"]["phaser_references"])
    return (
        template
        .replace("{{PHASER_REFERENCES}}", refs)
        .replace("{{PHASER_CDN}}", config["paths"]["phaser_cdn"])
    )


def _extract_html(text: str) -> str:
    m = re.search(r"```html\s*([\s\S]*?)```", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"(<!DOCTYPE html[\s\S]*|<html[\s\S]*)", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text.strip()


def _extract_concept(text: str) -> str:
    for line in text.strip().splitlines()[:10]:
        line = line.strip()
        if line and not line.startswith("<") and not line.startswith("```"):
            return line[:200]
    return "Untitled"


def generate(
    config: dict,
    prompt_dir: str,
    action: str,
    design_doc: dict | None = None,
    concept: str | None = None,
    prior_issues: list[dict] | None = None,
    generator_guidance: str | None = None,
    prior_html: str | None = None,
) -> tuple[str, str]:
    """
    Returns (game_html, concept_description).

    action: "REWRITE" | "REVISE" | "POLISH"
    design_doc: approved GDD from the design phase — used as the spec on first generation.
    """
    client, role_cfg = get_client_for_role("generator", config)
    system = _build_system_prompt(config, prompt_dir)

    if action == "REWRITE" or not prior_html:
        if design_doc:
            user_parts = [
                "Build this game exactly to its AGX-1 spec. The design has been approved — implement it faithfully.",
                f"\nApproved AGX-1 Game Spec:\n```json\n{json.dumps(design_doc, indent=2)}\n```",
                "\nImplementation requirements:",
                "- Single self-contained HTML file, all JavaScript inline",
                "- Phaser.js from CDN only — no other external resources",
                "- All visuals drawn programmatically (Graphics API, shapes, particles, text) — no image files",
                "- Implement all scenes, entities, mechanics, and difficulty scaling defined in the spec",
                "- Wire up telemetry_contract events as console.log calls for future collection",
            ]
        else:
            user_parts = [
                "Invent and build a completely unique, experimental web game using Phaser.js. "
                "Output a single self-contained HTML file with all JavaScript inline and all visuals drawn programmatically."
            ]
        if generator_guidance:
            user_parts.append(f"\nAvoid these problems from the previous attempt:\n{generator_guidance}")
    else:
        issue_lines = "\n".join(
            f"[{i['severity']}] {i['description']} → {i.get('suggestion', '')}"
            for i in (prior_issues or [])
        )
        user_parts = [
            f"Revise the following Phaser.js game to fix these issues:\n\n{issue_lines}",
            "\nPreserve the core concept and mechanics. Fix only what's listed.",
        ]
        if generator_guidance:
            user_parts.append(f"\nAdditional guidance:\n{generator_guidance}")
        user_parts.append(f"\nCurrent game HTML:\n```html\n{prior_html}\n```")
        user_parts.append("\nOutput the complete revised HTML file.")

    response = client.chat.completions.create(
        model=role_cfg["model"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": "\n".join(user_parts)},
        ],
        temperature=role_cfg.get("temperature", 0.9),
        max_tokens=role_cfg.get("max_tokens", 16000),
    )

    content = response.choices[0].message.content
    html = _extract_html(content)
    new_concept = concept or (design_doc or {}).get("hook") or _extract_concept(content)
    return html, new_concept
