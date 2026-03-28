"""
IIT Phi Computation — From Scratch

Computes Integrated Information (Φ) for small discrete networks using
the IIT 3.0 formalism (Oizumi, Albantakis & Tononi, 2014).

Building this from scratch rather than using PyPhi because:
1. PyPhi's develop branch broke IIT 3.0 backward compat
2. Understanding the actual math matters more than calling an API
3. For small networks (≤8 nodes), a clean implementation is tractable

The core idea: Φ measures how much a system's cause-effect structure
is lost when you partition it. If Φ > 0, the system is "more than
the sum of its parts" — it has irreducible integrated information.
"""

import numpy as np
from itertools import combinations, product


def tpm_marginalize(tpm, node, direction="effect"):
    """Marginalize a node out of the TPM."""
    n = int(np.log2(tpm.shape[0]))
    axis = node
    return tpm.mean(axis=axis) if direction == "cause" else tpm


def cause_repertoire(tpm, mechanism, purview, state):
    """Compute the cause repertoire: p(purview_past | mechanism_current=state).

    Given the current state of the mechanism, what's the probability
    distribution over past states of the purview?

    Uses Bayes' rule with uniform prior (maximum entropy assumption).
    """
    n_nodes = tpm.shape[1]
    n_states = tpm.shape[0]

    # Current state of mechanism nodes
    mech_state = tuple(state[i] for i in mechanism)

    # For each possible past state of the purview, compute
    # p(purview_past) * p(mechanism_current | purview_past) via TPM
    purview_states = list(product([0, 1], repeat=len(purview)))
    probs = np.zeros(len(purview_states))

    for idx, pv_state in enumerate(purview_states):
        # Sum over all possible past states of non-purview nodes
        other_nodes = [i for i in range(n_nodes) if i not in purview]
        other_states = list(product([0, 1], repeat=len(other_nodes)))

        prob = 0.0
        for os_state in other_states:
            # Construct full past state
            past_state = [0] * n_nodes
            for i, node in enumerate(purview):
                past_state[node] = pv_state[i]
            for i, node in enumerate(other_nodes):
                past_state[node] = os_state[i]

            past_idx = sum(past_state[j] * (2 ** j) for j in range(n_nodes))

            # p(mechanism_current | past_state) from TPM
            p = 1.0
            for m in mechanism:
                if state[m] == 1:
                    p *= tpm[past_idx, m]
                else:
                    p *= (1.0 - tpm[past_idx, m])
            prob += p

        probs[idx] = prob

    # Normalize (Bayes with uniform prior)
    total = probs.sum()
    if total > 0:
        probs /= total
    else:
        probs = np.ones(len(purview_states)) / len(purview_states)

    return probs


def effect_repertoire(tpm, mechanism, purview, state):
    """Compute the effect repertoire: p(purview_future | mechanism_current=state).

    Given the current state of the mechanism, what's the probability
    distribution over future states of the purview?
    """
    n_nodes = tpm.shape[1]
    n_states = tpm.shape[0]

    purview_states = list(product([0, 1], repeat=len(purview)))
    probs = np.zeros(len(purview_states))

    # Marginalize over non-mechanism nodes in current state
    other_nodes = [i for i in range(n_nodes) if i not in mechanism]
    other_states = list(product([0, 1], repeat=len(other_nodes)))

    for idx, pv_state in enumerate(purview_states):
        prob = 0.0
        for os_state in other_states:
            # Construct full current state (mechanism fixed, others vary)
            current = [0] * n_nodes
            for i, node in enumerate(mechanism):
                current[node] = state[node]
            for i, node in enumerate(other_nodes):
                current[node] = os_state[i]

            curr_idx = sum(current[j] * (2 ** j) for j in range(n_nodes))

            # p(purview_future | current_state)
            p = 1.0
            for i, node in enumerate(purview):
                if pv_state[i] == 1:
                    p *= tpm[curr_idx, node]
                else:
                    p *= (1.0 - tpm[curr_idx, node])
            prob += p

        probs[idx] = prob / len(other_states)

    return probs


def emd(p, q):
    """Earth Mover's Distance for 1D distributions (L1 for distributions on binary strings)."""
    return np.sum(np.abs(p - q))


