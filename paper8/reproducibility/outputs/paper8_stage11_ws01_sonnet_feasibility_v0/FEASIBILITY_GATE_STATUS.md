# Feasibility gate status

| Criterion | Result |
|---|---|
| Frozen user messages | Exact three-message match |
| Visible model | `claude-sonnet-5` on all three turns |
| Baseline | `PLAN:B` / high |
| Execution | 6/6 correct |
| Follow-up | `PLAN:B` / high |
| Tools and server web | Zero |
| Raw HTTP count | Unknown |
| Baseline full result envelope | Missing |
| Randomized comparator | Absent |
| Calibration eligibility | No |
| Confirmation eligibility | No |

The cycle proves only that the exact WS01 state sequence can be carried through
Claude Code with mechanically valid visible outputs. It does not validate the
transport for the sealed calibration protocol and does not estimate the Binding
Test treatment contrast.
