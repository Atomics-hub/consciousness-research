import torch
import numpy as np
import sys
from pathlib import Path

# Add existing IIT code to path
IIT_DIR = Path(__file__).parent.parent.parent / "iit_phi"
sys.path.insert(0, str(IIT_DIR))


def extract_activations(agent, env, cfg, module_name="attention", n_steps=None):
    """Run agent and record activations from a specific module.

    Args:
        agent: trained agent
        env: Arena
        cfg: Config
        module_name: which module to record from ('attention' conv layers)
        n_steps: number of steps to record
    Returns:
        activations: (n_steps, n_neurons) numpy array
    """
    n_steps = n_steps or cfg.phi_n_steps
    env.set_curriculum_phase(3)
    obs = env.reset(seed=cfg.seed + 77777)
    agent.reset_episode(batch_size=1, device=cfg.device)

    activations = []
    hook_output = {}

    def hook_fn(module, input, output):
        if isinstance(output, tuple):
            hook_output["act"] = output[0].detach()
        else:
            hook_output["act"] = output.detach()

    # Hook into the second conv layer of the attention mechanism
    target = agent.attention
    if hasattr(target, 'conv2'):
        handle = target.conv2.register_forward_hook(hook_fn)
    elif hasattr(target, 'attn_proj'):
        handle = target.attn_proj.register_forward_hook(hook_fn)
    else:
        raise ValueError(f"Cannot find suitable layer to hook in {module_name}")

    for step in range(n_steps):
        obs_t = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
        action, out = agent.select_action(obs_t, epsilon=0.0)
        result = env.step(
            action.item(),
            attention_weights=out.attention_weights.squeeze(0).detach().cpu().numpy(),
        )

        if "act" in hook_output:
            act = hook_output["act"].squeeze(0)
            # Flatten spatial dims, take first N neurons
            flat = act.view(-1).numpy()
            activations.append(flat[:cfg.phi_n_nodes * 4])  # oversample, then select top-N

        obs = result.obs
        if result.done:
            obs = env.reset(seed=cfg.seed + 77777 + step)
            agent.reset_episode(batch_size=1, device=cfg.device)

    handle.remove()
    return np.array(activations)


def select_top_nodes(activations, n_nodes):
    """Select the n_nodes most variable neurons (likely most informative for Phi)."""
    variances = np.var(activations, axis=0)
    top_indices = np.argsort(variances)[-n_nodes:]
    return activations[:, top_indices], top_indices


def binarize(activations):
    """Binarize activations: above median = 1, below = 0."""
    medians = np.median(activations, axis=0)
    return (activations > medians).astype(int)


def compute_empirical_tpm(binary_states, return_counts=False):
    """Compute transition probability matrix from observed binary state sequences.

    Args:
        binary_states: (n_steps, n_nodes) binary array
    Returns:
        tpm: (2^n_nodes, n_nodes) state-by-node TPM
    """
    n_nodes = binary_states.shape[1]
    n_states = 2 ** n_nodes

    # Count transitions
    tpm = np.zeros((n_states, n_nodes))
    counts = np.zeros(n_states)

    for t in range(len(binary_states) - 1):
        current = binary_states[t]
        next_state = binary_states[t + 1]
        state_idx = sum(current[i] * (2 ** i) for i in range(n_nodes))
        tpm[state_idx] += next_state
        counts[state_idx] += 1

    # Normalize
    for s in range(n_states):
        if counts[s] > 0:
            tpm[s] /= counts[s]
        else:
            tpm[s] = 0.5  # uniform prior for unvisited states

    if return_counts:
        return tpm, counts
    return tpm


def compute_agent_phi(agent, env, cfg):
    """Full pipeline: extract activations -> select nodes -> binarize -> compute Phi.

    Returns:
        phi_value: float
        details: dict with intermediate results
    """
    activations = extract_activations(agent, env, cfg)
    selected, indices = select_top_nodes(activations, cfg.phi_n_nodes)
    binary = binarize(selected)
    tpm, counts = compute_empirical_tpm(binary, return_counts=True)

    # Approximate Phi* (Barrett & Seth 2011). This is intentionally not a
    # validated IIT 3.0/4.0 cause-effect structure calculation.
    phi_value = approximate_phi_star(binary)
    method_used = "approximate_phi_star"

    return phi_value, {
        "n_nodes": cfg.phi_n_nodes,
        "n_steps": len(activations),
        "node_indices": indices.tolist(),
        "tpm_shape": tpm.shape,
        "state_coverage": float(np.count_nonzero(counts) / len(counts)),
        "method_used": method_used,
    }


def approximate_phi_star(binary_states):
    """Phi* approximation (Barrett & Seth 2011).

    Measures the difference between the mutual information of the whole system
    and the sum of mutual informations of the minimum information partition.
    Uses a geometric mean normalization.
    """
    n_nodes = binary_states.shape[1]
    if n_nodes < 2:
        return 0.0

    # Whole-system mutual information: I(past; future)
    mi_whole = _time_delayed_mutual_info(binary_states)

    # Find minimum information partition (try all bipartitions for small n)
    min_mi_sum = float('inf')
    for mask in range(1, 2 ** n_nodes - 1):
        part_a = [i for i in range(n_nodes) if mask & (1 << i)]
        part_b = [i for i in range(n_nodes) if not (mask & (1 << i))]
        if not part_a or not part_b:
            continue

        mi_a = _time_delayed_mutual_info(binary_states[:, part_a])
        mi_b = _time_delayed_mutual_info(binary_states[:, part_b])

        # Normalize by partition size (geometric mean)
        norm = min(len(part_a), len(part_b))
        mi_sum = (mi_a + mi_b) / max(norm, 1)
        min_mi_sum = min(min_mi_sum, mi_sum)

    phi_star = max(0, mi_whole / max(n_nodes, 1) - min_mi_sum)
    return phi_star


def _time_delayed_mutual_info(binary_states):
    """Compute mutual information between t and t+1 states."""
    n = len(binary_states) - 1
    if n < 10:
        return 0.0

    n_nodes = binary_states.shape[1]
    n_states = min(2 ** n_nodes, 256)  # cap for tractability

    past = binary_states[:-1]
    future = binary_states[1:]

    def state_index(row):
        return sum(row[i] * (2 ** i) for i in range(len(row)))

    past_idx = np.array([state_index(past[t]) for t in range(n)])
    future_idx = np.array([state_index(future[t]) for t in range(n)])

    # Joint distribution
    joint = np.zeros((n_states, n_states))
    for t in range(n):
        pi, fi = int(past_idx[t]) % n_states, int(future_idx[t]) % n_states
        joint[pi, fi] += 1
    joint /= n

    # Marginals
    p_past = joint.sum(axis=1)
    p_future = joint.sum(axis=0)

    # MI
    mi = 0.0
    for i in range(n_states):
        for j in range(n_states):
            if joint[i, j] > 1e-10 and p_past[i] > 1e-10 and p_future[j] > 1e-10:
                mi += joint[i, j] * np.log2(joint[i, j] / (p_past[i] * p_future[j]))

    return max(0, mi)
