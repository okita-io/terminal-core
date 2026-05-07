#!/usr/bin/env python3
import argparse
import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from harness.pipeline import loop
from harness.storage import session as sess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("terminal-core")


def load_config(path: str = "config.json") -> dict:
    return json.loads(Path(path).read_text())


def cmd_new(args, config):
    envelope = {
        "genre":                  args.genre,
        "input_model":            args.input_model,
        "session_length_seconds": args.session_length,
        "novelty_target":         args.novelty_target,
        "difficulty_target":      args.difficulty,
        "performance_budget_ms":  args.perf_budget,
        "intended_players":       args.intended_players,
    }
    # Strip None values so the design prompt distinguishes "not specified" from "null"
    envelope = {k: v for k, v in envelope.items() if v is not None}

    state = sess.new_session(
        config["paths"]["sessions_dir"],
        title=args.title,
        constraint_envelope=envelope,
    )
    logger.info(f"New session: {state['game_id']} envelope={envelope or 'unconstrained'}")
    loop.run(config, config["paths"]["prompts_dir"], state, config["paths"]["sessions_dir"])


def cmd_resume(args, config):
    sessions_dir = config["paths"]["sessions_dir"]

    if args.game_id:
        state = sess.load_session(sessions_dir, args.game_id)
    else:
        all_sessions = sess.list_sessions(sessions_dir)
        resumable = [s for s in all_sessions if s["stage"] not in ("SHIPPED", "ESCALATED")]
        if not resumable:
            logger.error("No resumable sessions found.")
            sys.exit(1)
        state = resumable[0]

    logger.info(f"Resuming {state['game_id']} — stage={state['stage']} round={state['round']}")
    loop.run(config, config["paths"]["prompts_dir"], state, sessions_dir)


def cmd_list(args, config):
    all_sessions = sess.list_sessions(config["paths"]["sessions_dir"])
    if not all_sessions:
        print("No sessions.")
        return
    print(f"{'ID':<38}  {'Stage':<12}  {'Milestone':<10}  {'Rnd':>3}  Title")
    print("─" * 85)
    for s in all_sessions:
        print(
            f"{s['game_id']:<38}  "
            f"{s['stage']:<12}  "
            f"{s.get('milestone') or '-':<10}  "
            f"{s['round']:>3}  "
            f"{s.get('title') or '-'}"
        )


def main():
    parser = argparse.ArgumentParser(description="Terminal Core Game Harness")
    parser.add_argument("--config", default="config.json", help="Config file path")
    sub = parser.add_subparsers(dest="command", required=True)

    new_p = sub.add_parser("new", help="Start a new game generation session")
    new_p.add_argument("--title",            help="Optional working title")
    new_p.add_argument("--genre",            help="Genre hint: micro_arcade|puzzle|platformer|rhythm|tactics|survival|experimental")
    new_p.add_argument("--input-model",      dest="input_model", help="Input model: one_button|two_button|keyboard_arrows|mouse_only|touch_swipe|hybrid")
    new_p.add_argument("--session-length",   dest="session_length", type=int, help="Target session length in seconds")
    new_p.add_argument("--novelty-target",   dest="novelty_target", type=float, default=0.7, help="Novelty target 0.0–1.0 (default 0.7)")
    new_p.add_argument("--difficulty",       default="normal", help="Target difficulty: easy|normal|hard|extreme")
    new_p.add_argument("--perf-budget",      dest="perf_budget", type=int, default=16, help="Performance budget in ms per frame (default 16)")
    new_p.add_argument("--intended-players", dest="intended_players", default="human_vs_ai", help="human_only|ai_only|human_vs_ai|co_play")

    res_p = sub.add_parser("resume", help="Resume an interrupted session")
    res_p.add_argument("--game-id", dest="game_id", help="Game ID (default: most recent resumable)")

    sub.add_parser("list", help="List all sessions")

    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == "new":
        cmd_new(args, config)
    elif args.command == "resume":
        cmd_resume(args, config)
    elif args.command == "list":
        cmd_list(args, config)


if __name__ == "__main__":
    main()
