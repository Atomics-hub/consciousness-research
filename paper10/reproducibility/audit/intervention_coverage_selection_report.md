# Paper 10 G0-D Report — The Intervention-Coverage Barrier

**Author and accountable operator:** Thomas Ryan  
**AI role:** research assistance only; not an author  
**Date:** 27 August 2026  
**Decision:** GO to a bounded methods/theory Paper 10; no consciousness claim

## Result

The frozen synthetic gate passed every declared falsifier. A battery of 64
stateful intervention trajectories generated 512 tested state–input pairs. A
continuous piecewise-linear candidate was constructed that agreed with the
source exactly on all 64 trajectories yet diverged by `0.20` under one
admissible unseen intervention. Because the tested pairs left an approximate
fill distance of `0.2705` over the declared state–input domain, the sound
Lipschitz upper bound was `0.903`, far above the frozen `0.01` equivalence
threshold. The procedure therefore failed closed despite perfect test success.

At equal budget in two dimensions, an 8 × 8 regular covering had approximate
fill distance `0.07143`, compared with a median of `0.19800` across 100 frozen
random batteries. The ratio, `0.36075`, passed the frozen maximum of `0.75`.
Coverage design materially reduced worst-case uncertainty, but it did not erase
the distinction between empirical testing and certification.

All controls behaved as declared:

- exact replacement: zero interface error;
- output-unobservable hidden mismatch: zero interface error;
- unreachable mismatch: zero error on the declared reachable experiment;
- wrong interface: `0.10` error;
- stable non-normal recurrence: `16.384×` amplification of the local impulse;
- equivalent linear realizations: maximum Markov error `8.33e-17`; and
- a finite-horizon linear sham matched eight Markov parameters before differing
  at index eight.

Five deterministic tests passed. These are process and constructibility checks,
not independent scientific replication.

## Mathematical claim boundary

The paper may prove three bounded statements while crediting their ingredients
as inherited mathematics:

1. **Finite-battery indistinguishability.** For every finite set of point
   interventions in a continuous domain, a continuous piecewise-linear—and
   therefore finite-ReLU-representable—difference can be zero on the battery
   and nonzero elsewhere.
2. **Tight fill-distance audit.** If the discrepancy function has a sound
   global Lipschitz constant `K`, then its unseen supremum is at most the maximum
   tested discrepancy plus `K` times the battery fill distance. A
   distance-to-set witness attains the residual term, making the bound minimax
   tight for that information class.
3. **Recurrent transport condition.** A local discrepancy bound transports over
   a finite horizon only inside a domain containing both source and candidate
   reachable trajectories, with amplification controlled by an incremental
   simulation/Lipschitz factor.

The individual tools are not new. The Paper 10 contribution is their operational
use to prevent three claims from being collapsed in neural replacement and
brain-emulation work: falsification by a finite battery, distributional
validation, and worst-case certification.

## Hostile prior-art judgment

The positive finite-basis theorem was killed because it collided with linear
realization, approximate simulation, symbolic reachability, neural-network
verification, and optimal recovery. The narrower claim-audit framework survives
the targeted scan:

- Linssen and Koene propose standardized functional tests for whole-brain
  emulation fidelity, but do not provide a coverage certificate separating a
  passed battery from a uniform guarantee (`10.55613/jeet.v35i1.152`).
- The *State of Brain Emulation Report 2025* makes empirical fidelity a central
  goal and proposes benchmark families, while emphasizing incomplete functional
  coverage (`10.5281/zenodo.18377594`).
- A 2026 behavioral-reconstruction framework validates models on novel
  perturbations and acknowledges that test strength depends on perturbation
  richness, but does not turn finite held-out success into a worst-case
  certificate (`10.3389/fpsyg.2026.1833113`).
- Probabilistic ReLU verification explicitly makes distributional claims, while
  exact universal verification is a different task and is computationally hard
  for broad ReLU classes (PMLR 211; PMLR 291).
- Lipschitz optimization and information-based complexity already supply the
  covering mathematics. Paper 10 must cite them as foundations, not claim their
  rediscovery.

No exact prior source was found that applies this three-level claim audit to
stateful neural replacement or whole-brain-emulation fidelity. That absence is a
bounded search result, not proof of priority.

## Selection

Paper 10 is selected as a methods/theory paper under the working title:

> **The Intervention-Coverage Barrier: Why Finite Functional Tests Cannot
> Certify Neural Replacement Fidelity**

Selection is conditional on a frozen confirmatory fixture, complete proofs,
explicit prior-art attribution, and a manuscript claim ceiling. No FlyVis
holdout or biological outcome is required for the central result.

## Claim ceiling

The work can show that finite successful tests do not by themselves certify
uniform causal fidelity over a continuous intervention domain. It cannot show
that a particular replacement is inadequate, that whole-brain emulation is
impossible, or that consciousness, identity, survival, biological
replaceability, or substrate independence is preserved or lost.
