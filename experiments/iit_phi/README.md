# IIT Phi Computation with PyPhi

## What is PyPhi?

PyPhi is a Python library for computing Integrated Information (Phi), the central
quantity of Integrated Information Theory (IIT). IIT, developed by Giulio Tononi,
proposes that consciousness corresponds to a system's capacity to integrate
information — quantified by Phi.

**Key paper:** Mayner et al. (2018), "PyPhi: A toolbox for integrated information
theory," PLOS Computational Biology 14(7): e1006343.

**Repository:** https://github.com/wmayner/pyphi

## Core Concepts

- **Network**: A system of binary elements with a defined transition probability
  matrix (TPM) and connectivity matrix (CM).
- **Subsystem**: A subset of network nodes in a particular state.
- **Mechanism**: A subset of nodes within a subsystem whose causal power is analyzed.
- **Cause-Effect Structure (CES)**: The full set of irreducible cause-effect
  repertoires (concepts) specified by a subsystem.
- **Phi (big phi)**: The irreducibility of the cause-effect structure. A system with
  high Phi cannot be reduced to independent parts without losing information.
- **System Irreducibility Analysis (SIA)**: Finds the minimum information partition
  (MIP) — the "weakest link" cut that least damages the cause-effect structure.

## Computational Limits

PyPhi's computation scales super-exponentially with system size. The number of
partitions to evaluate grows as the Bell number. Practical limits:

- **~8-10 nodes**: Full SIA computation feasible (minutes to hours)
- **~12-15 nodes**: Possible with approximations or parallel computation
- **>15 nodes**: Intractable for exact Phi computation

This is a fundamental limitation of IIT, not just PyPhi. Alternatives like GeoMIP
(165-326x speedup) exist but don't solve the underlying exponential scaling.

## Installation

```bash
pip install pyphi
```

Requires Python 3.12+. Key dependencies: numpy, scipy, joblib, graphillion.

## Usage

```python
import pyphi
import numpy as np

# Create a network from a TPM and connectivity matrix
tpm = np.array([[...]])  # 2^n rows, n columns (state-by-node format)
cm = np.array([[...]])   # n x n adjacency matrix
network = pyphi.Network(tpm, cm=cm)

# Create a subsystem (nodes in a particular state)
state = (1, 0, 0)
subsystem = pyphi.Subsystem(network, state)

# Compute Phi
sia = pyphi.compute.sia(subsystem)
print(f"Phi = {sia.phi}")
print(f"MIP cut: {sia.cut}")
```

## Scripts

- `compute_phi.py` — Classic IIT examples: photodiode vs integrated network, demonstrating why feedback/integration matters.
- `explore_network_topologies.py` — Systematic exploration of how network structure affects Phi.

## References

- Tononi G (2004). An information integration theory of consciousness. BMC Neuroscience.
- Oizumi M, Albantakis L, Tononi G (2014). From the phenomenology to the mechanisms of consciousness: IIT 3.0. PLoS Comp Bio.
- Albantakis L et al. (2023). Integrated Information Theory (IIT) 4.0. arXiv.