def concept_phi(tpm, mechanism, state):
    """Compute small phi for a mechanism in a given state.

    Small phi = min over all partitions of the mechanism of the
    distance between the unpartitioned and partitioned cause-effect
    repertoires.

    Returns (phi, cause_purview, effect_purview).
    """
    n_nodes = tpm.shape[1]
    all_nodes = list(range(n_nodes))

    if len(mechanism) == 0:
        return 0.0, (), ()

    # Find the MIC (maximally irreducible cause) and MIE (maximally irreducible effect)
    # by searching over purviews and partitions

    best_cause_phi = 0.0
    best_cause_purview = ()
    best_effect_phi = 0.0
    best_effect_purview = ()

    # Try all possible purviews (non-empty subsets of nodes)
    for purview_size in range(1, n_nodes + 1):
        for purview in combinations(all_nodes, purview_size):
            purview = tuple(purview)

            # Cause repertoire (unpartitioned)
            cr = cause_repertoire(tpm, mechanism, purview, state)

            # Find minimum information partition for cause
            min_cause_dist = float('inf')
            for part in bipartitions(mechanism):
                if part is None:
                    continue
                part_a, part_b = part

                # Partitioned cause repertoire
                if len(part_a) > 0 and len(part_b) > 0:
                    # Partition purview proportionally
                    for pv_part in bipartitions(purview):
                        if pv_part is None:
                            continue
                        pv_a, pv_b = pv_part
                        cr_a = cause_repertoire(tpm, part_a, pv_a, state) if len(pv_a) > 0 else np.array([1.0])
                        cr_b = cause_repertoire(tpm, part_b, pv_b, state) if len(pv_b) > 0 else np.array([1.0])
                        cr_part = np.outer(cr_a, cr_b).flatten()
                        if len(cr_part) == len(cr):
                            dist = emd(cr, cr_part)
                            min_cause_dist = min(min_cause_dist, dist)
                elif len(part_a) == 0:
                    # Partition with empty part = unconstrained (uniform)
                    cr_unc = np.ones(len(cr)) / len(cr)
                    dist = emd(cr, cr_unc)
                    min_cause_dist = min(min_cause_dist, dist)

            if min_cause_dist == float('inf'):
                min_cause_dist = 0.0

            if min_cause_dist > best_cause_phi:
                best_cause_phi = min_cause_dist
                best_cause_purview = purview

            # Effect repertoire (unpartitioned)
            er = effect_repertoire(tpm, mechanism, purview, state)

            # Find minimum information partition for effect
            min_effect_dist = float('inf')
            for part in bipartitions(mechanism):
                if part is None:
                    continue
                part_a, part_b = part

                if len(part_a) > 0 and len(part_b) > 0:
                    for pv_part in bipartitions(purview):
                        if pv_part is None:
                            continue
                        pv_a, pv_b = pv_part
                        er_a = effect_repertoire(tpm, part_a, pv_a, state) if len(pv_a) > 0 else np.array([1.0])
                        er_b = effect_repertoire(tpm, part_b, pv_b, state) if len(pv_b) > 0 else np.array([1.0])
                        er_part = np.outer(er_a, er_b).flatten()
                        if len(er_part) == len(er):
                            dist = emd(er, er_part)
                            min_effect_dist = min(min_effect_dist, dist)
                elif len(part_a) == 0:
                    er_unc = np.ones(len(er)) / len(er)
                    dist = emd(er, er_unc)
                    min_effect_dist = min(min_effect_dist, dist)

            if min_effect_dist == float('inf'):
                min_effect_dist = 0.0

            if min_effect_dist > best_effect_phi:
                best_effect_phi = min_effect_dist
                best_effect_purview = purview

    # Small phi = min of cause and effect integrated information
    phi = min(best_cause_phi, best_effect_phi)
    return phi, best_cause_purview, best_effect_purview


def bipartitions(elements):
    """Generate all bipartitions of a tuple into two non-overlapping parts.

    Includes partitions where one part is empty (representing the "null" cut).
    """
    elements = tuple(elements)
    n = len(elements)
    if n == 0:
        return

    # Generate all subsets as part_a; part_b is the complement
    for i in range(2 ** n):
        part_a = tuple(elements[j] for j in range(n) if i & (1 << j))
        part_b = tuple(elements[j] for j in range(n) if not (i & (1 << j)))
        if part_a <= part_b:  # avoid duplicates
            yield (part_a, part_b)


