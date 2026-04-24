import torch
import torch.nn.functional as F


def detach_agent_state(agent):
    if getattr(agent, "schema_hidden", None) is not None:
        agent.schema_hidden = agent.schema_hidden.detach()
    if getattr(agent, "last_modulation", None) is not None:
        agent.last_modulation = agent.last_modulation.detach()


def compute_auxiliary_losses(agent_out, info, cfg):
    attn_target = agent_out.attention_weights.detach()
    report_loss = F.mse_loss(agent_out.schema.self_report, attn_target)

    tom_loss = agent_out.q_values.new_tensor(0.0)
    if info["query_other"] and info["partner_attn"] is not None:
        target = torch.tensor(info["partner_attn"], dtype=torch.float32, device=agent_out.q_values.device).unsqueeze(0)
        tom_loss = F.mse_loss(agent_out.schema.other_report, target)

    return report_loss, tom_loss


class Trainer:
    def __init__(self, agent, cfg):
        self.agent = agent
        self.target_agent = type(agent)(cfg)
        self.target_agent.load_state_dict(agent.state_dict())
        self.cfg = cfg
        self.optimizer = torch.optim.Adam(agent.parameters(), lr=cfg.lr)
        self.global_step = 0
        self.episode_rewards = []

    def get_epsilon(self):
        frac = min(1.0, self.global_step / self.cfg.eps_decay_steps)
        return self.cfg.eps_start + frac * (self.cfg.eps_end - self.cfg.eps_start)

    def get_curriculum_phase(self):
        if self.global_step < self.cfg.curriculum_phase1_steps:
            return 1
        elif self.global_step < self.cfg.curriculum_phase2_steps:
            return 2
        return 3

    def soft_update_target(self):
        for tp, p in zip(self.target_agent.parameters(), self.agent.parameters()):
            tp.data.copy_(self.cfg.target_tau * p.data + (1.0 - self.cfg.target_tau) * tp.data)

    def train_step(self, env):
        phase = self.get_curriculum_phase()
        env.set_curriculum_phase(phase)

        obs = env.reset()
        self.agent.reset_episode(batch_size=1, device=self.cfg.device)
        self.target_agent.reset_episode(batch_size=1, device=self.cfg.device)
        episode_reward = 0

        while True:
            obs_t = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            agent_out = self.agent(obs_t)
            epsilon = self.get_epsilon()
            if torch.rand(1).item() < epsilon:
                action_int = torch.randint(0, self.cfg.n_actions, (1,)).item()
            else:
                action_int = agent_out.q_values.argmax(dim=-1).item()

            result = env.step(
                action_int,
                attention_weights=agent_out.attention_weights.squeeze(0).detach().cpu().numpy(),
            )
            reward = result.reward

            if result.info["goal_found"]:
                self.agent.self_model.store_memory(
                    result.obs.flatten()[:32], reward, result.info["step"]
                )

            next_obs_t = torch.tensor(result.obs, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                target_out = self.target_agent(next_obs_t)
                next_q = target_out.q_values.max(dim=1)[0]
                target_q = torch.tensor([reward], dtype=torch.float32, device=next_q.device)
                target_q = target_q + self.cfg.gamma * next_q * (1 - float(result.done))

            chosen_q = agent_out.q_values[0, action_int].unsqueeze(0)
            td_loss = F.smooth_l1_loss(chosen_q, target_q)
            report_loss, tom_loss = compute_auxiliary_losses(agent_out, result.info, self.cfg)
            total_loss = td_loss + self.cfg.report_loss_weight * (report_loss + tom_loss)

            self.optimizer.zero_grad()
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.agent.parameters(), 1.0)
            self.optimizer.step()
            self.soft_update_target()

            detach_agent_state(self.agent)
            detach_agent_state(self.target_agent)

            episode_reward += reward
            obs = result.obs
            self.global_step += 1
            if result.done:
                break

        self.episode_rewards.append(episode_reward)
        return episode_reward

    def save_checkpoint(self, path):
        torch.save({
            "agent": self.agent.state_dict(),
            "target": self.target_agent.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "global_step": self.global_step,
            "episode_rewards": self.episode_rewards,
            "memory": self.agent.self_model.get_memory_state(),
        }, path)

    def load_checkpoint(self, path):
        ckpt = torch.load(path, weights_only=False)
        self.agent.load_state_dict(ckpt["agent"])
        self.target_agent.load_state_dict(ckpt["target"])
        self.optimizer.load_state_dict(ckpt["optimizer"])
        self.global_step = ckpt["global_step"]
        self.episode_rewards = ckpt["episode_rewards"]
        if "memory" in ckpt:
            self.agent.self_model.load_memory_state(ckpt["memory"])
