import torch
import torch.nn as nn
import torch.nn.functional as F

from .attention import AttentionMechanism
from .schema import AttentionSchema, SchemaOutput
from .self_model import SelfModel, SelfModelOutput
from .full_agent import FullAgent, AgentOutput


class NullSchema(nn.Module):
    """Ablated schema: outputs mean activations from training, not zeros.
    Zero modulation and uniform reports, while schema_state uses recorded mean
    so downstream modules see a realistic input distribution."""

    def __init__(self, map_size, schema_hidden, modulation_dim, mean_state=None):
        super().__init__()
        self.schema_hidden = schema_hidden
        self.map_size = map_size
        self.modulation_dim = modulation_dim
        if mean_state is not None:
            self.register_buffer("mean_state", mean_state)
        else:
            self.register_buffer("mean_state", torch.zeros(schema_hidden))

    def initial_hidden(self, batch_size, device):
        return torch.zeros(1, batch_size, self.schema_hidden, device=device)

    def forward(self, attention_weights, hidden):
        batch = attention_weights.size(0)
        device = attention_weights.device
        uniform = torch.ones(batch, self.map_size, device=device) / self.map_size
        state = self.mean_state.unsqueeze(0).expand(batch, -1)
        return SchemaOutput(
            state=state,
            self_report=uniform,
            other_report=uniform,
            modulation=torch.zeros(batch, self.modulation_dim, device=device),
        ), hidden


class NullAttention(nn.Module):
    """Ablated attention: uniform attention over a true pooled feature bottleneck."""

    def __init__(self, original_attention):
        super().__init__()
        import copy
        self.map_size = original_attention.map_size
        self.obs_window = original_attention.obs_window
        self.hidden_dim = original_attention.hidden_dim
        self.conv1 = copy.deepcopy(original_attention.conv1)
        self.conv2 = copy.deepcopy(original_attention.conv2)
        self.feature_head = copy.deepcopy(original_attention.feature_head)
        for p in self.parameters():
            p.requires_grad = False

    def forward(self, obs, modulation=None):
        batch = obs.size(0)
        device = obs.device
        uniform = torch.ones(batch, self.map_size, device=device) / self.map_size
        # Preserve the original pooled readout, but force a uniform spatial policy.
        with torch.no_grad():
            x = F.relu(self.conv1(obs))
            x = F.relu(self.conv2(x))
            spatial = x.view(x.size(0), self.hidden_dim, self.map_size)
            pooled = (spatial * uniform.unsqueeze(1)).sum(dim=-1)
            features = self.feature_head(pooled)
        return uniform, features


class NullSelfModel(nn.Module):
    """Ablated self-model: uses mean identity from training, no memory."""

    def __init__(self, self_model_dim, mean_identity=None):
        super().__init__()
        self.self_model_dim = self_model_dim
        if mean_identity is not None:
            self.register_buffer("mean_identity", mean_identity)
        else:
            self.register_buffer("mean_identity", torch.zeros(self_model_dim))

    def forward(self, attended_features, schema_state):
        batch = attended_features.size(0)
        device = attended_features.device
        identity = self.mean_identity.unsqueeze(0).expand(batch, -1)
        return SelfModelOutput(
            identity=identity,
            preference=torch.zeros(batch, self.self_model_dim // 2, device=device),
        )

    def store_memory(self, *args): pass
    def get_memory_state(self): return []
    def load_memory_state(self, state): pass


def _collect_mean_activations(agent, env, cfg, n_episodes=20):
    """Run agent for a few episodes and collect mean schema_state and identity."""
    env.set_curriculum_phase(3)
    schema_states = []
    identity_states = []

    for ep in range(n_episodes):
        obs = env.reset(seed=cfg.seed + 50000 + ep)
        agent.reset_episode(batch_size=1, device=cfg.device)
        for step in range(min(50, cfg.max_steps)):
            obs_t = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                out = agent(obs_t)
            schema_states.append(out.schema.state.squeeze(0))
            identity_states.append(out.self_model.identity.squeeze(0))
            result = env.step(
                out.q_values.argmax(dim=-1).item(),
                attention_weights=out.attention_weights.squeeze(0).detach().cpu().numpy(),
            )
            obs = result.obs
            if result.done:
                break

    mean_schema = torch.stack(schema_states).mean(dim=0)
    mean_identity = torch.stack(identity_states).mean(dim=0)
    return mean_schema, mean_identity


def make_ablated_agent(full_agent, ablation_type, env=None, cfg=None):
    """Create an ablated copy of a trained agent.

    Args:
        full_agent: trained FullAgent
        ablation_type: 'schema', 'attention', or 'self_model'
        env: Arena instance (needed to collect mean activations)
        cfg: Config instance
    Returns:
        FullAgent with one module replaced by its null version
    """
    from .full_agent import FullAgent as FA
    agent_cfg = full_agent.cfg
    agent = FA(agent_cfg)
    agent.load_state_dict(full_agent.state_dict())
    agent.self_model.load_memory_state(full_agent.self_model.get_memory_state())

    # Collect mean activations for fairer ablation
    mean_schema = None
    mean_identity = None
    if env is not None and cfg is not None:
        mean_schema, mean_identity = _collect_mean_activations(full_agent, env, cfg)

    if ablation_type == "schema":
        agent.schema = NullSchema(
            agent_cfg.attn_map_size, agent_cfg.schema_hidden,
            agent_cfg.modulation_dim, mean_state=mean_schema,
        )
    elif ablation_type == "attention":
        agent.attention = NullAttention(full_agent.attention)
    elif ablation_type == "self_model":
        agent.self_model = NullSelfModel(agent_cfg.self_model_dim, mean_identity=mean_identity)
    else:
        raise ValueError(f"Unknown ablation type: {ablation_type}")

    return agent
