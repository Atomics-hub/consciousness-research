import torch
import torch.nn as nn
import torch.nn.functional as F
import math

from ..agent.schema import AttentionSchema, SchemaOutput
from ..agent.self_model import SelfModel, SelfModelOutput
from ..agent.full_agent import AgentOutput


class TransformerAttention(nn.Module):
    """Transformer-based spatial attention, architecturally distinct from conv-based.

    Splits the observation into patches, applies multi-head self-attention,
    and computes spatial attention weights with a learned readout over outputs.
    """

    def __init__(self, n_channels, obs_window, n_heads, dim, feature_dim, modulation_dim):
        super().__init__()
        self.obs_window = obs_window
        self.map_size = obs_window * obs_window
        self.n_heads = n_heads
        self.dim = dim
        self.head_dim = dim // n_heads

        self.patch_embed = nn.Linear(n_channels, dim)
        self.pos_embed = nn.Parameter(torch.randn(1, self.map_size, dim) * 0.02)

        self.qkv = nn.Linear(dim, 3 * dim)
        self.attn_proj = nn.Linear(dim, dim)

        self.modulation_proj = nn.Linear(modulation_dim, dim)
        self.feature_head = nn.Linear(dim, feature_dim)
        self.attn_readout = nn.Linear(dim, 1)

    def forward(self, obs, modulation=None):
        """
        Args:
            obs: (batch, n_channels, H, W)
            modulation: (batch, modulation_dim) or None
        Returns:
            attention_weights: (batch, map_size)
            attended_features: (batch, feature_dim)
        """
        batch = obs.size(0)
        # Flatten spatial dims to patches: (batch, H*W, n_channels)
        patches = obs.view(batch, obs.size(1), -1).permute(0, 2, 1)  # (batch, map_size, n_channels)
        x = self.patch_embed(patches) + self.pos_embed  # (batch, map_size, dim)

        # Add modulation as bias
        if modulation is not None:
            mod = self.modulation_proj(modulation).unsqueeze(1)  # (batch, 1, dim)
            x = x + mod

        # Multi-head self-attention
        qkv = self.qkv(x).reshape(batch, self.map_size, 3, self.n_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # (3, batch, heads, map_size, head_dim)
        q, k, v = qkv[0], qkv[1], qkv[2]

        scale = math.sqrt(self.head_dim)
        attn_scores = (q @ k.transpose(-2, -1)) / scale  # (batch, heads, map_size, map_size)
        attn_probs = F.softmax(attn_scores, dim=-1)

        out = (attn_probs @ v).transpose(1, 2).reshape(batch, self.map_size, self.dim)
        out = self.attn_proj(out)  # (batch, map_size, dim)

        # Spatial attention weights from readout
        spatial_logits = self.attn_readout(out).squeeze(-1)  # (batch, map_size)
        attention_weights = F.softmax(spatial_logits, dim=-1)

        # Attended features via weighted mean pooling
        weighted = (out * attention_weights.unsqueeze(-1)).sum(dim=1)  # (batch, dim)
        attended_features = self.feature_head(weighted)  # (batch, feature_dim)

        return attention_weights, attended_features


class SubstrateBAgent(nn.Module):
    """Agent with transformer-based attention but transplanted schema + self-model.

    The interface adapters translate between Substrate B's attention representation
    and the schema/self-model that were trained on Substrate A.
    """

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

        self.attention = TransformerAttention(
            n_channels=cfg.n_channels,
            obs_window=cfg.obs_window,
            n_heads=cfg.transformer_heads,
            dim=cfg.transformer_dim,
            feature_dim=cfg.attn_feature_dim,
            modulation_dim=cfg.modulation_dim,
        )

        # Interface adapters (trainable during fine-tuning)
        self.schema_adapter = nn.Linear(cfg.attn_map_size, cfg.attn_map_size)
        self.feature_adapter = nn.Linear(cfg.attn_feature_dim, cfg.attn_feature_dim)

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
        if self.schema_hidden is None:
            self.reset_episode(obs.size(0), obs.device)

        attn_weights, attn_features = self.attention(obs, self.last_modulation)

        # Adapt representations for transplanted schema/self-model
        adapted_attn = self.schema_adapter(attn_weights)
        adapted_attn = F.softmax(adapted_attn, dim=-1)
        adapted_features = self.feature_adapter(attn_features)

        schema_out, self.schema_hidden = self.schema(adapted_attn, self.schema_hidden)
        self.last_modulation = schema_out.modulation.detach()

        sm_out = self.self_model(adapted_features, schema_out.state)

        dqn_input = torch.cat([adapted_features, schema_out.state, sm_out.identity], dim=-1)
        q_values = self.dqn_head(dqn_input)

        return AgentOutput(
            q_values=q_values,
            attention_weights=attn_weights,
            attended_features=adapted_features,
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
