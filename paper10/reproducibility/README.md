# Paper 10 reproducibility snapshot

This directory is a mechanical snapshot assembled from the frozen Paper 10
working artifacts. `synthetic/` contains the executable construction,
specifications, results, and tests. `audit/` contains decision reports and the
evidence ledger.

From this directory, run:

```bash
python3 -m unittest discover -s synthetic -p 'test_*.py' -v
python3 synthetic/intervention_coverage.py
python3 synthetic/run_confirmatory.py
```

Re-running the scripts overwrites deterministic result JSONs. It does not create
an independent experiment or a new preregistration event. SHA-256 values prove
artifact identity only. Thomas Ryan authorized the public v1.0.0 release on
29 August 2026 and remains the accountable operator.
