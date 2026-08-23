# Reproducibility Manifest

## Frozen source

- Repository: `https://github.com/TuragaLab/flyvis`
- Commit/version: `92b3845cc426dd309a1a0e1b3890156c42e14021` / `flyvis 1.2`
- Environment: Python 3.12, PyTorch 2.13 CPU
- Executed source checkout: project-local `work/flyvis-source` (not redistributed)
- Executed environment: project-local `work/flyvis-venv` (not redistributed)
- Public derived results: `paper9/results/`

The pretrained archive was 3,417,042 bytes and checksum-verified during acquisition. Redistribution must follow upstream licensing and model-artifact terms.

## Primary scripts

| Stage | Script |
|---|---|
| Source ensemble/margins | `paper9/code/d1b_source_ensemble.py` |
| Local calibration | `paper9/code/d1b_local_calibration.py` |
| Global holdout/replication | `paper9/code/d1b_global_holdout.py` |
| Causal replication/solver | `paper9/code/d1b_causal_replication.py` |
| Source causal scale | `paper9/code/d1c_source_effect_scale.py` |
| Matched calibration | `paper9/code/d1c_matched_calibration.py` |
| Tables and figures | `paper9/build_artifacts.py` |

## Primary results and SHA-256

| Artifact | SHA-256 |
|---|---|
| D1B source ensemble | `bf75b64246b03d74a0e2a4d4c95d5814acc1b890d07914ab943498973647d8b4` |
| D1B local calibration | `e6cc59d71a575a506887f98049d7bf7c54edb11f40be079a90078269fb68c5b2` |
| Checkpoint 008 global | `3fb0c10d5b87ecad9611b8dacb391a0c6e329b2b06ff215b3fcb2371c3b275ea` |
| Checkpoint 009 global | `e0eacb7d4ba5bd62ba46bcabbf973632b48e1abd8d2cb300f9f047277b1f66ac` |
| CP008 causal `.02` | `c82943c693812a9caa7381bf95a014100c5bf72e3d6ffbd4bb927d91057c5e15` |
| CP008 causal `.01` | `a432f2301aef88265b41882b8f0eb77df36ecdc407c051bd1f4786f65a8cb1bd` |
| CP009 causal `.02` | `f8d3b13077b2267848dd3f662f9b5f57435101027a825951407162e6e7159bfe` |
| CP009 causal `.01` | `6fa0ff3a30cdbe0971987c83d80f314d8bd46e92ee4d812fcac3b40feb2baa12` |
| D1C source effect scale | `788d37daeb958c67744ab0521859e9d32000bf8ed8345ce559d9d3bc27df0fa4` |
| D1C failed matching gate | `e995351ba010651bac055127d13ca16be074dfc615cc9e8ac8d979d698b27268` |

Hashes are integrity checks, not independent replication.

## Rebuild commands

From the project root:

```bash
python3 build_artifacts.py
```

The expensive upstream experiment commands remain documented in the stage reports and scripts. The release candidate should not rerun holdouts under altered environments and relabel them confirmatory.

## Verification expectations

1. `manuscript/build_artifacts.py` completes without exception.
2. Generated table row counts agree with the frozen checkpoint classifications.
3. Every figure is traceable to a generated CSV or explicit design metadata.
4. Exact-sham and topology gates remain true in all result JSONs.
5. Manuscript values are checked against CSV/JSON, not against plotted pixel positions.
6. Checkpoints 013–014 remain unexposed in the D1C generation.
