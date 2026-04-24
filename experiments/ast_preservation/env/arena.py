import numpy as np
from dataclasses import dataclass

CH_EMPTY = 0
CH_WALL = 1
CH_GOAL = 2
CH_DISTRACTOR = 3
CH_PARTNER = 4
CH_FOG = 5

ACTIONS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1), 4: (0, 0)}  # up, down, left, right, stay


@dataclass
class StepResult:
    obs: np.ndarray              # (n_channels, obs_window, obs_window)
    reward: float
    done: bool
    info: dict                   # goal_found, query_self, query_other, partner_attn, agent_pos, goal_pos


class PartnerAgent:
    """Goal-directed partner with epsilon-greedy noise.
    Navigates toward a randomly placed target with stochastic steps,
    making its attention non-trivially predictable (not just memorizable)."""

    def __init__(self, grid_size, epsilon=0.3, seed=0):
        self.grid_size = grid_size
        self.epsilon = epsilon
        self.rng = np.random.RandomState(seed)
        self.pos = None
        self.target = None
        self.attention = np.zeros(grid_size * grid_size)

    def reset(self):
        interior = [(r, c) for r in range(1, self.grid_size - 1)
                     for c in range(1, self.grid_size - 1)]
        self.pos = interior[self.rng.randint(len(interior))]
        self.target = interior[self.rng.randint(len(interior))]
        self.attention[:] = 0

    def step(self):
        # Epsilon-greedy: move toward target or random
        if self.rng.random() < self.epsilon:
            dr, dc = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)][self.rng.randint(5)]
        else:
            r, c = self.pos
            tr, tc = self.target
            dr = np.sign(tr - r)
            dc = np.sign(tc - c) if dr == 0 else 0

        nr = np.clip(self.pos[0] + dr, 1, self.grid_size - 2)
        nc = np.clip(self.pos[1] + dc, 1, self.grid_size - 2)
        self.pos = (int(nr), int(nc))

        # Attention is toward target, not just at position
        self.attention[:] = 0
        tr, tc = self.target
        self.attention[tr * self.grid_size + tc] = 0.7
        self.attention[self.pos[0] * self.grid_size + self.pos[1]] = 0.3

        # Re-pick target when reached
        if self.pos == self.target:
            interior = [(r, c) for r in range(1, self.grid_size - 1)
                         for c in range(1, self.grid_size - 1)]
            self.target = interior[self.rng.randint(len(interior))]

        return self.pos


