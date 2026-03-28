"""
Compute Phi for classic IIT examples.

Demonstrates why IIT claims integrated information (feedback, recurrence)
matters for consciousness, by comparing:
  1. A "photodiode" — a feedforward element with no integration
  2. A simple feedback network — minimal recurrence
  3. The classic IIT 3-node network (OR, AND, XOR gates with feedback)

The key insight: a photodiode can differentiate states (respond differently
to light vs dark) but has zero integration (Phi=0). A network with feedback
loops has Phi>0 because its parts are informationally integrated — you can't
partition it without losing cause-effect power.
"""

import pyphi
import numpy as np

pyphi.config.PROGRESS_BARS = False


def photodiode():
    """A single binary element that copies its input.

    This represents the simplest possible "detector" — like a photodiode.
    It responds to stimuli but has no integration because there's only
    one element. IIT predicts Phi=0: no consciousness.

    The TPM for a single COPY gate:
      State 0 -> stays 0 (no input)
      State 1 -> stays 1 (input present)
    """
    # Single node, deterministic self-loop (COPY gate)
    # TPM in state-by-node format: rows = current states, cols = next state prob per node
    tpm = np.array([
        [0],  # state (0,) -> node 0 turns OFF
        [1],  # state (1,) -> node 0 turns ON
    ])
    cm = np.array([[1]])  # self-loop
    network = pyphi.Network(tpm, cm=cm, node_labels=["P"])
    return network


def feedforward_chain():
    """Two nodes in a feedforward chain: A -> B (no feedback).

    A copies its own state (self-loop), B copies A.
    No recurrent connections. IIT predicts Phi=0 for the whole system
    because cutting A->B loses nothing that isn't already specified
    by A alone.

    TPM (state-by-node format, 4 states for 2 nodes):
      (A=0,B=0) -> A=0, B=0
      (A=1,B=0) -> A=1, B=1
      (A=0,B=1) -> A=0, B=0
      (A=1,B=1) -> A=1, B=1
    """
    tpm = np.array([
        [0, 0],  # (0,0) -> (0,0)
        [1, 1],  # (1,0) -> (1,1)
        [0, 0],  # (0,1) -> (0,0)
        [1, 1],  # (1,1) -> (1,1)
    ])
    cm = np.array([
        [1, 1],  # A -> A (self), A -> B
        [0, 0],  # B has no outputs
    ])
    network = pyphi.Network(tpm, cm=cm, node_labels=["A", "B"])
    return network


def feedback_pair():
    """Two nodes with mutual feedback: A <-> B.

    Both nodes are COPY gates that copy each other's previous state.
    This creates a recurrent loop — the simplest integrated system.
    IIT predicts Phi>0 because cutting the loop destroys information
    that neither part specifies alone.

    TPM:
      (0,0) -> (0,0)  both off, stay off
      (1,0) -> (0,1)  A on -> B copies A, A copies B(=0)
      (0,1) -> (1,0)  B on -> A copies B, B copies A(=0)
      (1,1) -> (1,1)  both on, stay on
    """
    tpm = np.array([
        [0, 0],  # (0,0) -> (0,0)
        [0, 1],  # (1,0) -> (0,1)
        [1, 0],  # (0,1) -> (1,0)
        [1, 1],  # (1,1) -> (1,1)
    ])
    cm = np.array([
        [0, 1],  # A -> B
        [1, 0],  # B -> A
    ])
    network = pyphi.Network(tpm, cm=cm, node_labels=["A", "B"])
    return network


def iit_classic_network():
    """The classic 3-node IIT example: OR, AND, XOR gates with full feedback.

    This is the standard example from Oizumi, Albantakis & Tononi (2014).
    Three nodes (A, B, C) are all-to-all connected:
      A = OR(B, C)   — turns on if either B or C was on
      B = AND(A, C)   — turns on only if both A and C were on
      C = XOR(A, B)   — turns on if exactly one of A, B was on

    This network has the highest Phi among 3-node systems because:
    - Full recurrence (every node feeds back to every other)
    - Diverse mechanisms (OR, AND, XOR create rich cause-effect structure)
    - High integration (can't cut it without major information loss)

    TPM in state-by-node format (8 states, 3 columns):
    State (A,B,C) -> next (A',B',C')
    """
    tpm = np.array([
        [0, 0, 0],  # (0,0,0) -> (0,0,0)
        [0, 0, 1],  # (1,0,0) -> (0,0,1)
        [1, 0, 1],  # (0,1,0) -> (1,0,1)
        [1, 0, 0],  # (1,1,0) -> (1,0,0)
        [1, 0, 1],  # (0,0,1) -> (1,0,1)
        [1, 1, 0],  # (1,0,1) -> (1,1,0)
        [1, 0, 0],  # (0,1,1) -> (1,0,0)
        [1, 1, 1],  # (1,1,1) -> (1,1,1)
    ])
    cm = np.ones((3, 3), dtype=int)  # fully connected
    network = pyphi.Network(tpm, cm=cm, node_labels=["A", "B", "C"])
    return network


