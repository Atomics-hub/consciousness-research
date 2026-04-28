#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from benchmark.seeds import build_seed_registry, write_seed_registry


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a PreservationBench seed registry.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.config.open() as f:
        cfg = json.load(f)

    records = build_seed_registry(
        study_id=cfg["study_id"],
        master_seed=int(cfg["master_seed"]),
        conditions=list(cfg["conditions"]),
        n_train_seeds=int(cfg["n_train_seeds"]),
        n_eval_episodes=int(cfg["n_eval_episodes"]),
        source_train_seed_override=cfg.get("checkpoint_source_seed"),
        condition_seed_aliases=cfg.get("condition_seed_aliases", {}),
    )
    write_seed_registry(args.output, records)
    print(f"Wrote {len(records)} seed records to {args.output}")


if __name__ == "__main__":
    main()
