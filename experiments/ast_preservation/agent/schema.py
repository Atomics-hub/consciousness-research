import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass


@dataclass
class SchemaOutput:
    state: torch.Tensor          # (batch, schema_hidden)
    self_report: torch.Tensor    # (batch, map_size)
    other_report: torch.Tensor   # (batch, map_size)
    modulation: torch.Tensor     # (batch, modulation_dim)


class AttentionSchema(nn.Module):
    """AST-style meta-model of attention used in the transplant assay.

    Takes the current attention weights as input, maintains a temporal model
    via GRU, and produces:
    - self_report: predicted own attention distribution
    - other_report: predicted partner's attention (theory of mind)
    - modulation: top-down bias fed back into attention control
    """

    def __init__(self, map_size, schema_hidden, modulation_dim):
        super().__init__()
        self.schema_hidden = schema_hidden

        self.input_proj = nn.Linear(map_size, schema_hidden)
        self.gru = nn.GRU(schema_hidden, schema_hidden, batch_first=True)
        self.state_proj = nn.Linear(schema_hidden, schema_hidden)

        self.self_report_head = nn.Linear(schema_hidden, map_size)
        self.other_report_head = nn.Linear(schema_hidden, map_size)
        self.modulation_head = nn.Linear(schema_hidden, modulation_dim)

    def initial_hidden(self, batch_size, device):
        return torch.zeros(1, batch_size, self.schema_hidden, device=device)

    def forward(self, attention_weights, hidden):
        """
        Args:
            attention_weights: (batch, map_size)
            hidden: (1, batch, schema_hidden), GRU hidden state
        Returns:
            SchemaOutput, new_hidden
        """
        x = F.relu(self.input_proj(attention_weights))  # (batch, schema_hidden)
        x = x.unsqueeze(1)  # (batch, 1, schema_hidden)
        gru_out, new_hidden = self.gru(x, hidden)  # gru_out: (batch, 1, schema_hidden)
        state = self.state_proj(gru_out.squeeze(1))  # (batch, schema_hidden)

        self_report = F.softmax(self.self_report_head(state), dim=-1)
        other_report = F.softmax(self.other_report_head(state), dim=-1)
        modulation = self.modulation_head(state)

        return SchemaOutput(
            state=state,
            self_report=self_report,
            other_report=other_report,
            modulation=modulation,
        ), new_hidden
