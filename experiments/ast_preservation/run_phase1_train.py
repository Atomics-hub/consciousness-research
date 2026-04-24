#!/usr/bin/env python3
"""Phase 1: Train the full agent with attention, schema, and self-model."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ast_preservation.config import Config, set_seed
from ast_preservation.env.arena import Arena
from ast_preservation.agent.full_agent import FullAgent
from ast_preservation.training.trainer import Trainer


def main():
    cfg = Config()
    set_seed(cfg.seed)

    print("=" * 60)
    print("PHASE 1: Training Full Agent")
    print(f"  Total steps: {cfg.total_steps}")
    print(f"  Curriculum: nav({cfg.curriculum_phase1_steps}) → distractors({cfg.curriculum_phase2_steps}) → full")
    print("=" * 60)

    env = Arena(cfg)
    agent = FullAgent(cfg)
    trainer = Trainer(agent, cfg)

    param_count = sum(p.numel() for p in agent.parameters())
    print(f"Agent parameters: {param_count:,}")

    log_interval = 100
    best_reward = float('-inf')
    episode = 0

    while trainer.global_step < cfg.total_steps:
        ep_reward = trainer.train_step(env)
        episode += 1

        if episode % log_interval == 0:
            recent = trainer.episode_rewards[-log_interval:]
            mean_r = sum(recent) / len(recent)
            phase = trainer.get_curriculum_phase()
            eps = trainer.get_epsilon()
            print(f"  Episode {episode:5d} | Step {trainer.global_step:7d} | "
                  f"Phase {phase} | ε={eps:.3f} | Mean reward: {mean_r:.2f}")

            if mean_r > best_reward:
                best_reward = mean_r
                trainer.save_checkpoint(cfg.checkpoint_dir / "best_agent.pt")

    trainer.save_checkpoint(cfg.checkpoint_dir / "final_agent.pt")

    # Save training curve
    curve = {
        "episode_rewards": trainer.episode_rewards,
        "total_steps": trainer.global_step,
        "total_episodes": episode,
    }
    with open(cfg.results_dir / "training_curve.json", "w") as f:
        json.dump(curve, f)

    print(f"\nTraining complete. {episode} episodes, {trainer.global_step} steps.")
    print(f"Best mean reward: {best_reward:.2f}")
    print(f"Checkpoints saved to {cfg.checkpoint_dir}")


if __name__ == "__main__":
    main()