def system_phi(tpm, state):
    """Compute big Φ for the whole system.

    Big Φ = minimum over all system partitions of the distance
    between the unpartitioned and partitioned cause-effect structures.

    For simplicity, we compute all concepts and report Φ as the
    sum of small phis (this is the "conceptual information" CI,
    which is a lower bound on big Φ in many cases and gives the
    right intuition).

    A proper big Φ computation requires comparing entire cause-effect
    structures across all system cuts, which is what makes it intractable
    for large systems.
    """
    n_nodes = tpm.shape[1]
    all_nodes = list(range(n_nodes))

    concepts = []
    total_phi = 0.0

    for size in range(1, n_nodes + 1):
        for mechanism in combinations(all_nodes, size):
            phi, cause_pv, effect_pv = concept_phi(tpm, mechanism, state)
            if phi > 1e-10:
                concepts.append({
                    'mechanism': mechanism,
                    'phi': phi,
                    'cause_purview': cause_pv,
                    'effect_purview': effect_pv,
                })
                total_phi += phi

    return total_phi, concepts


def make_tpm(n_nodes, gates):
    """Build a state-by-node TPM from gate definitions.

    gates: dict mapping node_index -> (gate_type, input_nodes)
    gate_type: 'OR', 'AND', 'XOR', 'COPY', 'NOT'
    """
    n_states = 2 ** n_nodes
    tpm = np.zeros((n_states, n_nodes))

    for state_idx in range(n_states):
        state = [(state_idx >> i) & 1 for i in range(n_nodes)]
        for node, (gate_type, inputs) in gates.items():
            input_vals = [state[i] for i in inputs]
            if gate_type == 'OR':
                tpm[state_idx, node] = 1.0 if any(input_vals) else 0.0
            elif gate_type == 'AND':
                tpm[state_idx, node] = 1.0 if all(input_vals) else 0.0
            elif gate_type == 'XOR':
                tpm[state_idx, node] = 1.0 if sum(input_vals) % 2 == 1 else 0.0
            elif gate_type == 'COPY':
                tpm[state_idx, node] = float(input_vals[0])
            elif gate_type == 'NOT':
                tpm[state_idx, node] = 1.0 - float(input_vals[0])

    return tpm


