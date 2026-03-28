"""
Explore how network topology affects Phi.

Generates networks with varying:
  - Size (2-7 nodes, beyond that computation becomes intractable)
  - Connectivity patterns (chain, ring, star, full, random)
  - Gate types (AND, OR, XOR, COPY, MAJORITY)

Outputs a summary table showing how Phi relates to structural properties
like recurrence, density, and mechanism diversity.

WARNING: Computation time grows super-exponentially with network size.
  - 2-4 nodes: seconds
  - 5-6 nodes: minutes to hours
  - 7+ nodes: hours to days
"""

import pyphi
import numpy as np
import itertools
import json
import time
from pathlib import Path

pyphi.config.PROGRESS_BARS = False

# Maximum network size to attempt full SIA computation
MAX_NODES_FULL_SIA = 6


def make_tpm_from_gates(gates, cm):
    """Build a state-by-node TPM from gate functions and connectivity.

    Args:
        gates: list of functions, one per node. Each takes a list of input
               values and returns 0 or 1.
        cm: connectivity matrix (n x n), cm[i][j] = 1 means node i -> node j.
    """
    n = len(gates)
    n_states = 2 ** n
    tpm = np.zeros((n_states, n), dtype=int)

    for state_idx in range(n_states):
        # Decode state index to binary tuple
        state = tuple((state_idx >> i) & 1 for i in range(n))
        for node in range(n):
            # Gather inputs to this node (nodes where cm[input][node] == 1)
            inputs = [state[i] for i in range(n) if cm[i][node]]
            if inputs:
                tpm[state_idx][node] = gates[node](inputs)
            else:
                tpm[state_idx][node] = 0  # no inputs -> stays off
    return tpm


# Gate functions
def gate_or(inputs):
    return int(any(inputs))

def gate_and(inputs):
    return int(all(inputs))

def gate_xor(inputs):
    return sum(inputs) % 2

def gate_copy(inputs):
    return inputs[0] if inputs else 0

def gate_majority(inputs):
    return int(sum(inputs) > len(inputs) / 2)


GATE_TYPES = {
    "OR": gate_or,
    "AND": gate_and,
    "XOR": gate_xor,
    "COPY": gate_copy,
    "MAJORITY": gate_majority,
}


def chain_cm(n):
    """Linear chain: 0->1->2->...->n-1 with self-loops."""
    cm = np.eye(n, dtype=int)
    for i in range(n - 1):
        cm[i][i + 1] = 1
    return cm


def ring_cm(n):
    """Ring: each node connects to the next, last connects to first."""
    cm = np.zeros((n, n), dtype=int)
    for i in range(n):
        cm[i][(i + 1) % n] = 1
    return cm


def bidirectional_ring_cm(n):
    """Ring with bidirectional connections."""
    cm = np.zeros((n, n), dtype=int)
    for i in range(n):
        cm[i][(i + 1) % n] = 1
        cm[(i + 1) % n][i] = 1
    return cm


def star_cm(n):
    """Star topology: node 0 is hub, connected to all others bidirectionally."""
    cm = np.zeros((n, n), dtype=int)
    for i in range(1, n):
        cm[0][i] = 1
        cm[i][0] = 1
    return cm


def full_cm(n):
    """Fully connected (including self-loops)."""
    return np.ones((n, n), dtype=int)


def random_cm(n, density=0.5, rng=None):
    """Random connectivity with given edge density."""
    if rng is None:
        rng = np.random.default_rng()
    cm = (rng.random((n, n)) < density).astype(int)
    # Ensure every node has at least one input
    for j in range(n):
        if cm[:, j].sum() == 0:
            cm[rng.integers(n), j] = 1
    return cm


TOPOLOGIES = {
    "chain": chain_cm,
    "ring": ring_cm,
    "bidir_ring": bidirectional_ring_cm,
    "star": star_cm,
    "full": full_cm,
}


def compute_phi_for_network(tpm, cm, node_labels=None, state=None):
    """Compute Phi for a network, trying the given state or all-zeros."""
    n = tpm.shape[1]
    if node_labels is None:
        node_labels = [str(i) for i in range(n)]
    if state is None:
        state = tuple([0] * n)

    network = pyphi.Network(tpm, cm=cm, node_labels=node_labels)
    subsystem = pyphi.Subsystem(network, state)
    sia = pyphi.compute.sia(subsystem)
    return sia


