#!/usr/bin/env python3
"""Phase 2: Ablation tests. Remove each component and measure behavioral deficits."""

import sys
import json
import numpy as np
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ast_preservation.config import Config, set_seed
from ast_preservation.env.arena import Arena
from ast_preservation.agent.full_agent import FullAgent
from ast_preservation.agent.ablated import make_ablated_agent
from ast_preservation.evaluation.behavioral import BehavioralEvaluator
from ast_preservation.evaluation.butlin_indicators import evaluate_butlin_indicators
from ast_preservation.evaluation.stats import compare_conditions, format_results_table


def main():
    cfg = Config()
    set_seed(cfg.seed)

    print("=" * 60)
    print("PHASE 2: Ablation Tests")
    print(f"  Eval episodes per condition: {cfg.eval_episodes}")
    print("=" * 60)

    env = Arena(cfg)

    # Load trained agent
    ckpt_path = cfg.checkpoint_dir / "final_agent.pt"
    if not ckpt_path.exists():
        ckpt_path = cfg.checkpoint_dir / "best_agent.pt"
    print(f"Loading agent from {ckpt_path}")

    agent = FullAgent(cfg)
    ckpt = torch.load(ckpt_path, weights_only=False)
    agent.load_state_dict(ckpt["agent"])
    if "memory" in ckpt:
        agent.self_model.load_memory_state(ckpt["memory"])

    evaluator = BehavioralEvaluator(cfg)
    conditions = {
        "full": agent,
        "schema_ablated": make_ablated_agent(agent, "schema", env, cfg),
        "attention_ablated": make_ablated_agent(agent, "attention", env, cfg),
        "self_model_ablated": make_ablated_agent(agent, "self_model", env, cfg),
    }

    all_results = {}
    all_metrics = {}  # keep raw ConditionMetrics for stats
    all_butlin = {}

    for name, cond_agent in conditions.items():
        print(f"\nEvaluating: {name}")
        metrics = evaluator.evaluate(cond_agent, env)
        all_metrics[name] = metrics
        all_results[name] = {
            "mean_reward": metrics.mean_reward,
            "mean_goals_found": metrics.mean_goals_found,
            "mean_steps": metrics.mean_steps,
            "distractor_suppression_rate": metrics.distractor_suppression_rate,
            "mean_self_report_corr": metrics.mean_self_report_corr,
            "mean_other_report_corr": metrics.mean_other_report_corr,
        }
        print(f"  Reward: {metrics.mean_reward:.2f}")
        print(f"  Goals: {metrics.mean_goals_found:.2f}")
        print(f"  Distractor suppression: {metrics.distractor_suppression_rate:.3f}")
        print(f"  Self-report corr: {metrics.mean_self_report_corr:.3f}")
        print(f"  ToM corr: {metrics.mean_other_report_corr:.3f}")

        butlin = evaluate_butlin_indicators(cond_agent, env, cfg, condition_name=name)
        all_butlin[name] = butlin
        present = sum(v == 1.0 for v in butlin.values())
        partial = sum(v == 0.5 for v in butlin.values())
        print(f"  Exploratory indicators: {present} present, {partial} partial")

    # Statistical comparisons
    print("\n" + "=" * 60)
    print("STATISTICAL TESTS (Wilcoxon signed-rank, Bonferroni-corrected)")
    print("=" * 60)
    all_stat_results = []
    for metric_name in ["reward", "self_report_corr", "goals_found", "distractor_captures"]:
        results = compare_conditions(all_metrics, metric_name)
        all_stat_results.extend(results)
    print(format_results_table(all_stat_results))

    # Save results
    with open(cfg.results_dir / "ablation_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    with open(cfg.results_dir / "butlin_indicators.json", "w") as f:
        json.dump(all_butlin, f, indent=2)

    stat_data = [{"metric": r.metric, "a": r.condition_a, "b": r.condition_b,
                  "mean_a": float(r.mean_a), "mean_b": float(r.mean_b), "d": float(r.effect_size),
                  "p": float(r.p_value) if not np.isnan(r.p_value) else None,
                  "sig": bool(r.significant)} for r in all_stat_results]
    with open(cfg.results_dir / "ablation_stats.json", "w") as f:
        json.dump(stat_data, f, indent=2)

    # Print comparison table
    print("\n" + "=" * 60)
    print("ABLATION SUMMARY")
    print("=" * 60)
    header = f"{'Condition':<22} {'Reward':>8} {'Goals':>6} {'Distr.Supp':>10} {'Self-Rpt':>9} {'ToM':>6}"
    print(header)
    print("-" * len(header))
    for name, r in all_results.items():
        print(f"{name:<22} {r['mean_reward']:>8.2f} {r['mean_goals_found']:>6.2f} "
              f"{r['distractor_suppression_rate']:>10.3f} {r['mean_self_report_corr']:>9.3f} "
              f"{r['mean_other_report_corr']:>6.3f}")

    print("\nResults saved to", cfg.results_dir)


if __name__ == "__main__":
    main()
