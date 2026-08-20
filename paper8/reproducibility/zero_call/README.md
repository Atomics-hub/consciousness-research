# Binding Test zero-call package

This directory is the local construction gate for Paper 8's refined Binding
Test. It makes no provider calls and grants no pilot authorization.

Run from the workspace root:

```bash
PYTHONPATH=.:zero_call PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s zero_call/tests -v
PYTHONPATH=.:zero_call PYTHONDONTWRITEBYTECODE=1 python3 zero_call/run_gate.py
PYTHONPATH=.:zero_call PYTHONDONTWRITEBYTECODE=1 python3 zero_call/run_redesign_gate.py --workers 4
```

Primary outputs:

- `GATE_SPEC.md` freezes gate rules before result generation.
- `item_bank_v0.json` contains 12 deterministic baseline/follow-up pairs.
- `ITEM_SEMANTIC_AUDIT.md` records the item author's structural semantic audit.
- `binding_test/` contains parsers, state machine, assignment, rendering,
  runtime binding, estimands, simulations, stress tests, and planning formulas.
- `results/gate_results.json` is the complete machine-readable result.
- `ZERO_CALL_GATE_REPORT.md` is the decision-oriented report.
- `REDESIGN_GATE_SPEC.md` freezes the identified-outcome redesign and its
  numerical-certification rules.
- `binding_test/confirmatory.py` is the final fixed-stratum inference engine;
  `binding_test/certification_planning.py` is its seeded numerical-certification
  mirror and whole-grid trust root.
- `results/redesign_gate_results.json` and `REDESIGNED_GATE_REPORT.md` are the
  redesigned machine-readable result and decision report.

The first-stage result remains `REDESIGN_BEFORE_PROVIDER_CALLS` for the latent
binary architecture. The completed redesign result is
`CONFIRMATORY_SIZE_IDENTIFIED` for the frozen +15-point observed `L/H/U`
reallocation target at B=384 active blocks per macro cell. The broad negative
headline is abandoned, and the exact provider snapshots and dollar/token
envelope remain unfrozen.

The confirmatory boundary has a hard phase firewall. Every
`ConfirmatoryDesign` and `ConfirmatoryObservation` requires `study_phase`,
`protocol_run_id`, and a lowercase SHA-256 `protocol_manifest_digest`.
Calibration-phase records, mapping schema drift, and run/digest mismatches are
rejected before confirmatory block analysis. Calibration and confirmatory runs
must use distinct bindings; calibration records are never confirmatory data.

Neither verdict authorizes a provider call, pilot, credential use, recruited
session, or spend. See `REDESIGNED_GATE_REPORT.md` before proposing any bounded
external calibration.
