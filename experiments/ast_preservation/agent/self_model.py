import torch
import torch.nn as nn
import hashlib
import numpy as np
from collections import deque
from dataclasses import dataclass


@dataclass
class SelfModelOutput:
    identity: torch.Tensor        # (batch, self_model_dim)
    preference: torch.Tensor      # (batch, self_model_dim // 2)


class EpisodicMemory:
    """Extractable memory buffer storing (state_hash, reward, step) tuples.
    Uses full SHA-256 hex for collision resistance."""

    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def store(self, state_repr, reward, step):
        h = hashlib.sha256(state_repr.tobytes()).hexdigest()
        self.buffer.append((h, float(reward), int(step)))

    def query(self, state_repr, k=5):
        return list(self.buffer)[-k:]

    def get_state(self):
        return list(self.buffer)

    def load_state(self, state):
        self.buffer = deque(state, maxlen=self.capacity)

    def __len__(self):
        return len(self.buffer)


class SelfModel(nn.Module):
    """Encodes identity and preferences from attended features + schema state.
    Maintains an episodic memory buffer that is extractable and transplantable."""

    def __init__(self, feature_dim, schema_hidden, self_model_dim, memory_capacity):
        super().__init__()
        input_dim = feature_dim + schema_hidden
        self.identity_net = nn.Sequential(
            nn.Linear(input_dim, self_model_dim * 2),
            nn.ReLU(),
            nn.Linear(self_model_dim * 2, self_model_dim),
        )
        self.preference_head = nn.Linear(self_model_dim, self_model_dim // 2)
        self.memory = EpisodicMemory(memory_capacity)

    def forward(self, attended_features, schema_state):
        x = torch.cat([attended_features, schema_state], dim=-1)
        identity = self.identity_net(x)
        preference = self.preference_head(identity)
        return SelfModelOutput(identity=identity, preference=preference)

    def store_memory(self, state_repr, reward, step):
        self.memory.store(state_repr, reward, step)

    def get_memory_state(self):
        return self.memory.get_state()

    def load_memory_state(self, state):
        self.memory.load_state(state)

    def identity_fingerprint(self):
        """Hash the current self-model weights plus episodic memory contents.

        This gives a source-specific fingerprint that survives transplant when
        the self-model is copied, but is not recreated by merely re-running the
        same environment.
        """
        digest = hashlib.sha256()

        for name, tensor in sorted(self.state_dict().items()):
            digest.update(name.encode("utf-8"))
            arr = tensor.detach().cpu().numpy().astype(np.float32, copy=False)
            digest.update(arr.tobytes())

        for memory_item in self.memory.get_state():
            digest.update(repr(memory_item).encode("utf-8"))

        return digest.digest()

    def answer_identity_probe(self, cue):
        """Return a deterministic source-specific answer to a fingerprint cue."""
        digest = hashlib.sha256()
        digest.update(self.identity_fingerprint())
        digest.update(str(int(cue)).encode("utf-8"))
        return digest.hexdigest()[:12]
