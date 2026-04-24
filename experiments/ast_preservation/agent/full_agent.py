import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass

from .attention import AttentionMechanism
from .schema import AttentionSchema, SchemaOutput
from .self_model import SelfModel, SelfModelOutput


@dataclass
class AgentOutput:
    q_values: torch.Tensor           # (batch, n_actions)
    attention_weights: torch.Tensor  # (batch, map_size)
    attended_features: torch.Tensor  # (batch, feature_dim)
    schema: SchemaOutput
    self_model: SelfModelOutput


class FullAgent(nn.Module):
    """Complete agent with separable attention, schema, and self-model.

    Pipeline:
        observation → Attention → attention_weights, attended_features
        attention_weights → Schema → schema_state, reports, modulation
        modulation → Attention (next step, stored in self.last_modulation)
        attended_features + schema_state → SelfModel → identity, preferences
        [attended_features, schema_state, identity] → DQN head → Q-values
    """

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

        self.attention = AttentionMechanism(
            n_channels=cfg.n_channels,
            obs_window=cfg.obs_window,
            hidden_dim=cfg.attn_hidden,
            feature_dim=cfg.attn_feature_dim,
            modulation_dim=cfg.modulation_dim,
        )
        self.schema = AttentionSchema(
            map_size=cfg.attn_map_size,
            schema_hidden=cfg.schema_hidden,
            modulation_dim=cfg.modulation_dim,
        )
        self.self_model = SelfModel(
            feature_dim=cfg.attn_feature_dim,
            schema_hidden=cfg.schema_hidden,
            self_model_dim=cfg.self_model_dim,
            memory_capacity=cfg.memory_capacity,
        )

        dqn_input = cfg.attn_feature_dim + cfg.schema_hidden + cfg.self_model_dim
        self.dqn_head = nn.Sequential(
            nn.Linear(dqn_input, 64),
            nn.ReLU(),
            nn.Linear(64, cfg.n_actions),
        )

        self.schema_hidden = None
        self.last_modulation = None

    def reset_episode(self, batch_size=1, device="cpu"):
        self.schema_hidden = self.schema.initial_hidden(batch_size, device)
        self.last_modulation = torch.zeros(batch_size, self.cfg.modulation_dim, device=device)

    def forward(self, obs):
        """
        Args:
            obs: (batch, n_channels, H, W)
        Returns:
            AgentOutput
        """
        if self.schema_hidden is None:
            self.reset_episode(obs.size(0), obs.device)

        attn_weights, attn_features = self.attention(obs, self.last_modulation)

        schema_out, self.schema_hidden = self.schema(attn_weights, self.schema_hidden)
        self.last_modulation = schema_out.modulation.detach()

        sm_out = self.self_model(attn_features, schema_out.state)

        dqn_input = torch.cat([attn_features, schema_out.state, sm_out.identity], dim=-1)
        q_values = self.dqn_head(dqn_input)

        return AgentOutput(
            q_values=q_values,
            attention_weights=attn_weights,
            attended_features=attn_features,
            schema=schema_out,
            self_model=sm_out,
        )

    def select_action(self, obs, epsilon=0.0):
        with torch.no_grad():
            out = self.forward(obs)
        if torch.rand(1).item() < epsilon:
            return torch.randint(0, self.cfg.n_actions, (obs.size(0),)), out
        return out.q_values.argmax(dim=-1), out

    def get_schema_state_dict(self):
        return self.schema.state_dict()

    def get_self_model_state_dict(self):
        return {
            "weights": self.self_model.state_dict(),
            "memory": self.self_model.get_memory_state(),
        }
