import torch
import torch.nn as nn
import torch.nn.functional as F


class AttentionMechanism(nn.Module):
    """Spatial attention over the observation window.

    Produces a soft attention map and attended feature vector.
    Optionally accepts a top-down modulation signal from the schema.
    """

    def __init__(self, n_channels, obs_window, hidden_dim, feature_dim, modulation_dim):
        super().__init__()
        self.obs_window = obs_window
        self.map_size = obs_window * obs_window
        self.hidden_dim = hidden_dim

        self.conv1 = nn.Conv2d(n_channels, hidden_dim, 3, padding=1)
        self.conv2 = nn.Conv2d(hidden_dim, hidden_dim, 3, padding=1)
        self.flatten_dim = hidden_dim * obs_window * obs_window

        self.attn_head = nn.Linear(self.flatten_dim + modulation_dim, self.map_size)
        self.feature_head = nn.Linear(hidden_dim, feature_dim)

    def forward(self, obs, modulation=None):
        """
        Args:
            obs: (batch, n_channels, H, W)
            modulation: (batch, modulation_dim) or None
        Returns:
            attention_weights: (batch, map_size), softmax over spatial positions
            attended_features: (batch, feature_dim)
        """
        x = F.relu(self.conv1(obs))
        x = F.relu(self.conv2(x))
        flat = x.view(x.size(0), -1)  # (batch, hidden*H*W)

        if modulation is not None:
            attn_input = torch.cat([flat, modulation], dim=-1)
        else:
            attn_input = torch.cat([flat, torch.zeros(flat.size(0), self.attn_head.in_features - flat.size(1), device=flat.device)], dim=-1)

        attention_weights = F.softmax(self.attn_head(attn_input), dim=-1)  # (batch, map_size)

        # True weighted pooling: reduce over space so the attended path is an information bottleneck.
        spatial = x.view(x.size(0), self.hidden_dim, self.map_size)  # (batch, hidden, H*W)
        pooled = (spatial * attention_weights.unsqueeze(1)).sum(dim=-1)  # (batch, hidden)
        attended_features = self.feature_head(pooled)  # (batch, feature_dim)

        return attention_weights, attended_features
