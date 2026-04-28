# Paper 3 Stats Plan

This plan fixes the main weakness of the Paper 2 pilot: episode-level samples are not independent replications. The independent unit is the trained source seed.

## Unit Of Inference

Use independent training seeds as the main unit of inference.

- Recommended final run: 20 to 30 source seeds.
- Pilot run: 5 to 8 source seeds for variance and power estimates.
- Smoke run: 2 source seeds for plumbing only.
- Evaluation episodes: 200 to 500 paired episodes per condition per source seed.

Current AST v0 draft decision:

- Use the core 10-attempted-seed replication as the preprint-scale result basis.
- Report the eight source seeds that passed validation as the transfer-analysis set.
- Retain the two rejected source seeds in the validation flow and run records.
- Treat a 20 to 30 attempted-seed run as an upgrade path for a larger journal-style version, not a blocker for drafting.

Episodes reduce measurement noise inside a seed. They do not replace independent source seeds.

## Seed Registry

Generate seeds from a fixed master seed and stable labels:

```text
study_id
run_id
role
condition
training_seed_index
eval_episode_index
extra
```

Seed roles:

- source_train_seed
- target_init_seed
- finetune_env_seed
- eval_episode_seed
- identity_probe_seed
- phi_sampling_seed
- bootstrap_seed

Every run should save the resolved seed registry.

## Paired Evaluation

For every training seed, evaluate every condition on the same ordered evaluation episodes.

Pair by:

```text
training_seed_index x eval_episode_seed x condition
```

Primary analysis should aggregate each metric to one value per training seed per condition, then compute paired seed-level differences.

## Primary Metrics

- reward
- goals found
- distractor capture rate
- self-report correlation
- identity probe accuracy
- adaptation steps to threshold

Metric-specific rules:

- Use Fisher z before averaging correlations, then back-transform for reporting.
- Use rates for distractor capture if episode lengths differ.
- Use exact or binomial intervals for identity probe accuracy.
- Treat memory overlap as diagnostic unless a behavioral memory task is added.
- Treat ToM as secondary unless source validation clears a preregistered threshold.

## Primary Tests

For each primary contrast:

1. Compute seed-level condition means.
2. Compute paired seed-level differences.
3. Report mean difference.
4. Report median difference.
5. Report 95 percent bootstrap CI over source seeds.
6. Report paired Cohen dz.
7. Report paired sign-flip permutation p-value.
8. Apply Holm correction across the primary family.

Mixed-effects models can be used as sensitivity analysis, but not as the headline claim.

## Correction Strategy

Use a primary family with Holm-Bonferroni correction:

1. source_full versus source ablations
2. copied conditions versus matched random controls
3. copied-trainable versus behavior distillation
4. copied-trainable versus full retrain, if a non-inferiority margin is defined first

Use Benjamini-Hochberg FDR for secondary metrics. Report exploratory analyses without significance language.

## Minimum Effects Of Interest

Draft margins:

- self-report correlation: delta r >= 0.10 after back-transform
- reward: at least 20 percent closure of the random-to-source gap
- identity probe accuracy: copied condition >= 0.95 and independent controls <= 0.05
- non-inferiority to full retrain: no worse than 20 percent of the full-retrain minus random-control gap

These margins should be frozen before final runs.

## Power

Pilot with 5 to 8 seeds, then simulate power from the observed seed-level paired differences.

Planning rule:

- 20 seeds has useful power for effects around 0.65 SD of paired differences.
- 30 seeds gets closer to 0.5 SD.
- More episodes help within-seed precision, but do not fix high seed-to-seed variance.

## Reporting

Every results table should include:

- n source seeds
- n paired evaluation episodes
- raw condition means
- paired mean differences
- 95 percent CIs
- effect sizes
- corrected p-values for primary tests
- failed or excluded runs with reasons

Every figure should be generated from saved raw metrics, not from hand-entered summary values.