def analyze_network(network, state, name):
    """Compute and display Phi and cause-effect structure for a network."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Nodes: {network.node_labels}")
    print(f"  State: {state}")
    print(f"  Connectivity matrix:\n{network.cm}")

    node_indices = tuple(range(network.size))
    subsystem = pyphi.Subsystem(network, state, node_indices)

    # Compute System Irreducibility Analysis
    sia = pyphi.compute.sia(subsystem)

    print(f"\n  Phi (big phi) = {sia.phi:.6f}")

    if sia.phi > 0:
        print(f"  MIP cut: {sia.cut}")
        print(f"  This system IS integrated — it cannot be reduced to")
        print(f"  independent parts without losing cause-effect power.")

        # Show the cause-effect structure (all concepts)
        ces = sia.ces
        print(f"\n  Cause-Effect Structure ({len(ces)} concepts):")
        for concept in ces:
            mech_labels = [network.node_labels[i] for i in concept.mechanism]
            print(f"    Mechanism {mech_labels}: phi = {concept.phi:.6f}")
    else:
        print(f"  This system has NO integration — Phi is zero.")
        print(f"  IIT predicts: no consciousness, no matter how complex")
        print(f"  the input-output behavior.")

    return sia


def main():
    print("IIT Phi Computation — Classic Examples")
    print("=" * 60)
    print()
    print("Core IIT claim: consciousness requires integrated information.")
    print("A system is conscious only if Phi > 0, meaning it cannot be")
    print("reduced to independent parts without losing causal power.")
    print("Feedforward systems always have Phi = 0.")

    # Example 1: Photodiode (Phi = 0)
    net = photodiode()
    analyze_network(net, (0,), "Photodiode (single COPY gate)")

    # Example 2: Feedforward chain (Phi = 0)
    net = feedforward_chain()
    analyze_network(net, (1, 0), "Feedforward chain A->B (no feedback)")

    # Example 3: Feedback pair (Phi > 0)
    net = feedback_pair()
    analyze_network(net, (1, 0), "Feedback pair A<->B (mutual feedback)")

    # Example 4: Classic 3-node IIT network (highest Phi for 3 nodes)
    net = iit_classic_network()
    # State (1,0,0) is commonly used in the IIT literature
    analyze_network(net, (1, 0, 0), "Classic IIT network (OR, AND, XOR) — state (1,0,0)")

    # Also compute for all-on state
    analyze_network(net, (1, 1, 1), "Classic IIT network (OR, AND, XOR) — state (1,1,1)")

    # Use PyPhi's built-in examples for comparison
    print(f"\n{'='*60}")
    print(f"  PyPhi Built-in Examples")
    print(f"{'='*60}")

    # XOR network — fully connected but all XOR gates
    # Interesting because XOR has no individual causal power (mechanisms vanish)
    xor_net = pyphi.examples.xor_network()
    state = (0, 0, 0)
    subsystem = pyphi.Subsystem(xor_net, state)
    sia = pyphi.compute.sia(subsystem)
    print(f"\n  XOR network (all XOR gates), state (0,0,0)")
    print(f"  Phi = {sia.phi:.6f}")
    print(f"  Despite full connectivity, XOR-only networks have low/zero Phi")
    print(f"  because individual XOR mechanisms are not irreducible.")

    print(f"\n{'='*60}")
    print(f"  Summary")
    print(f"{'='*60}")
    print(f"  Photodiode:        Phi = 0  (no integration possible)")
    print(f"  Feedforward chain: Phi = 0  (no recurrence)")
    print(f"  Feedback pair:     Phi > 0  (minimal integration)")
    print(f"  OR/AND/XOR net:    Phi > 0  (rich integration)")
    print(f"  XOR-only net:      Phi ~ 0  (mechanisms vanish)")
    print()
    print("Key takeaway: connectivity alone doesn't guarantee Phi > 0.")
    print("What matters is that mechanisms are IRREDUCIBLE — they specify")
    print("cause-effect repertoires that can't be decomposed.")


if __name__ == "__main__":
    main()
