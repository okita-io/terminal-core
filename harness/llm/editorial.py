import json
import re
from pathlib import Path

from harness.llm.router import get_client_for_role
from harness.pipeline.severity import decide_action


def _parse(text: str) -> dict:
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {
        "action": "REVISE",
        "classified_issues": [],
        "summary": text[:300],
        "generator_guidance": "Fix all identified issues and improve UI clarity.",
    }


def synthesize(
    config: dict,
    prompt_dir: str,
    adversarial_report: dict,
    state: dict,
    similar_past: list[dict] | None = None,
    fitness_scores: dict | None = None,
) -> dict:
    client, role_cfg = get_client_for_role("editorial", config)
    system = (Path(prompt_dir) / "editorial_system.md").read_text()

    past_ctx = ""
    if similar_past:
        lines = "\n".join(
            f"  Round {r['metadata']['round']}: {r['document']}" for r in similar_past[:3]
        )
        past_ctx = f"\n\nSimilar past rounds (for pattern awareness):\n{lines}"

    fitness_ctx = ""
    if fitness_scores:
        from harness.pipeline.fitness import format_summary
        fitness_ctx = f"\n\nFitness scores: {format_summary(fitness_scores)}"

    user = f"""Adversarial report:
{json.dumps(adversarial_report, indent=2)}

Session state:
- Round: {state['round']}
- Current milestone: {state.get('milestone') or 'none'}
- BLOCKING retries: {state['retry_counts'].get('BLOCKING', 0)}
- MAJOR retries: {state['retry_counts'].get('MAJOR', 0)}
- MINOR retries: {state['retry_counts'].get('MINOR', 0)}
{fitness_ctx}
{past_ctx}

Output your editorial decision as a single JSON object."""

    response = client.chat.completions.create(
        model=role_cfg["model"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=role_cfg.get("temperature", 0.2),
        max_tokens=role_cfg.get("max_tokens", 4000),
    )

    result = _parse(response.choices[0].message.content)

    # Hard-enforce action based on severity rules — editorial cannot override these
    issues = result.get("classified_issues") or adversarial_report.get("issues", [])
    enforced = decide_action(issues, state["retry_counts"], config)
    result["action"] = enforced.value
    result["classified_issues"] = issues

    return result
