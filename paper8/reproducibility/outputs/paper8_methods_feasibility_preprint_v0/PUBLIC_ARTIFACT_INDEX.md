# Public artifact index

## Evidence classes

The public reproducibility archive contains four separately labeled evidence
layers:

| Path | Evidence role | Empirical authority |
|---|---|---|
| `zero_call/` | Deterministic construction and seeded synthetic planning | No provider observations |
| `outputs/paper8_stage1_release_v0/` | Sealed Stage 1 construction wrapper and amendment diagnostics | No provider observations |
| `outputs/paper8_stage10_claude_cli_observation_v0/` | Sanitized route observation | Exploratory, nonauthenticating |
| `outputs/paper8_stage11_ws01_sonnet_feasibility_v0/` | Sanitized one-trajectory feasibility record | Exploratory, nonconfirmatory |
| `outputs/paper8_methods_feasibility_preprint_v0/` | Publication overlay, claim ledger, metadata, and verifiers | No causal result |
| `binding_calibration/frozen_prompt_catalog.json` | Exact frozen message catalog used by Stage 11 | Material identity only |

Construction checks, simulations, and provider observations must not be pooled
as though they have the same inferential status.

## Exclusions

The archive intentionally excludes:

- credentials, authentication state, provider account metadata, and environment
  values;
- raw provider envelopes, request identifiers, session identifiers, and raw
  runtime paths;
- quarantined transcripts and historical subscription-runtime records;
- active action proposals, external-action receipts, and mutable runner state;
- caches, bytecode, symlinks, sockets, devices, and other nonregular files.

The Stage 10 and Stage 11 releases contain sanitized, bounded records. The raw
Stage 11 session record remains unpublished; only its SHA-256 commitment appears
in the sanitized result.

## Verification

From the extracted archive root, run:

```bash
/opt/homebrew/bin/python3.14 -I -B -S \
  outputs/paper8_stage10_claude_cli_observation_v0/verify_stage10.py
/opt/homebrew/bin/python3.14 -I -B -S \
  outputs/paper8_stage11_ws01_sonnet_feasibility_v0/verify_stage11.py
/opt/homebrew/bin/python3.14 -I -B -S \
  outputs/paper8_methods_feasibility_preprint_v0/verify_preprint.py
```

The full Stage 1 verifier additionally requires the documented Python 3.14.3
and NumPy 2.4.2 reference environment and performs a long deterministic replay.

Verifier success establishes local byte and construction consistency. It does
not create a confirmatory observation or causal effect estimate.
