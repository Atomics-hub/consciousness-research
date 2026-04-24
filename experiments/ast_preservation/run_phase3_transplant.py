#!/usr/bin/env python3
"""Phase 3: Transplant assay for schema and self-model transfer."""

import sys
import json
import numpy as np
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ast_preservation.config import Config, set_seed
from ast_preservation.env.arena import Arena
from ast_preservation.agent.full_agent import FullAgent
from ast_preservation.transplant.substrate_b import SubstrateBAgent
from ast_preservation.transplant.transplant import (
    create_transplant_conditions, finetune_transplanted
)
from ast_preservation.evaluation.behavioral import (
    BehavioralEvaluator,
    build_identity_probe_cues,
    evaluate_identity_probe_accuracy,
    evaluate_memory_overlap,
)
from ast_preservation.evaluation.stats import compare_conditions, format_results_table
from ast_preservation.training.trainer import Trainer


def main():
    cfg = Config()
    set_seed(cfg.seed)

    print("=" * 60)
    print("PHASE 3: Frozen Schema/Self-Model Transplant Assay")
    print(f"  Fine-tune steps: {cfg.finetune_steps}")
    print(f"  Eval episodes: {cfg.eval_episodes}")
    print("=" * 60)

    env = Arena(cfg)

    # Load trained agent (source)
    ckpt_path = cfg.checkpoint_dir / "final_agent.pt"
    if not ckpt_path.exists():
        ckpt_path = cfg.checkpoint_dir / "best_agent.pt"
    print(f"Loading source agent from {ckpt_path}")

    source_agent = FullAgent(cfg)
    ckpt = torch.load(ckpt_path, weights_only=False)
    source_agent.load_state_dict(ckpt["agent"])
    if "memory" in ckpt:
        source_agent.self_model.load_memory_state(ckpt["memory"])

    # Save source memories for overlap diagnostics and build source-specific probes.
    source_memories = source_agent.self_model.get_memory_state()
    print(f"Source agent has {len(source_memories)} episodic memories")
    identity_probe_cues = build_identity_probe_cues(n_probes=32, seed=cfg.seed + 2026)
    print(f"Prepared {len(identity_probe_cues)} self-model fingerprint probes")

    # Create transplant conditions
    print("\nCreating transplant conditions...")
    conditions = create_transplant_conditions(source_agent, cfg)

    # Also train a full-retrain control (Substrate B from scratch)
    print("\nTraining full-retrain control (Substrate B from scratch)...")
    retrain_agent = SubstrateBAgent(cfg)
    retrain_trainer = Trainer(retrain_agent, cfg)
    retrain_episodes = 0
    while retrain_trainer.global_step < cfg.total_steps:
        retrain_trainer.train_step(env)
        retrain_episodes += 1
        if retrain_episodes % 100 == 0:
            recent = retrain_trainer.episode_rewards[-100:]
            mean_r = sum(recent) / len(recent)
            print(f"  Retrain episode {retrain_episodes} | step {retrain_trainer.global_step}/{cfg.total_steps} | mean reward {mean_r:.2f}")
    conditions["full_retrain"] = retrain_agent

    # Fine-tune transplanted conditions
    for name in ["transplant", "random_control", "arch_matched"]:
        print(f"\nFine-tuning: {name}")
        ft_env = Arena(cfg)
        ft_rewards = finetune_transplanted(conditions[name], ft_env, cfg)
        mean_r = sum(ft_rewards[-10:]) / min(10, len(ft_rewards)) if ft_rewards else 0
        print(f"  Final mean reward: {mean_r:.2f}")

    # Evaluate all conditions
    evaluator = BehavioralEvaluator(cfg)
    all_results = {}
    all_metrics = {}

    for name, agent in conditions.items():
        print(f"\nEvaluating: {name}")
        metrics = evaluator.evaluate(agent, env)
        all_metrics[name] = metrics
        identity_accuracy = evaluate_identity_probe_accuracy(agent, source_agent, identity_probe_cues)
        memory_overlap = evaluate_memory_overlap(agent, source_memories)

        all_results[name] = {
            "mean_reward": metrics.mean_reward,
            "mean_goals_found": metrics.mean_goals_found,
            "mean_steps": metrics.mean_steps,
            "distractor_suppression_rate": metrics.distractor_suppression_rate,
            "mean_self_report_corr": metrics.mean_self_report_corr,
            "mean_other_report_corr": metrics.mean_other_report_corr,
            "identity_probe_accuracy": identity_accuracy,
            "memory_overlap": memory_overlap,
        }
        print(f"  Reward: {metrics.mean_reward:.2f}")
        print(f"  Self-report: {metrics.mean_self_report_corr:.3f}")
        print(f"  Identity probes: {identity_accuracy:.3f}")
        print(f"  Memory overlap (diagnostic): {memory_overlap:.3f}")

    print("\n" + "=" * 60)
    print("TRANSPLANT STATISTICAL TESTS (Wilcoxon signed-rank, Bonferroni-corrected)")
    print("=" * 60)
    all_stat_results = []
    for metric_name in ["reward", "self_report_corr", "other_report_corr", "goals_found"]:
        results = compare_conditions(all_metrics, metric_name)
        all_stat_results.extend(results)
    print(format_results_table(all_stat_results))

    # Save
    with open(cfg.results_dir / "transplant_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    stat_data = [{"metric": r.metric, "a": r.condition_a, "b": r.condition_b,
                  "mean_a": float(r.mean_a), "mean_b": float(r.mean_b), "d": float(r.effect_size),
                  "p": float(r.p_value) if not np.isnan(r.p_value) else None,
                  "sig": bool(r.significant)} for r in all_stat_results]
    with open(cfg.results_dir / "transplant_stats.json", "w") as f:
        json.dump(stat_data, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("TRANSPLANT SUMMARY")
    print("=" * 60)
    header = f"{'Condition':<18} {'Reward':>8} {'Self-Rpt':>9} {'ToM':>6} {'Ident':>7}"
    print(header)
    print("-" * len(header))
    for name, r in all_results.items():
        print(f"{name:<18} {r['mean_reward']:>8.2f} {r['mean_self_report_corr']:>9.3f} "
              f"{r['mean_other_report_corr']:>6.3f} {r['identity_probe_accuracy']:>7.3f}")


if __name__ == "__main__":
    main()
