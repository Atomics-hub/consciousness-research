import torch
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    seed: int = 42
    device: str = "cpu"
    root: Path = Path(__file__).parent

    # Environment
    grid_size: int = 15
    obs_window: int = 7
    n_channels: int = 6  # empty, wall, goal, distractor, partner, fog
    n_goals: int = 1
    n_distractors: int = 2
    max_steps: int = 200
    query_prob: float = 0.1  # prob of self-report / ToM query per step
    distractor_salience: float = 0.8  # how strongly distractors attract attention
    goal_reward: float = 4.0  # reward for reaching a goal while properly attending to it
    goal_progress_reward: float = 0.2  # shaping reward for moving closer to the nearest goal
    distractor_hit_penalty: float = 0.75  # penalty for stepping onto a distractor
    attention_goal_reward: float = 0.6  # reward for attending to visible goals
    attention_distractor_penalty: float = 1.2  # penalty for attending to visible distractors
    attention_capture_threshold: float = 0.05  # minimum goal attention mass required to collect a goal
    unattended_goal_penalty: float = 0.3  # penalty for touching a goal without focusing it
    distractor_focus_pool: int = 8  # place distractors preferentially near goals

    # Agent
    attn_hidden: int = 16
    attn_feature_dim: int = 64
    attn_map_size: int = 49  # obs_window^2
    schema_hidden: int = 32
    modulation_dim: int = 16
    self_model_dim: int = 32
    memory_capacity: int = 256
    n_actions: int = 5  # up, down, left, right, stay

    # Training
    lr: float = 1e-4
    gamma: float = 0.99
    eps_start: float = 1.0
    eps_end: float = 0.10
    eps_decay_steps: int = 120_000
    target_tau: float = 0.005
    total_steps: int = 150_000
    curriculum_phase1_steps: int = 40_000  # basic navigation only
    curriculum_phase2_steps: int = 100_000  # add distractors
    # phase 3: full task (distractors + partner queries)
    report_loss_weight: float = 0.3

    # Transplant
    finetune_steps: int = 10_000
    transformer_heads: int = 2
    transformer_dim: int = 16

    # Evaluation
    eval_episodes: int = 100
    phi_n_nodes: int = 8
    phi_n_steps: int = 1000

    # Paths
    @property
    def checkpoint_dir(self):
        d = self.root / "checkpoints"
        d.mkdir(exist_ok=True)
        return d

    @property
    def results_dir(self):
        d = self.root / "results"
        d.mkdir(exist_ok=True)
        return d

    @property
    def figures_dir(self):
        d = self.root / "figures"
        d.mkdir(exist_ok=True)
        return d


def set_seed(seed: int):
    import random
    import numpy as np
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