class Arena:
    def __init__(self, cfg):
        self.cfg = cfg
        self.gs = cfg.grid_size
        self.ow = cfg.obs_window
        self.nc = cfg.n_channels
        self.rng = np.random.RandomState(cfg.seed)
        self.partner = PartnerAgent(self.gs, epsilon=0.3, seed=cfg.seed + 777)
        self.curriculum_phase = 1  # 1=nav only, 2=+distractors, 3=full

        self.grid = None
        self.agent_pos = None
        self.partner_pos = None
        self.goal_positions = []
        self.distractor_positions = []
        self.step_count = 0
        self.goals_found = 0

    def _visible_mass(self, obs, channel_idx, attention_weights):
        if attention_weights is None:
            return 0.0
        mask = (obs[channel_idx].reshape(-1) > 0).astype(np.float32)
        if mask.sum() == 0:
            return 0.0
        attn = np.asarray(attention_weights, dtype=np.float32).reshape(-1)
        if attn.shape[0] != self.ow * self.ow:
            return 0.0
        return float(np.dot(attn, mask))

    def _nearest_goal_distance(self, pos):
        if not self.goal_positions:
            return 0
        return min(abs(pos[0] - gr) + abs(pos[1] - gc) for gr, gc in self.goal_positions)

    def set_curriculum_phase(self, phase):
        self.curriculum_phase = min(max(phase, 1), 3)

    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.RandomState(seed)
            self.partner.rng = np.random.RandomState(seed + 777)
        self.grid = np.zeros((self.nc, self.gs, self.gs), dtype=np.float32)
        self.step_count = 0
        self.goals_found = 0

        # Walls on border
        self.grid[CH_WALL, 0, :] = 1
        self.grid[CH_WALL, -1, :] = 1
        self.grid[CH_WALL, :, 0] = 1
        self.grid[CH_WALL, :, -1] = 1

        interior = [(r, c) for r in range(1, self.gs - 1) for c in range(1, self.gs - 1)]
        self.rng.shuffle(interior)
        idx = 0

        self.agent_pos = interior[idx]; idx += 1

        # Goals
        self.goal_positions = []
        for _ in range(self.cfg.n_goals):
            pos = interior[idx]; idx += 1
            self.goal_positions.append(pos)
            self.grid[CH_GOAL, pos[0], pos[1]] = 1.0

        # Distractors (only in phase 2+)
        self.distractor_positions = []
        if self.curriculum_phase >= 2:
            remaining = interior[idx:]
            ranked = sorted(
                remaining,
                key=lambda pos: min(abs(pos[0] - gr) + abs(pos[1] - gc) for gr, gc in self.goal_positions),
            )
            focus_pool = ranked[:max(self.cfg.distractor_focus_pool, self.cfg.n_distractors)]
            self.rng.shuffle(focus_pool)
            chosen = focus_pool[:self.cfg.n_distractors]
            for pos in chosen:
                self.distractor_positions.append(pos)
                self.grid[CH_DISTRACTOR, pos[0], pos[1]] = self.cfg.distractor_salience

        # Partner (only active in phase 3)
        self.partner.reset()
        self.partner_pos = self.partner.pos if self.curriculum_phase >= 3 else None

        # Fog everywhere except agent's current view
        self.grid[CH_FOG, :, :] = 1.0
        self._reveal_around(self.agent_pos)

        return self._get_obs()

    def _reveal_around(self, pos):
        r, c = pos
        hw = self.ow // 2
        r0, r1 = max(0, r - hw), min(self.gs, r + hw + 1)
        c0, c1 = max(0, c - hw), min(self.gs, c + hw + 1)
        self.grid[CH_FOG, r0:r1, c0:c1] = 0.0

    def _get_obs(self):
        r, c = self.agent_pos
        hw = self.ow // 2
        obs = np.zeros((self.nc, self.ow, self.ow), dtype=np.float32)
        for dr in range(-hw, hw + 1):
            for dc in range(-hw, hw + 1):
                gr, gc = r + dr, c + dc
                oi, oj = dr + hw, dc + hw
                if 0 <= gr < self.gs and 0 <= gc < self.gs:
                    obs[:, oi, oj] = self.grid[:, gr, gc]
                else:
                    obs[CH_WALL, oi, oj] = 1.0
        # Mark partner in obs if visible
        if self.partner_pos is not None:
            pr, pc = self.partner_pos
            dr, dc = pr - r, pc - c
            if abs(dr) <= hw and abs(dc) <= hw:
                obs[CH_PARTNER, dr + hw, dc + hw] = 1.0
        return obs

    def step(self, action, attention_weights=None):
        self.step_count += 1
        reward = -0.1  # time penalty
        prev_obs = self._get_obs()
        prev_goal_dist = self._nearest_goal_distance(self.agent_pos)

        goal_attention_mass = self._visible_mass(prev_obs, CH_GOAL, attention_weights)
        distractor_attention_mass = self._visible_mass(prev_obs, CH_DISTRACTOR, attention_weights)
        reward += self.cfg.attention_goal_reward * goal_attention_mass
        reward -= self.cfg.attention_distractor_penalty * distractor_attention_mass

        # Move agent
        dr, dc = ACTIONS[action]
        nr, nc_ = self.agent_pos[0] + dr, self.agent_pos[1] + dc
        if 0 <= nr < self.gs and 0 <= nc_ < self.gs and self.grid[CH_WALL, nr, nc_] == 0:
            self.agent_pos = (nr, nc_)
            self._reveal_around(self.agent_pos)

        new_goal_dist = self._nearest_goal_distance(self.agent_pos)
        reward += self.cfg.goal_progress_reward * float(prev_goal_dist - new_goal_dist)

        # Check goal
        goal_found = False
        for i, gp in enumerate(self.goal_positions):
            if self.agent_pos == gp:
                if goal_attention_mass >= self.cfg.attention_capture_threshold:
                    reward += self.cfg.goal_reward
                    goal_found = True
                    self.goals_found += 1
                    self.grid[CH_GOAL, gp[0], gp[1]] = 0.0
                    self.goal_positions[i] = None
                else:
                    reward -= self.cfg.unattended_goal_penalty
        self.goal_positions = [g for g in self.goal_positions if g is not None]

        # Check distractor capture (agent stepped onto distractor)
        for dp in self.distractor_positions:
            if self.agent_pos == dp:
                reward -= self.cfg.distractor_hit_penalty
                break

        # Move partner
        if self.curriculum_phase >= 3:
            self.partner_pos = self.partner.step()
            if self.partner_pos:
                self.grid[CH_PARTNER, :, :] = 0.0
                self.grid[CH_PARTNER, self.partner_pos[0], self.partner_pos[1]] = 1.0

        # Query probes
        query_self = False
        query_other = False
        if self.curriculum_phase >= 3 and self.rng.random() < self.cfg.query_prob:
            if self.rng.random() < 0.5:
                query_self = True
            else:
                query_other = True

        done = (len(self.goal_positions) == 0) or (self.step_count >= self.cfg.max_steps)

        # Partner attention as ground truth for ToM
        partner_attn = None
        if self.curriculum_phase >= 3:
            partner_attn = self._get_partner_attention_local()

        obs = self._get_obs()

        info = {
            "goal_found": goal_found,
            "query_self": query_self,
            "query_other": query_other,
            "partner_attn": partner_attn,
            "agent_pos": self.agent_pos,
            "goal_positions": list(self.goal_positions),
            "step": self.step_count,
            "goal_attention_mass": goal_attention_mass,
            "distractor_attention_mass": distractor_attention_mass,
            "goal_capture_threshold": self.cfg.attention_capture_threshold,
        }

        return StepResult(obs=obs, reward=reward, done=done, info=info)

    def _get_partner_attention_local(self):
        """Partner's attention (toward its target + position) projected onto agent's local window."""
        attn = np.zeros(self.ow * self.ow, dtype=np.float32)
        if self.partner_pos is None:
            return attn
        r, c = self.agent_pos
        hw = self.ow // 2

        # Map partner's global attention to agent's local window
        for gi in range(self.gs):
            for gj in range(self.gs):
                global_idx = gi * self.gs + gj
                val = self.partner.attention[global_idx]
                if val > 0:
                    dr, dc = gi - r, gj - c
                    if abs(dr) <= hw and abs(dc) <= hw:
                        local_idx = (dr + hw) * self.ow + (dc + hw)
                        attn[local_idx] = val

        # Normalize to sum to 1 if any attention is visible
        total = attn.sum()
        if total > 0:
            attn /= total
        return attn

    def get_goal_direction(self):
        """Returns a one-hot-ish vector pointing toward nearest goal (for shaping)."""
        if not self.goal_positions:
            return np.zeros(4, dtype=np.float32)
        r, c = self.agent_pos
        dists = [(abs(gr - r) + abs(gc - c), gr, gc) for gr, gc in self.goal_positions]
        _, gr, gc = min(dists)
        direction = np.zeros(4, dtype=np.float32)
        if gr < r: direction[0] = 1  # up
        if gr > r: direction[1] = 1  # down
        if gc < c: direction[2] = 1  # left
        if gc > c: direction[3] = 1  # right
        return direction
