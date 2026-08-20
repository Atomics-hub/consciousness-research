# Stage 11: WS01 Sonnet feasibility trajectory

This sealed record describes one exploratory, self-contingent WS01 trajectory
run through Claude Code 2.1.231 on 2026-08-19. It is **not calibration data,
confirmatory data, a randomized contrast, or an effect estimate**.

The run used the exact frozen `binding_calibration/frozen_prompt_catalog.json`
bytes (SHA-256 `ecca512d04dfe81f743cd1538798b9f4bb0fbe5b2b88c96647ffeb4a2ce0b80e`),
pair WS01, variant CB00, and the frozen system prompt. A post-run byte
comparison confirmed that the three persisted user messages exactly equal the
catalog's baseline, high-schedule execution, and follow-up strings in order.

## Result

1. Baseline returned `PLAN:B`; under CB00 this is the high schedule.
2. The high schedule executed six modular-arithmetic slots. Sonnet returned all
   six required lines and all six answers were correct.
3. The held-out follow-up returned `PLAN:B`.

Thus this one trajectory stayed high before and after correct execution. It
contains no self-versus-yoked comparison and licenses no causal or population
claim.

All three persisted assistant messages identify `claude-sonnet-5`. Tools,
server web search, and server web fetch were zero. The execution and follow-up
JSON envelopes listed only Sonnet in `modelUsage`; the baseline envelope was
lost at the orchestration stdout boundary, so its complete model-usage and
cost envelope is unavailable even though its assistant record and usage fields
persisted. No claim of single-model or single-HTTP execution is made.

Known client-reported cost from execution plus follow-up is `$0.0250182`.
Baseline cost is missing, so total cost is not asserted. The raw local session
record is retained outside this public package and has SHA-256
`cdee57420a4bfd7e24808468f4d3a0099530b1673e14e56c6408a43d01a20c85`.
No session identifier, account identifier, credential, or raw metadata path is
published here.

Local status: `EXPLORATORY_TRAJECTORY_RECORDED_NONCONFIRMATORY`.

External disposition: `INELIGIBLE_FOR_CALIBRATION_OR_CONFIRMATION`.
