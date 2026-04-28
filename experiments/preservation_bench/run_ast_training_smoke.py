#!/usr/bin/env python3
import argparse
import json
import platform
import sys
from pathlib import Path

import torch

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = SCRIPT_DIR.parent
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ast_preservation.agent.full_agent import FullAgent
from ast_preservation.config import Config, set_seed
from ast_preservation.env.arena import Arena
from ast_preservation.evaluation.behavioral import (
    build_identity_probe_cues,
    evaluate_identity_probe_accuracy,
    evaluate_memory_overlap,
)
from ast_preservation.training.trainer import Trainer
from benchmark.episode_logs import (
    aggregate_episode_logs,
    summarize_episode,
    write_episode_logs_jsonl,
)
from benchmark.seeds import build_seed_registry, stable_seed, write_seed_registry
from benchmark.validation import validate_source_summary
from run_ast_checkpoint_eval import build_condition_agent, run_condition, write_json


def load_config(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def read_json(path: Path):
    with path.open() as f:
        return json.load(f)


def update_seed_manifest(seed_dir: Path, updates: dict) -> dict:
    path = seed_dir / "manifest.json"
    if path.exists():
        manifest = read_json(path)
    else:
        manifest = {}
    manifest.update(updates)
    write_json(path, manifest)
    return manifest


def make_cfg(run_cfg: dict, seed: int) -> Config:
    cfg = Config()
    cfg.seed = seed
    for key, value in run_cfg.get("config_overrides", {}).items():
        if not hasattr(cfg, key):
            raise ValueError(f"Unknown Config override: {key}")
        setattr(cfg, key, value)
    if "obs_window" in run_cfg.get("config_overrides", {}):
        cfg.attn_map_size = int(cfg.obs_window) * int(cfg.obs_window)
    cfg.total_steps = int(run_cfg.get("source_steps", cfg.total_steps))
    cfg.finetune_steps = int(run_cfg.get("finetune_steps", cfg.finetune_steps))
    cfg.max_steps = int(run_cfg.get("max_steps", cfg.max_steps))
    cfg.curriculum_phase1_steps = int(
        run_cfg.get("curriculum_phase1_steps", cfg.curriculum_phase1_steps)
    )
    cfg.curriculum_phase2_steps = int(
        run_cfg.get("curriculum_phase2_steps", cfg.curriculum_phase2_steps)
    )
    cfg.condition_finetune_steps = dict(run_cfg.get("condition_finetune_steps", {}))
    cfg.condition_seed_aliases = dict(run_cfg.get("condition_seed_aliases", {}))
    return cfg


def load_source_agent(cfg: Config, checkpoint_path: Path) -> FullAgent:
    agent = FullAgent(cfg)
    ckpt = torch.load(checkpoint_path, weights_only=False, map_location=cfg.device)
    agent.load_state_dict(ckpt["agent"])
    if "memory" in ckpt:
        agent.self_model.load_memory_state(ckpt["memory"])
    agent.eval()
    return agent


def train_source_agent(cfg: Config, output_dir: Path) -> tuple[FullAgent, dict]:
    set_seed(cfg.seed)
    env = Arena(cfg)
    agent = FullAgent(cfg)
    trainer = Trainer(agent, cfg)

    episode = 0
    while trainer.global_step < cfg.total_steps:
        trainer.train_step(env)
        episode += 1

    output_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_checkpoint(output_dir / "source_final.pt")

    curve = {
        "seed": cfg.seed,
        "episode_rewards": trainer.episode_rewards,
        "total_steps": trainer.global_step,
        "total_episodes": episode,
    }
    write_json(output_dir / "training_curve.json", curve)
    agent.eval()
    return agent, curve


def is_source_condition(condition: str) -> bool:
    return condition.startswith("source_")


def evaluate_seed(
    run_cfg: dict,
    source_agent: FullAgent,
    cfg: Config,
    train_idx: int,
    output_dir: Path,
    force: bool = False,
) -> list[dict]:
    study_id = run_cfg["study_id"]
    master_seed = int(run_cfg["master_seed"])
    n_eval_episodes = int(run_cfg["n_eval_episodes"])
    conditions = list(run_cfg["conditions"])

    source_memories = source_agent.self_model.get_memory_state()
    identity_seed = stable_seed(study_id, master_seed, "identity_probe_seed", "source", train_idx)
    identity_cues = build_identity_probe_cues(n_probes=32, seed=identity_seed)

    seed_summaries = []
    source_validation = None
    for condition in conditions:
        if (
            source_validation is not None
            and not source_validation["passed"]
            and not is_source_condition(condition)
        ):
            print(f"  Skipping {condition}: source validation failed")
            continue

        print(f"  Evaluating {condition}...")
        condition_dir = output_dir / f"train_seed_{train_idx}"
        condition_summary_path = condition_dir / f"{condition}_summary.json"
        if condition_summary_path.exists() and not force:
            summary = read_json(condition_summary_path)
            print(f"    Reusing existing summary for {condition}")
            seed_summaries.append(summary)
            if condition == "source_full":
                source_validation_result = validate_source_summary(
                    summary,
                    run_cfg.get("source_validation", {}),
                )
                source_validation = {
                    "passed": source_validation_result.passed,
                    "reasons": source_validation_result.reasons,
                    "metrics": source_validation_result.metrics,
                }
                write_json(condition_dir / "source_validation.json", source_validation)
            continue

        env = Arena(cfg)
        agent = build_condition_agent(
            name=condition,
            source_agent=source_agent,
            cfg=cfg,
            env=env,
            study_id=study_id,
            master_seed=master_seed,
            train_idx=train_idx,
        )
        agent.eval()
        logs = run_condition(
            agent=agent,
            env=env,
            cfg=cfg,
            study_id=study_id,
            condition=condition,
            train_idx=train_idx,
            n_eval_episodes=n_eval_episodes,
            master_seed=master_seed,
            source_reference_agent=source_agent,
        )

        write_episode_logs_jsonl(condition_dir / f"{condition}_episodes.jsonl", logs)
        write_json(
            condition_dir / f"{condition}_episode_summaries.json",
            [summarize_episode(log) for log in logs],
        )

        summary = aggregate_episode_logs(logs)
        summary["identity_probe_accuracy"] = evaluate_identity_probe_accuracy(
            agent,
            source_agent,
            identity_cues,
        )
        summary["memory_overlap"] = evaluate_memory_overlap(agent, source_memories)
        write_json(condition_summary_path, summary)
        seed_summaries.append(summary)

        if condition == "source_full":
            source_validation_result = validate_source_summary(
                summary,
                run_cfg.get("source_validation", {}),
            )
            source_validation = {
                "passed": source_validation_result.passed,
                "reasons": source_validation_result.reasons,
                "metrics": source_validation_result.metrics,
            }
            write_json(condition_dir / "source_validation.json", source_validation)
            update_seed_manifest(
                condition_dir,
                {
                    "source_validation": source_validation,
                    "status": "evaluating" if source_validation["passed"] else "source_failed",
                },
            )
            if not source_validation["passed"]:
                print("  Source validation failed:")
                for reason in source_validation["reasons"]:
                    print(f"    {reason}")

    return seed_summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny multiseed AST benchmark smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--force", action="store_true", help="Rerun seeds even if summaries exist.")
    parser.add_argument(
        "--force-eval",
        action="store_true",
        help="Reuse source checkpoints but rerun condition evaluation and summaries.",
    )
    args = parser.parse_args()

    run_cfg = load_config(args.config)
    study_id = run_cfg["study_id"]
    master_seed = int(run_cfg["master_seed"])
    n_train_seeds = int(run_cfg["n_train_seeds"])
    n_eval_episodes = int(run_cfg["n_eval_episodes"])
    conditions = list(run_cfg["conditions"])
    output_dir = Path(run_cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    seed_records = build_seed_registry(
        study_id=study_id,
        master_seed=master_seed,
        conditions=conditions,
        n_train_seeds=n_train_seeds,
        n_eval_episodes=n_eval_episodes,
        condition_seed_aliases=run_cfg.get("condition_seed_aliases", {}),
    )
    write_seed_registry(output_dir / "seed_registry.csv", seed_records)

    manifest = {
        "study_id": study_id,
        "config": run_cfg,
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
    }
    write_json(output_dir / "manifest.json", manifest)

    all_seed_summaries = []
    training_curves = []
    for train_idx in range(n_train_seeds):
        source_seed = stable_seed(
            study_id,
            master_seed,
            "source_train_seed",
            "source",
            train_idx,
        )
        cfg = make_cfg(run_cfg, source_seed)
        print(f"Training source seed {train_idx} with seed {source_seed}...")
        seed_dir = output_dir / f"train_seed_{train_idx}"

        seed_summary_path = seed_dir / "seed_summaries.json"
        seed_manifest_path = seed_dir / "manifest.json"
        if seed_summary_path.exists() and seed_manifest_path.exists() and not args.force:
            seed_manifest = read_json(seed_manifest_path)
            if (
                not args.force_eval
                and
                seed_manifest.get("status") == "completed"
                and int(seed_manifest.get("n_condition_summaries", 0)) >= len(conditions)
            ):
                print(f"  Reusing completed seed {train_idx}")
                all_seed_summaries.extend(read_json(seed_summary_path))
                if (seed_dir / "training_curve.json").exists():
                    training_curves.append(read_json(seed_dir / "training_curve.json"))
                continue

        update_seed_manifest(
            seed_dir,
            {
                "study_id": study_id,
                "training_seed_index": train_idx,
                "source_seed": source_seed,
                "status": "training",
                "conditions": conditions,
            },
        )

        checkpoint_path = seed_dir / "source_final.pt"
        if checkpoint_path.exists() and not args.force:
            print(f"  Loading existing source checkpoint for seed {train_idx}")
            source_agent = load_source_agent(cfg, checkpoint_path)
            curve = read_json(seed_dir / "training_curve.json")
        else:
            source_agent, curve = train_source_agent(cfg, seed_dir)
        update_seed_manifest(seed_dir, {"status": "evaluating"})

        training_curves.append(curve)
        seed_summaries = evaluate_seed(
            run_cfg,
            source_agent,
            cfg,
            train_idx,
            output_dir,
            force=args.force or args.force_eval,
        )
        write_json(seed_summary_path, seed_summaries)
        source_validation = {}
        if (seed_dir / "source_validation.json").exists():
            source_validation = read_json(seed_dir / "source_validation.json")
        validation_passed = bool(source_validation.get("passed", False))
        completed = validation_passed and len(seed_summaries) >= len(conditions)
        update_seed_manifest(
            seed_dir,
            {
                "status": "completed" if completed else "source_failed",
                "n_condition_summaries": len(seed_summaries),
            },
        )
        all_seed_summaries.extend(seed_summaries)

    write_json(output_dir / "training_curves.json", training_curves)
    write_json(output_dir / "seed_summaries.json", all_seed_summaries)

    print("\nSummary")
    for summary in all_seed_summaries:
        print(
            f"seed={summary['training_seed_index']} "
            f"{summary['condition']:<24} "
            f"reward={summary['reward']:>7.2f} "
            f"self_report={summary['self_report_corr']:>6.3f} "
            f"identity={summary['identity_probe_accuracy']:>5.3f}"
        )
    print(f"\nWrote artifacts to {output_dir}")


if __name__ == "__main__":
    main()
