from enum import Enum


class Severity(str, Enum):
    BLOCKING = "BLOCKING"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class Action(str, Enum):
    REWRITE = "REWRITE"    # BLOCKING found — full redesign
    REVISE = "REVISE"      # MAJOR found — targeted fixes
    POLISH = "POLISH"      # MINOR only — light touch
    APPROVE = "APPROVE"    # Clean — milestone check + ship
    ESCALATE = "ESCALATE"  # MAJOR retry limit hit


def decide_action(issues: list[dict], retry_counts: dict, config: dict) -> Action:
    """Hard-rule action decision. Overrides whatever editorial suggests."""
    max_major = config["pipeline"]["max_major_retries"]
    severities = {i.get("severity") for i in issues}

    if Severity.BLOCKING in severities:
        return Action.REWRITE

    if Severity.MAJOR in severities:
        if retry_counts.get("MAJOR", 0) >= max_major:
            return Action.ESCALATE
        return Action.REVISE

    if Severity.MINOR in severities:
        return Action.POLISH

    return Action.APPROVE
