#!/usr/bin/env python3
"""Phase 4: exploratory Phi-star side analysis in full vs ablated agents."""

import sys
import json
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ast_preservation.config import Config, set_seed
from ast_preservation.env.arena import Arena
from ast_preservation.agent.full_agent import FullAgent
from ast_preservation.agent.ablated import make_ablated_agent
from ast_preservation.evaluation.phi_bridge import compute_agent_phi


def main():
    cfg = Config()
    set_seed(cfg.seed)

    print("=" * 60)
    print("PHASE 4: Exploratory Phi-star Side Analysis")
    print(f"  Nodes: {cfg.phi_n_nodes}")
    print(f"  Steps for TPM: {cfg.phi_n_steps}")
    print("=" * 60)

    env = Arena(cfg)

    # Load trained agent
    ckpt_path = cfg.checkpoint_dir / "final_agent.pt"
    if not ckpt_path.exists():
        ckpt_path = cfg.checkpoint_dir / "best_agent.pt"

    agent = FullAgent(cfg)
    ckpt = torch.load(ckpt_path, weights_only=False)
    agent.load_state_dict(ckpt["agent"])

    conditions = {
        "full": agent,
        "schema_ablated": make_ablated_agent(agent, "schema", env, cfg),
    }

    results = {}

    for name, cond_agent in conditions.items():
        print(f"\nComputing Phi for: {name}")
        phi_val, details = compute_agent_phi(cond_agent, env, cfg)
        results[name] = {
            "phi": phi_val,
            "details": details,
        }
        print(f"  Phi-star proxy = {phi_val:.4f}")
        print(f"  Visited-state coverage: {details['state_coverage']:.2%}")

    # Exploratory comparison
    phi_full = results["full"]["phi"]
    phi_ablated = results["schema_ablated"]["phi"]

    print("\n" + "=" * 60)
    print("PHI-STAR SIDE ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Full agent Phi-star:          {phi_full:.4f}")
    print(f"Schema-ablated Phi-star:      {phi_ablated:.4f}")
    print(f"Difference:              {phi_full - phi_ablated:.4f}")

    min_coverage = min(results["full"]["details"]["state_coverage"],
                       results["schema_ablated"]["details"]["state_coverage"])

    if max(abs(phi_full), abs(phi_ablated)) < 1e-6:
        print("\n→ Both conditions are at or near zero Phi-star.")
        print("  The side analysis is inconclusive at this scale.")
        if min_coverage < 0.5:
            print("  The empirical TPM is also sparsely sampled, so treat this as exploratory only.")
    elif min_coverage < 0.5:
        print("\n→ Visited-state coverage is low.")
        print("  Treat the Phi-star side analysis as exploratory only; the empirical TPM is sparsely sampled.")
    elif phi_ablated >= phi_full * 0.9:
        print("\n→ Schema-ablated agent has comparable or higher Phi-star.")
        print("  This would motivate a more rigorous IIT-oriented follow-up.")
    else:
        print("\n→ Full agent has substantially higher Phi-star.")
        print("  This would motivate a more rigorous IIT-oriented follow-up.")

    with open(cfg.results_dir / "iit_contrast.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {cfg.results_dir / 'iit_contrast.json'}")


if __name__ == "__main__":
    main()
