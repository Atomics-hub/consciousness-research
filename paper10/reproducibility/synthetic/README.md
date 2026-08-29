# G0-D intervention-coverage barrier

This directory contains a theorem-guided synthetic falsification gate. It is
not neural evidence and does not measure consciousness.

The gate asks whether a finite behavioral or causal test battery can support a
uniform causal-equivalence claim over a continuous intervention domain. It
separates three logically different outcomes:

1. an empirical counterexample, which falsifies the declared equivalence;
2. a distributional estimate, which applies only to an explicit intervention
   distribution; and
3. a worst-case certificate, which additionally requires sound structural or
   regularity-and-coverage assumptions.

`frozen_spec.json` was written before the synthetic outcomes were generated.
`intervention_coverage.py` implements the deterministic fixtures and writes
`g0d_result.json`. `test_intervention_coverage.py` checks the core invariants.

Run:

```bash
python3 intervention_coverage.py
python3 -m unittest -v test_intervention_coverage.py
```

Passing this gate supports only the constructibility of the proposed claim
audit. It does not make the underlying optimal-recovery, realization,
simulation-relation, or neural-network-verification mathematics novel.
