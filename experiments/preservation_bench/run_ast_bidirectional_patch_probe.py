#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import platform
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = SCRIPT_DIR.parent
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ast_preservation.config import set_seed
from ast_preservation.env.arena import Arena
from run_ast_causal_patch_probe import (
    advance_source_history,
    agent_response,
    agent_response_with_attention_state_patch,
    agent_response_with_schema_state_patch,
    patch_metadata,
    response_delta,
    select_source_candidates,
)
from run_ast_checkpoint_eval import build_condition_agent, load_source_agent
from run_ast_perturbation_probe import (
    make_cfg,
    mean_abs,
    mse,
    numeric_train_seed_index,
    read_json,
    restore_recurrent,
    validated_source_seed_dirs,
    write_json,
    write_jsonl,
)


CONDITION_ORDER = [
    "source_full",
    "b_source_align_attention_copy_long",
    "b_behavior_distill",
    "b_frozen_random",
]


def load_config(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def target_donor_response(
    target_agent,
    selected: dict,
    target_context_b: dict,
    cfg,
) -> dict:
    restore_recurrent(target_agent, target_context_b["target_snapshot"])
    return agent_response(target_agent, selected["context_b"]["obs"], cfg)


def source_response_with_donor(source_agent, selected: dict, donor: dict, cfg, vector_path: str) -> dict:
    restore_recurrent(source_agent, selected["context_a"]["source_snapshot"])
    if vector_path == "schema_state":
        return agent_response_with_schema_state_patch(
            source_agent,
            selected["context_a"]["obs"],
            cfg,
            donor_schema_state=donor["schema_state"],
        )
    if vector_path == "attention_state":
        return agent_response_with_attention_state_patch(
            source_agent,
            selected["context_a"]["obs"],
            cfg,
            donor_attention=donor["attention"],
            donor_features=donor["features"],
        )
    raise ValueError("Bidirectional activation probe supports schema_state or attention_state.")


def donor_distance_to_source_b(donor: dict, source_b: dict) -> dict:
    return {
        "donor_attention_l1_to_source_b": mean_abs(donor["attention"] - source_b["attention"]),
        "donor_feature_mse_to_source_b": mse(donor["features"] - source_b["features"]),
        "donor_schema_state_mse_to_source_b": mse(
            donor["schema_state"] - source_b["schema_state"]
        ),
        "donor_q_mse_to_source_b": mse(donor["q_values"] - source_b["q_values"]),
        "donor_self_report_l1_to_source_b": mean_abs(
            donor["self_report"] - source_b["self_report"]
        ),
    }


def bidirectional_row(
    study_id: str,
    condition: str,
    train_idx: int,
    selected: dict,
    donor_response: dict,
    source_with_donor: dict,
    target_context_b_obs_match: int,
    vector_path: str,
) -> dict:
    source_a = selected["source_a"]
    source_b = selected["source_b"]
    source_cf = selected["source_cf"]

    source_delta_q = response_delta(source_cf, source_a, "q_values")
    patched_delta_q = response_delta(source_with_donor, source_a, "q_values")
    source_delta_report = response_delta(source_cf, source_a, "self_report")
    patched_delta_report = response_delta(source_with_donor, source_a, "self_report")
    source_delta_attention = response_delta(source_cf, source_a, "attention")
    patched_delta_attention = response_delta(source_with_donor, source_a, "attention")
    source_delta_schema = response_delta(source_cf, source_a, "schema_state")
    patched_delta_schema = response_delta(source_with_donor, source_a, "schema_state")

    source_action_changed = int(source_a["action"] != source_cf["action"])
    patched_action_changed = int(source_a["action"] != source_with_donor["action"])

    row = {
        "study_id": study_id,
        "condition": condition,
        "training_seed_index": int(train_idx),
        "candidate_index": int(selected["candidate_index"]),
        "source_patch_selection_rank": int(selected["source_patch_selection_rank"]),
        "source_patch_candidate_pool_size": int(
            selected["source_patch_candidate_pool_size"]
        ),
        "eval_seed_a": int(selected["seed_a"]),
        "eval_seed_b": int(selected["seed_b"]),
        "vector_path": vector_path,
        "target_context_b_obs_matches_source_context_b": int(target_context_b_obs_match),
        "source_a_action": int(source_a["action"]),
        "source_b_action": int(source_b["action"]),
        "source_cf_action": int(source_cf["action"]),
        "donor_action": int(donor_response["action"]),
        "source_with_donor_action": int(source_with_donor["action"]),
        "source_patch_action_changed": source_action_changed,
        "source_with_donor_action_changed": patched_action_changed,
        "source_with_donor_shift_match": int(patched_action_changed == source_action_changed),
        "source_with_donor_interchange_action_agreement": int(
            source_with_donor["action"] == source_cf["action"]
        ),
        "source_with_donor_source_a_action_agreement": int(
            source_with_donor["action"] == source_a["action"]
        ),
        "source_with_donor_source_b_action_agreement": int(
            source_with_donor["action"] == source_b["action"]
        ),
        "donor_action_matches_source_b_action": int(
            donor_response["action"] == source_b["action"]
        ),
        "donor_action_matches_source_cf_action": int(
            donor_response["action"] == source_cf["action"]
        ),
        "source_patch_q_delta_mse": float(selected["source_patch_q_delta_mse"]),
        "source_patch_self_report_delta_l1": float(
            selected["source_patch_self_report_delta_l1"]
        ),
        "source_patch_attention_delta_l1": float(
            selected["source_patch_attention_delta_l1"]
        ),
        "source_patch_feature_delta_mse": float(
            selected["source_patch_feature_delta_mse"]
        ),
        "source_patch_schema_state_delta_mse": float(
            selected["source_patch_schema_state_delta_mse"]
        ),
        "source_with_donor_q_delta_mse": mse(patched_delta_q),
        "source_with_donor_self_report_delta_l1": mean_abs(patched_delta_report),
        "source_with_donor_attention_delta_l1": mean_abs(patched_delta_attention),
        "source_with_donor_schema_state_delta_mse": mse(patched_delta_schema),
        "source_with_donor_delta_q_mse_to_source": mse(
            patched_delta_q - source_delta_q
        ),
        "source_with_donor_delta_self_report_l1_to_source": mean_abs(
            patched_delta_report - source_delta_report
        ),
        "source_with_donor_delta_attention_l1_to_source": mean_abs(
            patched_delta_attention - source_delta_attention
        ),
        "source_with_donor_delta_schema_state_mse_to_source": mse(
            patched_delta_schema - source_delta_schema
        ),
        "source_with_donor_q_mse_to_source_cf": mse(
            source_with_donor["q_values"] - source_cf["q_values"]
        ),
        "source_with_donor_self_report_l1_to_source_cf": mean_abs(
            source_with_donor["self_report"] - source_cf["self_report"]
        ),
        "source_with_donor_attention_l1_to_source_cf": mean_abs(
            source_with_donor["attention"] - source_cf["attention"]
        ),
    }
    row.update(donor_distance_to_source_b(donor_response, source_b))
    return row


def source_full_rows(study_id: str, train_idx: int, selected_candidates: list[dict], vector_path: str) -> list[dict]:
    rows = []
    for selected in selected_candidates:
        rows.append(
            bidirectional_row(
                study_id=study_id,
                condition="source_full",
                train_idx=train_idx,
                selected=selected,
                donor_response=selected["source_b"],
                source_with_donor=selected["source_cf"],
                target_context_b_obs_match=1,
                vector_path=vector_path,
            )
        )
    return rows


def target_condition_rows(
    study_id: str,
    master_seed: int,
    train_idx: int,
    condition: str,
    source_agent,
    target_agent,
    cfg,
    selected_candidates: list[dict],
    warmup_steps: int,
    vector_path: str,
) -> list[dict]:
    rows = []
    for selected in selected_candidates:
        target_context_b = advance_source_history(
            source_agent=source_agent,
            target_agent=target_agent,
            cfg=cfg,
            eval_seed=int(selected["seed_b"]),
            warmup_steps=warmup_steps,
        )
        obs_match = bool(np.allclose(target_context_b["obs"], selected["context_b"]["obs"]))
        donor = target_donor_response(
            target_agent=target_agent,
            selected=selected,
            target_context_b=target_context_b,
            cfg=cfg,
        )
        source_with_donor = source_response_with_donor(
            source_agent=source_agent,
            selected=selected,
            donor=donor,
            cfg=cfg,
            vector_path=vector_path,
        )
        rows.append(
            bidirectional_row(
                study_id=study_id,
                condition=condition,
                train_idx=train_idx,
                selected=selected,
                donor_response=donor,
                source_with_donor=source_with_donor,
                target_context_b_obs_match=int(obs_match),
                vector_path=vector_path,
            )
        )
    return rows


def aggregate_rows(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["condition"]].append(row)

    metric_names = sorted(
        {
            key
            for row in rows
            for key, value in row.items()
            if isinstance(value, (int, float))
            and key
            not in {
                "training_seed_index",
                "candidate_index",
                "source_patch_selection_rank",
                "source_patch_candidate_pool_size",
                "eval_seed_a",
                "eval_seed_b",
            }
        }
    )
    summaries = []
    for condition in CONDITION_ORDER:
        group = grouped.get(condition, [])
        if not group:
            continue
        summary = {
            "condition": condition,
            "n_rows": len(group),
            "n_source_seeds": len({row["training_seed_index"] for row in group}),
        }
        for metric in metric_names:
            summary[metric] = float(np.mean([row[metric] for row in group]))
        summaries.append(summary)
    return summaries


def markdown_report(manifest: dict, summaries: list[dict]) -> str:
    lines = [
        "# Paper 5 Bidirectional Patch Probe",
        "",
        "This bounded probe patches target-B activations back into source context A and compares the resulting source response with the source-B-to-source-A counterfactual. It tests whether target activations can play the source variable's causal role in the source, not only whether source activations drive the target.",
        "",
        "It does not measure consciousness, survival, personal identity, biological preservation, or AST truth.",
        "",
        "## Run",
        "",
        f"- study_id: `{manifest['study_id']}`",
        f"- vector_path: `{manifest['patch']['vector_path']}`",
        f"- source_run_dir: `{manifest['source_run_dir']}`",
        f"- selected source seeds: `{manifest['seed_status']['selected_train_seed_indices']}`",
        f"- candidate pairs per seed: `{manifest['candidate_eval_pairs']}`",
        f"- selected pairs per seed: `{manifest['selected_pairs']}`",
        "",
        "## Summary",
        "",
        "| condition | n | source flip | action agreement | shift match | q-delta error | patched-Q error | donor attention L1 | donor feature MSE |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        lines.append(
            "| {condition} | {n_rows:.0f} | {source_flip:.3f} | {action:.3f} | "
            "{shift:.3f} | {q_delta:.4f} | {patched_q:.4f} | {attn_l1:.4f} | {feat_mse:.4f} |".format(
                condition=summary["condition"],
                n_rows=summary["n_rows"],
                source_flip=summary.get("source_patch_action_changed", 0.0),
                action=summary.get(
                    "source_with_donor_interchange_action_agreement",
                    0.0,
                ),
                shift=summary.get("source_with_donor_shift_match", 0.0),
                q_delta=summary.get(
                    "source_with_donor_delta_q_mse_to_source",
                    0.0,
                ),
                patched_q=summary.get(
                    "source_with_donor_q_mse_to_source_cf",
                    0.0,
                ),
                attn_l1=summary.get("donor_attention_l1_to_source_b", 0.0),
                feat_mse=summary.get("donor_feature_mse_to_source_b", 0.0),
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a bounded target-to-source/bidirectional activation patch probe."
    )
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    run_cfg = load_config(args.config)
    study_id = run_cfg["study_id"]
    candidate_seed_study_id = run_cfg.get("candidate_seed_study_id", study_id)
    master_seed = int(run_cfg["master_seed"])
    candidate_seed_master_seed = int(run_cfg.get("candidate_seed_master_seed", master_seed))
    source_run_dir = Path(run_cfg["source_run_dir"])
    output_dir = Path(run_cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    source_manifest = read_json(source_run_dir / "manifest.json")
    source_run_cfg = copy.deepcopy(source_manifest["config"])
    source_study_id = source_run_cfg["study_id"]
    source_master_seed = int(source_run_cfg["master_seed"])
    vector_path = str(run_cfg.get("patch", {}).get("vector_path", "attention_state"))
    if vector_path not in {"schema_state", "attention_state"}:
        raise SystemExit("Bidirectional probe supports schema_state or attention_state.")
    conditions = list(run_cfg["conditions"])
    warmup_steps = int(run_cfg.get("warmup_steps", 8))
    candidate_eval_pairs = int(run_cfg.get("candidate_eval_pairs", 80))
    selected_pairs = int(run_cfg.get("selected_pairs", 8))
    max_train_seeds = run_cfg.get("max_train_seeds")
    max_train_seeds = None if max_train_seeds is None else int(max_train_seeds)

    seed_dirs = validated_source_seed_dirs(source_run_dir, max_train_seeds)
    if not seed_dirs:
        raise SystemExit(f"No validated source seeds found under {source_run_dir}")

    rows: list[dict] = []
    seed_status = {
        "source_run_dir": str(source_run_dir),
        "source_study_id": source_study_id,
        "source_master_seed": source_master_seed,
        "selected_train_seed_indices": [],
    }
    for seed_dir in seed_dirs:
        train_idx = numeric_train_seed_index(seed_dir)
        seed_manifest = read_json(seed_dir / "manifest.json")
        source_seed = int(seed_manifest["source_seed"])
        cfg = make_cfg(source_run_cfg, source_seed)
        set_seed(cfg.seed)
        source_agent = load_source_agent(cfg, seed_dir / "source_final.pt")
        seed_status["selected_train_seed_indices"].append(train_idx)

        print(f"Selecting source patch pairs for train_seed_{train_idx}...", flush=True)
        selected_candidates, _ = select_source_candidates(
            source_agent=source_agent,
            cfg=cfg,
            study_id=candidate_seed_study_id,
            master_seed=candidate_seed_master_seed,
            train_idx=train_idx,
            candidate_eval_pairs=candidate_eval_pairs,
            selected_pairs=selected_pairs,
            warmup_steps=warmup_steps,
            vector_path=vector_path,
        )
        source_flip_rate = np.mean(
            [item["source_patch_action_changed"] for item in selected_candidates]
        )
        print(
            f"Selected {len(selected_candidates)} pairs; "
            f"source_action_flip_rate={source_flip_rate:.3f}.",
            flush=True,
        )

        for condition in conditions:
            if condition == "source_full":
                print(f"Evaluating train_seed_{train_idx}/{condition}...", flush=True)
                rows.extend(
                    source_full_rows(
                        study_id=study_id,
                        train_idx=train_idx,
                        selected_candidates=selected_candidates,
                        vector_path=vector_path,
                    )
                )
                continue
            print(f"Evaluating train_seed_{train_idx}/{condition}...", flush=True)
            env = Arena(cfg)
            target_agent = build_condition_agent(
                name=condition,
                source_agent=source_agent,
                cfg=cfg,
                env=env,
                study_id=source_study_id,
                master_seed=source_master_seed,
                train_idx=train_idx,
            )
            target_agent.eval()
            rows.extend(
                target_condition_rows(
                    study_id=study_id,
                    master_seed=master_seed,
                    train_idx=train_idx,
                    condition=condition,
                    source_agent=source_agent,
                    target_agent=target_agent,
                    cfg=cfg,
                    selected_candidates=selected_candidates,
                    warmup_steps=warmup_steps,
                    vector_path=vector_path,
                )
            )

    summaries = aggregate_rows(rows)
    manifest = {
        "study_id": study_id,
        "config": run_cfg,
        "source_run_dir": str(source_run_dir),
        "candidate_seed_study_id": candidate_seed_study_id,
        "candidate_seed_master_seed": candidate_seed_master_seed,
        "seed_status": seed_status,
        "candidate_eval_pairs": candidate_eval_pairs,
        "selected_pairs": selected_pairs,
        "warmup_steps": warmup_steps,
        "conditions": conditions,
        "patch": patch_metadata(vector_path),
        "python": sys.version,
        "platform": platform.platform(),
        "metric_boundary": (
            "This bidirectional activation probe tests toy source-counterfactual "
            "functional responses. It does not measure consciousness, survival, "
            "identity, biological preservation, or AST truth."
        ),
    }
    write_json(output_dir / "manifest.json", manifest)
    write_jsonl(output_dir / "bidirectional_patch_rows.jsonl", rows)
    write_json(output_dir / "bidirectional_patch_summary.json", summaries)
    (output_dir / "bidirectional_patch_report.md").write_text(
        markdown_report(manifest, summaries),
        encoding="utf-8",
    )

    print("\nSummary")
    for summary in summaries:
        print(
            "{condition:<48} n={n_rows:.0f} source_flip={source_flip:.3f} "
            "action={action:.3f} q_delta={q_delta:.4f} donor_attn_l1={attn:.4f}".format(
                condition=summary["condition"],
                n_rows=summary["n_rows"],
                source_flip=summary.get("source_patch_action_changed", 0.0),
                action=summary.get(
                    "source_with_donor_interchange_action_agreement",
                    0.0,
                ),
                q_delta=summary.get("source_with_donor_delta_q_mse_to_source", 0.0),
                attn=summary.get("donor_attention_l1_to_source_b", 0.0),
            )
        )


if __name__ == "__main__":
    main()
