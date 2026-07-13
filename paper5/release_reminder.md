# Paper 5 Release-Readiness Record

Target release-readiness review date: Tuesday, June 23, 2026.

This file records the internal readiness gate used before the Paper 5 preprint and release snapshot.

Update on 2026-06-25: Zenodo record published at https://doi.org/10.5281/zenodo.20852042. The `paper5-v1.0.0` GitHub release snapshot is the supplementary code/results record referenced by Zenodo.

## Review Question

Does the current Paper 5 package prove a bounded causal-preservation result clearly enough that a careful reader can reproduce the evidence and understand the claim ceiling?

## Public Release Gate

- Rerun citation/reference audit if references changed.
- Recheck figure and table numbering if result presentation changed.
- Manuscript read-through for overclaiming.
- Rerun PDF/render check if the manuscript changed.
- Explicit Tom approval for any public posting, Zenodo deposition, or GitHub release.

Current local verification after the bidirectional update: PDF render, figure/table presence, row counts, JSON loads, Python compile checks, ASCII scan, and stale-language scan have passed. These checks must be rerun if the result presentation changes again.

## Current Evidence To Preserve

- Schema-state full panel: copied attention exceeds behavior distillation and frozen random under action-mismatch causal intervention.
- Attention-state full panel: copied attention strongly tracks source counterfactuals while behavior distillation does not.
- Behavior-matched subsets: behavior distillation can match ordinary source-A action while still failing the intervention.
- Donor-action-mismatch follow-up: copied attention retains a counterfactual Q-geometry advantage under source-counterfactual/donor-action decoupling, while its action-label advantage is modest and explicitly limited.
- Bidirectional target-to-source follow-up: copied-attention target-B attention state can substitute back into source-A with 0.938 source-counterfactual action agreement, versus 0.210 for behavior distillation and 0.199 for frozen random.
