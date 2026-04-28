# PreservationBench

This directory is the Paper 3 scaffold. It should grow beside `experiments/ast_preservation`, not replace it. The Paper 2 experiment remains the frozen reproduction path.

PreservationBench asks a narrow question:

> When source state is moved into a target substrate, which preservation-relevant functions remain active because of copied state rather than relearning?

It does not claim to measure consciousness, identity, or first-person survival.

## Current Contents

```text
experiments/preservation_bench/
  benchmark/
    ast_eval.py   # log-first evaluator for the Paper 2 AST environment
    episode_logs.py
    spec.py      # condition, metric, and benchmark dataclasses
    seeds.py     # stable seed generation and seed registry helpers
    stats.py     # paired seed-level stats helpers
  configs/
    ast_checkpoint_smoke.json
    ast_smoke.json
    ast_competence_smoke.json
    ast_competence_v2_smoke.json
    ast_competence_v2_5seed.json
    ast_competence_v2_core_10seed.json
    ast_pilot_5seed.json
    ast_multiseed_v0.json
  run_seed_registry.py
  run_ast_checkpoint_eval.py
  plot_preservation_profile.py
  plot_core_figures.py
```

## V0 Target

The first target is **PreservationBench-AST v0**:

- keep the Paper 2 AST environment
- evaluate multiple independent source seeds
- add matched transfer controls
- use paired evaluation episodes
- analyze training-seed-level paired differences
- report continuity profiles instead of one score

## First Runnable Smoke Test

The initial smoke test evaluates static conditions from the existing Paper 2 checkpoint. It does not retrain or fine-tune targets yet.

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_checkpoint_eval.py \
  --config experiments/preservation_bench/configs/ast_checkpoint_smoke.json
```

This writes raw logs and summaries under:

```text
experiments/preservation_bench/runs/ast_checkpoint_smoke/
```

The repair smoke test adds adapter-only repair, fully trainable repair, and behavior-only distillation:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_checkpoint_eval.py \
  --config experiments/preservation_bench/configs/ast_checkpoint_repair_smoke.json
```

The training smoke trains two tiny source agents and evaluates a small condition set:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_training_smoke.py \
  --config experiments/preservation_bench/configs/ast_smoke.json
```

It is resumable by default. Use `--force` to overwrite an existing run.

Each training seed writes:

```text
train_seed_{i}/manifest.json
train_seed_{i}/source_validation.json
train_seed_{i}/seed_summaries.json
train_seed_{i}/{condition}_summary.json
```

The current best pilot config is the competence v2 small-arena task:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_training_smoke.py \
  --config experiments/preservation_bench/configs/ast_competence_v2_5seed.json
```

The reduced replication config keeps the core contrasts and drops exploratory side branches:

```bash
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 python3 \
  experiments/preservation_bench/run_ast_training_smoke.py \
  --config experiments/preservation_bench/configs/ast_competence_v2_core_10seed.json
```

## Main Conditions

- source_full
- source_attention_ablated
- source_schema_ablated
- source_self_model_ablated
- a_to_a_copy
- b_frozen_copy
- b_adapter_repair_copy
- b_source_align_repair_copy
- b_source_align_repair_copy_long
- b_source_align_policy_copy_long
- b_source_align_attention_copy_long
- b_source_align_attention_adapter_long
- b_source_align_control_adapter_long
- b_source_align_attention_copy_trainable_long
- b_source_align_attention_copy_random_adapter_long
- b_source_align_identity_adapter_long
- b_trainable_copy
- b_behavior_distill
- b_frozen_random
- b_trainable_random
- b_full_retrain

## Reproducibility Rules

- Every final run gets a manifest.
- Every condition uses the same final evaluation episode seeds.
- Validation seeds and final evaluation seeds stay separate.
- Crashed or failed runs are logged, not silently replaced.
- Final analysis happens from raw metrics, not hand-entered summaries.

## Next Build Step

Generate validation-aware summaries and contrasts from a run:

```bash
python3 experiments/preservation_bench/analyze_seed_summaries.py \
  experiments/preservation_bench/runs/ast_competence_v2_5seed/seed_summaries.json \
  --validated-only \
  --means

python3 experiments/preservation_bench/analyze_contrasts.py \
  experiments/preservation_bench/runs/ast_competence_v2_5seed/seed_summaries.json \
  --validated-only
```

Generate a preservation-profile figure from a run:

```bash
python3 experiments/preservation_bench/plot_preservation_profile.py \
  experiments/preservation_bench/runs/ast_competence_v2_5seed/seed_summaries.json \
  --output experiments/preservation_bench/runs/ast_competence_v2_5seed/preservation_profile.png \
  --validated-only
```

Generate the core paper figures:

```bash
python3 experiments/preservation_bench/plot_core_figures.py \
  experiments/preservation_bench/runs/ast_competence_v2_core_10seed/seed_summaries.json \
  --output-dir experiments/preservation_bench/runs/ast_competence_v2_core_10seed/paper_figures
```

Current pilot read:

- copied identity probes survive across copied-payload transfer conditions
- source-alignment repair improves report over frozen copy but does not restore control
- copied-attention conditions recover the strongest profile, but they narrow the substrate gap
- the attention-adapter bridge recovers report without source-like control
- the control-adapter bridge can optimize reward and goal attention without restoring source-like goals found or source-action agreement

Core replication status:

- `ast_competence_v2_core_10seed.json` has been run
- 8 of 10 source seeds passed validation
- rejected source seeds are retained as source-validation failures, not used for transfer contrasts
- the reduced preservation profile is written to `runs/ast_competence_v2_core_10seed/preservation_profile_core.png`
- focused paper figures are written under `runs/ast_competence_v2_core_10seed/paper_figures/`
- the paper-facing results and discussion draft is at `paper3/ast_v0_results_draft.md`
- the main manuscript draft is at `paper3/manuscript.md`
- trackable manuscript figures are under `paper3/figures/`

Seed-count decision:

- use the validated n = 8 core replication as the preprint-scale AST v0 result basis
- do not add more transfer variants before drafting
- only run 20 to 30 attempted source seeds if the target is a larger journal-style version

Next build step:

1. audit `paper3/manuscript.md` for overclaims and missing citations
2. add a PDF build path for Paper 3
3. freeze the protocol before any larger final run

## Seed Registry

Generate a smoke-test seed registry with:

```bash
python3 experiments/preservation_bench/run_seed_registry.py \
  --config experiments/preservation_bench/configs/ast_smoke.json \
  --output experiments/preservation_bench/seeds/ast_smoke_seed_registry.csv
```