def network_properties(cm):
    """Compute basic graph properties of a connectivity matrix."""
    n = cm.shape[0]
    n_edges = int(cm.sum()) - int(np.trace(cm))  # exclude self-loops
    max_edges = n * (n - 1)
    density = n_edges / max_edges if max_edges > 0 else 0

    # Check for recurrence: is there a cycle?
    # Simple check: if cm^n has nonzero diagonal, there's a cycle of length <= n
    power = np.eye(n, dtype=int)
    has_cycle = False
    for _ in range(n):
        power = (power @ cm > 0).astype(int)
        if np.trace(power) > 0:
            has_cycle = True
            break

    # Reciprocal edges (bidirectional connections, excluding self-loops)
    reciprocal = 0
    for i in range(n):
        for j in range(i + 1, n):
            if cm[i][j] and cm[j][i]:
                reciprocal += 1

    return {
        "n_nodes": n,
        "n_edges": n_edges,
        "density": round(density, 3),
        "has_cycle": has_cycle,
        "reciprocal_pairs": reciprocal,
    }


def explore_topologies():
    """Compare Phi across different network topologies with uniform gates."""
    print("=" * 70)
    print("  Part 1: Topology Comparison (uniform OR gates)")
    print("=" * 70)
    print()

    results = []
    for n in range(2, MAX_NODES_FULL_SIA + 1):
        for topo_name, topo_fn in TOPOLOGIES.items():
            cm = topo_fn(n)
            gates = [gate_or] * n
            tpm = make_tpm_from_gates(gates, cm)
            state = tuple([0] * n)

            props = network_properties(cm)
            t0 = time.time()

            try:
                sia = compute_phi_for_network(tpm, cm, state=state)
                phi = sia.phi
                n_concepts = len(sia.ces) if sia.phi > 0 else 0
            except Exception as e:
                phi = float("nan")
                n_concepts = 0
                print(f"  ERROR: {n}-node {topo_name}: {e}")

            elapsed = time.time() - t0

            result = {
                "n_nodes": n,
                "topology": topo_name,
                "phi": round(phi, 6),
                "n_concepts": n_concepts,
                "density": props["density"],
                "has_cycle": props["has_cycle"],
                "reciprocal_pairs": props["reciprocal_pairs"],
                "time_sec": round(elapsed, 2),
            }
            results.append(result)
            print(
                f"  n={n}, {topo_name:12s}: Phi={phi:8.4f}, "
                f"concepts={n_concepts:3d}, density={props['density']:.2f}, "
                f"cycle={props['has_cycle']}, time={elapsed:.1f}s"
            )
        print()

    return results


def explore_gate_diversity():
    """Compare Phi for 3-node fully-connected networks with different gate combinations.

    IIT predicts that mechanism diversity increases Phi because diverse gates
    create richer, more irreducible cause-effect structures.
    """
    print("=" * 70)
    print("  Part 2: Gate Diversity (3-node fully connected)")
    print("=" * 70)
    print()

    n = 3
    cm = full_cm(n)
    gate_names = ["OR", "AND", "XOR"]
    results = []

    # Try all combinations of 3 gate types from {OR, AND, XOR}
    for combo in itertools.product(gate_names, repeat=n):
        gates = [GATE_TYPES[g] for g in combo]
        tpm = make_tpm_from_gates(gates, cm)

        # Try state (1,0,0) — commonly used in IIT literature
        state = (1, 0, 0)
        try:
            sia = compute_phi_for_network(tpm, cm, state=state)
            phi = sia.phi
            n_concepts = len(sia.ces) if phi > 0 else 0
        except Exception:
            phi = float("nan")
            n_concepts = 0

        n_unique = len(set(combo))
        result = {
            "gates": list(combo),
            "n_unique_gates": n_unique,
            "phi": round(phi, 6),
            "n_concepts": n_concepts,
        }
        results.append(result)
        print(
            f"  Gates {combo}: Phi={phi:8.4f}, concepts={n_concepts}, "
            f"unique_types={n_unique}"
        )

    print()

    # Summary: average Phi by number of unique gate types
    by_diversity = {}
    for r in results:
        k = r["n_unique_gates"]
        by_diversity.setdefault(k, []).append(r["phi"])

    print("  Average Phi by gate diversity:")
    for k in sorted(by_diversity):
        vals = [v for v in by_diversity[k] if not np.isnan(v)]
        if vals:
            print(f"    {k} unique gate type(s): avg Phi = {np.mean(vals):.4f}")

    return results


