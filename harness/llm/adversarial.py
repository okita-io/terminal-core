import json
import re
from pathlib import Path

from harness.llm.router import get_client_for_role


def _parse(text: str) -> dict:
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {
        "can_play_without_guessing": False,
        "first_impression": "Failed to parse VLM response",
        "issues": [
            {
                "severity": "BLOCKING",
                "description": "VLM response could not be parsed as JSON",
                "element": "system",
                "suggestion": "Retry the adversarial pass",
            }
        ],
        "summary": text[:500],
    }


def evaluate(
    config: dict,
    prompt_dir: str,
    screenshots_b64: list[str],
    round_n: int,
    prior_summaries: list[str] | None = None,
) -> dict:
    client, role_cfg = get_client_for_role("adversarial", config)
    system = (Path(prompt_dir) / "adversarial_system.md").read_text()

    content: list[dict] = [
        {
            "type": "text",
            "text": (
                f"Round {round_n}: Evaluate these game screenshots as a first-time player. "
                "Identify every issue that would prevent understanding how to play without guessing."
            ),
        }
    ]

    for b64 in screenshots_b64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"},
        })

    if prior_summaries:
        history = "\n".join(f"- {s}" for s in prior_summaries[-3:])
        content.append({
            "type": "text",
            "text": f"Issues found in prior rounds (for context, do not assume fixed):\n{history}",
        })

    content.append({
        "type": "text",
        "text": "Output your evaluation as a single JSON object matching the format in your instructions.",
    })

    response = client.chat.completions.create(
        model=role_cfg["model"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ],
        temperature=role_cfg.get("temperature", 0.3),
        max_tokens=role_cfg.get("max_tokens", 4000),
    )

    return _parse(response.choices[0].message.content)
