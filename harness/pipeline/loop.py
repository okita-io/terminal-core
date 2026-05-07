import base64
import json
import logging
from pathlib import Path

from harness.llm import adversarial as adv_llm
from harness.llm import design as design_llm
from harness.llm import editorial as ed_llm
from harness.llm import generator as gen_llm
from harness.pipeline import fitness as fitness_mod
from harness.pipeline import mutation as mutation_mod
from harness.pipeline.severity import Action
from harness.renderer import playwright_runner as renderer
from harness.storage import milestones, session as sess
from harness.storage import spec_store
from harness.storage.vectordb import FeedbackStore

logger = logging.getLogger(__name__)

_DESIGN_STAGES  = {"INIT", "DESIGN_REWRITE", "DESIGN_REVISE"}
_GENERATE_STAGES = {"REWRITE", "REVISE", "POLISH"}


def run(config: dict, prompt_dir: str, state: dict, sessions_dir: str) -> dict:
    game_id = state["game_id"]
    store = FeedbackStore(sessions_dir, game_id)

    while state["stage"] not in ("SHIPPED", "ESCALATED"):
        stage = state["stage"]
        logger.info(
            f"[{game_id[:8]}] stage={stage} "
            f"design_round={state.get('design_round', 0)} "
            f"round={state['round']} "
            f"milestone={state.get('milestone') or '-'}"
        )

        # ── DESIGN DOC ────────────────────────────────────────────────────────
        if stage in _DESIGN_STAGES:
            prior_gdd = state.get("design_doc")
            guidance = state.get("_design_guidance")
            action = "REWRITE" if stage in ("INIT", "DESIGN_REWRITE") else "REVISE"

            gdd = design_llm.generate_gdd(
                config=config,
                prompt_dir=prompt_dir,
                game_id=game_id,
                constraint_envelope=state.get("constraint_envelope"),
                prior_gdd=prior_gdd if action == "REVISE" else None,
                designer_guidance=guidance,
                action=action,
            )

            state["design_doc"] = gdd
            state["design_round"] = state.get("design_round", 0) + 1
            if not state.get("title") and gdd.get("title"):
                state["title"] = gdd["title"]

            state["stage"] = "DESIGN_REVIEW"
            sess.save_session(sessions_dir, state)

        # ── DESIGN REVIEW ─────────────────────────────────────────────────────
        elif stage == "DESIGN_REVIEW":
            gdd = state.get("design_doc", {})
            review = design_llm.review_gdd(
                config=config,
                prompt_dir=prompt_dir,
                gdd=gdd,
                design_round=state.get("design_round", 0),
                design_retries=state["retry_counts"].get("DESIGN", 0),
                max_retries=config["pipeline"]["max_design_retries"],
            )

            action = review.get("action", "REVISE")
            logger.info(f"[{game_id[:8]}] design review → {action}: {review.get('verdict', '')}")

            # Persist the design review in its own directory
            sess.save_design_review(sessions_dir, game_id, state.get("design_round", 0), {
                "type": "design_review",
                "design_round": state.get("design_round", 0),
                "gdd": gdd,
                "review": review,
            })

            store.add_round(
                -(state.get("design_round", 0)),  # negative = design round in vectordb
                review.get("summary", ""),
                metadata={"type": "design_review", "action": action},
            )

            if action == "APPROVE":
                state["concept"] = (
                    gdd.get("metadata", {}).get("description")
                    or gdd.get("title")
                    or "Untitled"
                )
                state["title"] = gdd.get("metadata", {}).get("title") or gdd.get("title") or state.get("title", "Untitled")
                state.pop("_design_guidance", None)

                # Save versioned spec
                parent_id = state.get("spec_id")
                spec_id = spec_store.save_spec(sessions_dir, game_id, gdd, parent_spec_id=parent_id)
                state["spec_id"] = spec_id
                state["spec_version"] = state.get("spec_version", 0) + 1
                state["spec_lineage"] = state.get("spec_lineage", []) + [spec_id]

                new_ms = milestones.check_and_record(sessions_dir, state)
                if new_ms:
                    logger.info(f"[{game_id[:8]}] Milestone: {new_ms.upper()}")

                state["stage"] = "GENERATE"
            elif action == "REWRITE":
                state["retry_counts"]["DESIGN"] += 1
                state["_design_guidance"] = review.get("designer_guidance", "")
                state["design_doc"] = None
                state["stage"] = "DESIGN_REWRITE"
            else:  # REVISE
                state["retry_counts"]["DESIGN"] += 1
                state["_design_guidance"] = review.get("designer_guidance", "")
                state["stage"] = "DESIGN_REVISE"

            sess.save_session(sessions_dir, state)

        # ── GENERATE ─────────────────────────────────────────────────────────
        elif stage in _GENERATE_STAGES or stage == "GENERATE":
            prior_html = None
            prior_issues = None
            guidance = None

            if state["rounds_completed"] and stage != "REWRITE":
                last = sess.load_round(sessions_dir, game_id, state["rounds_completed"][-1])
                prior_issues = last.get("classified_issues")
                guidance = last.get("generator_guidance")
                if state["current_game_path"]:
                    prior_html = Path(state["current_game_path"]).read_text()

            gen_action = "REWRITE" if stage in ("GENERATE", "REWRITE") else stage
            html, concept = gen_llm.generate(
                config=config,
                prompt_dir=prompt_dir,
                action=gen_action,
                design_doc=state.get("design_doc"),
                concept=state.get("concept"),
                prior_issues=prior_issues,
                generator_guidance=guidance,
                prior_html=prior_html,
            )

            game_dir = sess.get_game_dir(sessions_dir, game_id)
            game_dir.mkdir(parents=True, exist_ok=True)
            game_path = game_dir / "index.html"
            game_path.write_text(html)

            state["current_game_path"] = str(game_path)
            if not state.get("concept"):
                state["concept"] = concept
            if not state.get("title"):
                state["title"] = concept[:60]

            state["stage"] = "RENDERING"
            sess.save_session(sessions_dir, state)

        # ── RENDER ───────────────────────────────────────────────────────────
        elif stage == "RENDERING":
            shots_dir = sess.get_screenshots_dir(sessions_dir, game_id, state["round"])
            screenshots, errors = renderer.capture(
                html_path=state["current_game_path"],
                output_dir=shots_dir,
                count=config["pipeline"]["screenshot_count"],
                wait_ms=config["pipeline"]["render_wait_ms"],
                interaction_wait_ms=config["pipeline"]["interaction_wait_ms"],
            )

            if not screenshots:
                logger.error(f"[{game_id[:8]}] No screenshots — forcing REWRITE")
                state["retry_counts"]["BLOCKING"] += 1
                state["stage"] = "REWRITE"
                sess.save_session(sessions_dir, state)
                continue

            round_data = {
                "round": state["round"],
                "stage": "RENDERING",
                "screenshot_paths": [str(shots_dir / f"screenshot_{i:02d}.png") for i in range(len(screenshots))],
                "console_errors": errors,
            }
            sess.save_round(sessions_dir, game_id, state["round"], round_data)

            # alpha: first successful render
            new_ms = milestones.check_and_record(sessions_dir, state)
            if new_ms:
                logger.info(f"[{game_id[:8]}] Milestone: {new_ms.upper()}")

            state["stage"] = "ADVERSARIAL"
            sess.save_session(sessions_dir, state)

        # ── ADVERSARIAL ───────────────────────────────────────────────────────
        elif stage == "ADVERSARIAL":
            shots_dir = sess.get_screenshots_dir(sessions_dir, game_id, state["round"])
            screenshots_b64 = [
                base64.b64encode(p.read_bytes()).decode()
                for p in sorted(shots_dir.glob("screenshot_*.png"))
            ]

            report = adv_llm.evaluate(
                config=config,
                prompt_dir=prompt_dir,
                screenshots_b64=screenshots_b64,
                round_n=state["round"],
                prior_summaries=store.get_all_summaries(),
            )

            round_data = sess.load_round(sessions_dir, game_id, state["round"])
            round_data["adversarial_report"] = report
            round_data["stage"] = "ADVERSARIAL"
            sess.save_round(sessions_dir, game_id, state["round"], round_data)

            state["stage"] = "EDITORIAL"
            sess.save_session(sessions_dir, state)

        # ── EDITORIAL ─────────────────────────────────────────────────────────
        elif stage == "EDITORIAL":
            round_data = sess.load_round(sessions_dir, game_id, state["round"])
            report = round_data.get("adversarial_report", {})

            # Attach console errors to report for performance fitness computation
            report["_console_errors"] = round_data.get("console_errors", [])

            # Compute fitness scores before editorial synthesis
            fit_scores = fitness_mod.compute(
                adversarial_report=report,
                state=state,
                constraint_envelope=state.get("constraint_envelope"),
            )
            logger.info(f"[{game_id[:8]}] {fitness_mod.format_summary(fit_scores)}")

            similar = store.query_similar(report.get("summary", ""), n=3)

            editorial = ed_llm.synthesize(
                config=config,
                prompt_dir=prompt_dir,
                adversarial_report=report,
                state=state,
                similar_past=similar,
                fitness_scores=fit_scores,
            )

            action = editorial["action"]
            issues = editorial.get("classified_issues", [])

            # Select mutation operators for REVISE / POLISH passes
            operators = mutation_mod.select(
                fitness_scores=fit_scores,
                issues=issues,
                action=action,
                constraint_envelope=state.get("constraint_envelope"),
            )
            mutation_guidance = mutation_mod.to_guidance(operators, issues)
            op_names = mutation_mod.operator_names(operators)
            if op_names:
                logger.info(f"[{game_id[:8]}] Mutation operators: {op_names}")

            # Combine editorial guidance with mutation operator instructions
            base_guidance = editorial.get("generator_guidance", "")
            combined_guidance = "\n\n".join(filter(None, [base_guidance, mutation_guidance]))

            # Update resolution flags
            state["issues_by_severity"] = {
                "BLOCKING": sum(1 for i in issues if i.get("severity") == "BLOCKING"),
                "MAJOR":    sum(1 for i in issues if i.get("severity") == "MAJOR"),
                "MINOR":    sum(1 for i in issues if i.get("severity") == "MINOR"),
            }
            state["blocking_resolved"] = state["issues_by_severity"]["BLOCKING"] == 0
            state["major_resolved"]    = state["issues_by_severity"]["MAJOR"] == 0
            state["minor_resolved"]    = state["issues_by_severity"]["MINOR"] == 0
            state["fitness_scores"]    = fit_scores
            state["fitness_history"]   = state.get("fitness_history", []) + [fit_scores["composite"]]

            # Persist full editorial + fitness in round
            round_data.update({
                "editorial": editorial,
                "classified_issues": issues,
                "generator_guidance": combined_guidance,
                "fitness_scores": fit_scores,
                "selected_operators": op_names,
                "action": action,
                "stage": "EDITORIAL",
            })
            sess.save_round(sessions_dir, game_id, state["round"], round_data)

            # Store summary + fitness in vectordb
            store.add_round(
                state["round"],
                editorial.get("summary", report.get("summary", "")),
                metadata={
                    "action": action,
                    "blocking": state["issues_by_severity"]["BLOCKING"],
                    "major": state["issues_by_severity"]["MAJOR"],
                    "minor": state["issues_by_severity"]["MINOR"],
                    "composite_fitness": fit_scores["composite"],
                },
            )

            # Update retry counters
            if action == Action.REWRITE:
                state["retry_counts"]["BLOCKING"] += 1
                state["retry_counts"]["MAJOR"] = 0
                state["retry_counts"]["MINOR"] = 0
            elif action == Action.REVISE:
                state["retry_counts"]["MAJOR"] += 1
            elif action == Action.POLISH:
                state["retry_counts"]["MINOR"] += 1

            state["rounds_completed"].append(state["round"])
            state["round"] += 1

            # Milestone check
            new_ms = milestones.check_and_record(sessions_dir, state)
            if new_ms:
                logger.info(f"[{game_id[:8]}] Milestone: {new_ms.upper()}")

            if action == Action.APPROVE:
                state["stage"] = "SHIPPED"
                logger.info(f"[{game_id[:8]}] SHIPPED — fitness={fit_scores['composite']:.2f} milestone={state.get('milestone')}")
            elif action == Action.ESCALATE:
                state["stage"] = "ESCALATED"
                logger.warning(f"[{game_id[:8]}] ESCALATED — max MAJOR retries reached")
            else:
                state["stage"] = action  # REWRITE | REVISE | POLISH

            sess.save_session(sessions_dir, state)

        elif stage not in ("SHIPPED", "ESCALATED"):
            logger.error(f"[{game_id[:8]}] Unknown stage: {stage}")
            break

    return state