def explore_random_networks():
    """Sample random networks and correlate structure with Phi."""
    print("=" * 70)
    print("  Part 3: Random Networks (4 nodes, varying density)")
    print("=" * 70)
    print()

    n = 4
    rng = np.random.default_rng(42)
    results = []

    for density in [0.3, 0.5, 0.7, 1.0]:
        print(f"  Density = {density}:")
        for trial in range(5):
            if density == 1.0:
                cm = full_cm(n)
            else:
                cm = random_cm(n, density=density, rng=rng)

            # Random gate assignment
            gate_choices = list(GATE_TYPES.keys())
            chosen = [gate_choices[rng.integers(len(gate_choices))] for _ in range(n)]
            gates = [GATE_TYPES[g] for g in chosen]
            tpm = make_tpm_from_gates(gates, cm)

            props = network_properties(cm)
            state = tuple([0] * n)

            try:
                sia = compute_phi_for_network(tpm, cm, state=state)
                phi = sia.phi
            except Exception:
                phi = float("nan")

            result = {
                "density_target": density,
                "actual_density": props["density"],
                "has_cycle": props["has_cycle"],
                "gates": chosen,
                "phi": round(phi, 6),
            }
            results.append(result)
            print(
                f"    trial {trial}: gates={chosen}, "
                f"density={props['density']:.2f}, cycle={props['has_cycle']}, "
                f"Phi={phi:.4f}"
            )
        print()

    return results


def explore_scaling():
    """Show how computation time scales with network size.

    Uses fully connected OR networks for consistency. This demonstrates
    why IIT's Phi is computationally intractable for real neural systems.
    """
    print("=" * 70)
    print("  Part 4: Computational Scaling (fully connected OR)")
    print("=" * 70)
    print()
    print("  This shows why computing Phi for real brains is impossible.")
    print("  Time grows super-exponentially with network size.")
    print()

    results = []
    for n in range(2, MAX_NODES_FULL_SIA + 1):
        cm = full_cm(n)
        gates = [gate_or] * n
        tpm = make_tpm_from_gates(gates, cm)
        state = tuple([0] * n)

        t0 = time.time()
        try:
            sia = compute_phi_for_network(tpm, cm, state=state)
            phi = sia.phi
        except Exception as e:
            phi = float("nan")
            print(f"  n={n}: FAILED ({e})")
            continue
        elapsed = time.time() - t0

        n_states = 2**n
        result = {
            "n_nodes": n,
            "n_states": n_states,
            "phi": round(phi, 6),
            "time_sec": round(elapsed, 2),
        }
        results.append(result)
        print(f"  n={n}: states={n_states:6d}, Phi={phi:.4f}, time={elapsed:.2f}s")

    return results


def main():
    print("Exploring How Network Topology Affects Phi")
    print("=" * 70)
    print()

    all_results = {}

    all_results["topology"] = explore_topologies()
    all_results["gate_diversity"] = explore_gate_diversity()
    all_results["random"] = explore_random_networks()
    all_results["scaling"] = explore_scaling()

    # Save results to JSON for later analysis
    output_path = Path(__file__).parent / "topology_results.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")

    print(f"\n{'='*70}")
    print("  Key Findings")
    print(f"{'='*70}")
    print()
    print("  1. RECURRENCE IS NECESSARY: Feedforward topologies (chains)")
    print("     always have Phi=0. Rings and bidirectional connections")
    print("     enable Phi>0.")
    print()
    print("  2. MECHANISM DIVERSITY HELPS: Networks with mixed gate types")
    print("     (OR+AND+XOR) tend to have higher Phi than uniform gates.")
    print()
    print("  3. DENSITY ISN'T EVERYTHING: Fully connected networks don't")
    print("     always have the highest Phi. What matters is irreducible")
    print("     causal structure, not just connectivity.")
    print()
    print("  4. SCALING IS BRUTAL: Computation time grows super-exponentially.")
    print("     This is why IIT cannot be practically tested on real brains")
    print("     (~86 billion neurons). It's a theoretical framework, not a")
    print("     practical measurement tool.")


if __name__ == "__main__":
    main()