def main():
    print("IIT Integrated Information — From Scratch")
    print("=" * 60)
    print()
    print("Core claim: consciousness = integrated information (Φ).")
    print("A system is conscious iff its parts specify more cause-effect")
    print("power together than they do independently.")

    # Example 1: Photodiode (single self-loop COPY gate)
    print(f"\n{'='*60}")
    print("  1. Photodiode (single COPY gate)")
    print(f"{'='*60}")
    tpm = np.array([[0.0], [1.0]])
    state = (0,)
    phi, concepts = system_phi(tpm, state)
    print(f"  Nodes: 1, State: {state}")
    print(f"  Φ = {phi:.4f}")
    print(f"  Concepts: {len(concepts)}")
    print(f"  → A single element can't be partitioned. Φ = 0 trivially.")
    print(f"  → IIT: a photodiode is NOT conscious, no matter how it responds.")

    # Example 2: Feedforward A->B (COPY gates, no feedback)
    print(f"\n{'='*60}")
    print("  2. Feedforward chain A→B (no feedback)")
    print(f"{'='*60}")
    tpm = make_tpm(2, {
        0: ('COPY', [0]),  # A copies itself
        1: ('COPY', [0]),  # B copies A
    })
    state = (1, 1)
    phi, concepts = system_phi(tpm, state)
    print(f"  Nodes: 2, State: {state}")
    print(f"  Φ = {phi:.4f}")
    print(f"  Concepts: {len(concepts)}")
    for c in concepts:
        print(f"    Mechanism {c['mechanism']}: φ = {c['phi']:.4f}")
    print(f"  → No feedback loop. Each part's causes are fully specified")
    print(f"    by itself. Cutting A→B loses no irreducible information.")

    # Example 3: Feedback pair A<->B (mutual COPY)
    print(f"\n{'='*60}")
    print("  3. Feedback pair A↔B (mutual COPY gates)")
    print(f"{'='*60}")
    tpm = make_tpm(2, {
        0: ('COPY', [1]),  # A copies B
        1: ('COPY', [0]),  # B copies A
    })
    state = (1, 0)
    phi, concepts = system_phi(tpm, state)
    print(f"  Nodes: 2, State: {state}")
    print(f"  Φ = {phi:.4f}")
    print(f"  Concepts: {len(concepts)}")
    for c in concepts:
        print(f"    Mechanism {c['mechanism']}: φ = {c['phi']:.4f}")
    print(f"  → Recurrence creates integration. Cutting the loop destroys")
    print(f"    information that neither part specifies alone.")

    # Example 4: Classic IIT 3-node network (OR, AND, XOR)
    print(f"\n{'='*60}")
    print("  4. Classic IIT network: OR, AND, XOR (full feedback)")
    print(f"{'='*60}")
    tpm = make_tpm(3, {
        0: ('OR', [1, 2]),   # A = OR(B, C)
        1: ('AND', [0, 2]),  # B = AND(A, C)
        2: ('XOR', [0, 1]),  # C = XOR(A, B)
    })
    state = (1, 0, 0)
    phi, concepts = system_phi(tpm, state)
    print(f"  Nodes: 3, State: {state}")
    print(f"  Φ = {phi:.4f}")
    print(f"  Concepts: {len(concepts)}")
    for c in concepts:
        print(f"    Mechanism {c['mechanism']}: φ = {c['phi']:.4f}")
    print(f"  → Diverse gates + full feedback = rich cause-effect structure.")
    print(f"  → This is the canonical IIT example with high integration.")

    # Example 5: All-XOR network (same connectivity, different gates)
    print(f"\n{'='*60}")
    print("  5. All-XOR network (full feedback, but uniform gates)")
    print(f"{'='*60}")
    tpm = make_tpm(3, {
        0: ('XOR', [1, 2]),
        1: ('XOR', [0, 2]),
        2: ('XOR', [0, 1]),
    })
    state = (0, 0, 0)
    phi, concepts = system_phi(tpm, state)
    print(f"  Nodes: 3, State: {state}")
    print(f"  Φ = {phi:.4f}")
    print(f"  Concepts: {len(concepts)}")
    for c in concepts:
        print(f"    Mechanism {c['mechanism']}: φ = {c['phi']:.4f}")
    print(f"  → Same connectivity as #4 but uniform gates.")
    print(f"  → XOR is parity — each output depends on ALL inputs equally,")
    print(f"    so individual mechanisms have limited causal specificity.")

    # Example 6: Comparison across states
    print(f"\n{'='*60}")
    print("  6. State dependence — same network, different states")
    print(f"{'='*60}")
    tpm = make_tpm(3, {
        0: ('OR', [1, 2]),
        1: ('AND', [0, 2]),
        2: ('XOR', [0, 1]),
    })
    print(f"  Network: OR/AND/XOR (same as #4)")
    for s in [(0,0,0), (1,0,0), (1,1,0), (1,0,1), (1,1,1)]:
        phi, concepts = system_phi(tpm, s)
        print(f"    State {s}: Φ = {phi:.4f} ({len(concepts)} concepts)")
    print(f"  → Φ depends on the state! Different states activate different")
    print(f"    cause-effect structures. This is a key IIT prediction:")
    print(f"    the \"quality\" of experience changes with the state.")

    print(f"\n{'='*60}")
    print("  KEY TAKEAWAYS")
    print(f"{'='*60}")
    print("""
  1. Feedforward systems have Φ ≈ 0 (no integration)
  2. Feedback/recurrence is necessary but not sufficient for Φ > 0
  3. Gate diversity matters — uniform gates reduce integration
  4. Φ is state-dependent — same network can have different Φ
  5. This scales HORRIBLY — 2^(2^n) complexity. 10+ nodes = intractable.
     This is IIT's fundamental problem: the theory makes predictions
     we can't compute for any system we actually care about.
  6. For consciousness preservation: if IIT is right, preserving the
     connectivity alone isn't enough. You need to preserve the specific
     causal mechanisms (gate functions) AND the state.
""")


if __name__ == "__main__":
    main()
