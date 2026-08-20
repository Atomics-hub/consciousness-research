"""Hostile tests for the frozen final confirmatory analysis."""

from dataclasses import replace
import json
import unittest

from zero_call.binding_test.confirmatory import (
    CALIBRATION_STUDY_PHASE,
    CATEGORIES,
    CellStrataRequirement,
    CONFIRMATORY_STUDY_PHASE,
    ConfirmatoryDesign,
    ConfirmatoryObservation,
    FROZEN_PAIR_IDS,
    FROZEN_TARGET_FAMILIES,
    MacroCell,
    analyze_confirmatory,
    canonical_active_fine_strata,
    canonical_block_fingerprint,
)


PROTOCOL_RUN_ID = "binding-confirmatory-run-2026-08-05"
PROTOCOL_MANIFEST_DIGEST = "a" * 64


def _cells() -> tuple[MacroCell, ...]:
    return tuple(
        MacroCell(model, target)
        for model in ("model-a@2026-08-01", "model-b@2026-08-02")
        for target in FROZEN_TARGET_FAMILIES
    )


def _design(**overrides: object) -> ConfirmatoryDesign:
    values: dict[str, object] = {
        "study_phase": CONFIRMATORY_STUDY_PHASE,
        "protocol_run_id": PROTOCOL_RUN_ID,
        "protocol_manifest_digest": PROTOCOL_MANIFEST_DIGEST,
        "requirements": tuple(
            CellStrataRequirement(cell, canonical_active_fine_strata(cell.target_family))
            for cell in _cells()
        ),
        "equivalence_margins": {"L": 0.05, "H": 0.05, "U": 0.02},
    }
    values.update(overrides)
    return ConfirmatoryDesign(**values)  # type: ignore[arg-type]


PATTERNS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "zero": (("H", "H", "L", "L"), ("H", "H", "L", "L")),
    "positive_1": (("H", "H", "H", "H"), ("L", "L", "L", "L")),
    "positive_075": (("H", "H", "H", "L"), ("L", "L", "L", "L")),
    "negative_1": (("L", "L", "L", "L"), ("H", "H", "H", "H")),
    "negative_075": (("L", "L", "L", "H"), ("H", "H", "H", "H")),
    "h_pos_025": (("H", "H", "L", "L"), ("H", "L", "L", "L")),
    "h_neg_025": (("H", "L", "L", "L"), ("H", "H", "L", "L")),
    "u_pos_025": (("H", "H", "L", "U"), ("H", "H", "L", "L")),
    "u_neg_025": (("H", "H", "L", "L"), ("H", "H", "L", "U")),
}


def _pattern(kind: str, block_index: int, n_blocks: int) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if kind == "positive":
        return PATTERNS["positive_1" if block_index % 2 == 0 else "positive_075"]
    if kind == "negative":
        return PATTERNS["negative_1" if block_index % 2 == 0 else "negative_075"]
    if kind == "equivalent_variable":
        sequence = ("h_pos_025", "h_neg_025", "u_pos_025", "u_neg_025")
        return PATTERNS[sequence[block_index]] if block_index < 4 else PATTERNS["zero"]
    if kind == "boundary":
        return PATTERNS["h_pos_025"] if block_index < n_blocks // 5 else PATTERNS["zero"]
    return PATTERNS["zero"]


def _block(
    cell: MacroCell,
    fine: str,
    index: int,
    pattern: tuple[tuple[str, ...], tuple[str, ...]],
) -> list[ConfirmatoryObservation]:
    block_id = f"{cell.cell_id}::{fine}::b{index:03d}"
    session_ids = [f"{block_id}::s{value}" for value in range(8)]
    baselines = ("L", "L", "H", "H", "L", "L", "H", "H")
    arms = ("self",) * 4 + ("yoke",) * 4
    donors = tuple(session_ids[:4]) + (
        session_ids[0], session_ids[2], session_ids[1], session_ids[3]
    )
    schedules = ("L", "L", "H", "H", "L", "H", "L", "H")
    assignments = tuple(
        (session_ids[i], baselines[i], arms[i], schedules[i], donors[i])
        for i in range(8)
    )
    fingerprint = canonical_block_fingerprint(
        block_id, cell.model_snapshot, cell.target_family, fine, assignments
    )
    outcomes = tuple(pattern[0]) + tuple(pattern[1])
    return [
        ConfirmatoryObservation(
            study_phase=CONFIRMATORY_STUDY_PHASE,
            protocol_run_id=PROTOCOL_RUN_ID,
            protocol_manifest_digest=PROTOCOL_MANIFEST_DIGEST,
            block_id=block_id,
            session_id=session_ids[i],
            fine_stratum=fine,
            model_snapshot=cell.model_snapshot,
            target_family=cell.target_family,
            arm=arms[i],
            category=outcomes[i],
            baseline_choice=baselines[i],
            received_schedule=schedules[i],
            donor_session_id=donors[i],
            canonical_block_fingerprint=fingerprint,
        )
        for i in range(8)
    ]


def _panel(
    kinds: dict[MacroCell, str] | None = None,
    *,
    n_blocks: int = 4,
    count_override: dict[tuple[MacroCell, str], int] | None = None,
) -> tuple[ConfirmatoryObservation, ...]:
    rows: list[ConfirmatoryObservation] = []
    kinds = kinds or {}
    for cell in _cells():
        kind = kinds.get(cell, "zero")
        for fine in canonical_active_fine_strata(cell.target_family):
            count = n_blocks if count_override is None else count_override[(cell, fine)]
            for index in range(count):
                rows.extend(_block(cell, fine, index, _pattern(kind, index, count)))
    return tuple(rows)


class ConfirmatoryInferenceTests(unittest.TestCase):
    def test_frozen_design_rejects_parameter_flexibility_and_margins_are_immutable(self) -> None:
        design = _design()
        self.assertEqual(design.alpha, 0.05)
        self.assertEqual(design.positive_threshold, 0.05)
        with self.assertRaises(TypeError):
            design.equivalence_margins["L"] = 0.10  # type: ignore[index]
        with self.assertRaises(TypeError):
            dict.__setitem__(design.equivalence_margins, "L", 0.10)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            FROZEN_PAIR_IDS["work_score_allocation"] = ("forged",)  # type: ignore[index]
        for override in (
            {"alpha": 0.10},
            {"positive_threshold": 0.0},
            {"min_blocks_per_stratum": 3},
            {"equivalence_margins": {"L": 0.10, "H": 0.05, "U": 0.02}},
        ):
            with self.assertRaises(ValueError):
                _design(**override)
        json.dumps(design.to_dict(), allow_nan=False)

    def test_phase_and_protocol_binding_are_required_and_validated(self) -> None:
        for override in (
            {"study_phase": "pilot"},
            {"protocol_run_id": ""},
            {"protocol_manifest_digest": "A" * 64},
            {"protocol_manifest_digest": "a" * 63},
        ):
            with self.assertRaises(ValueError):
                _design(**override)

        row = _panel()[0]
        for override in (
            {"study_phase": "pilot"},
            {"protocol_run_id": ""},
            {"protocol_manifest_digest": "not-a-digest"},
        ):
            with self.assertRaises(ValueError):
                replace(row, **override)

        encoded = _design().to_dict()
        self.assertEqual(encoded["study_phase"], CONFIRMATORY_STUDY_PHASE)
        self.assertEqual(encoded["protocol_run_id"], PROTOCOL_RUN_ID)
        self.assertEqual(
            encoded["protocol_manifest_digest"], PROTOCOL_MANIFEST_DIGEST
        )

    def test_confirmatory_firewall_precedes_block_analysis(self) -> None:
        row = _panel()[0]

        calibration = replace(row, study_phase=CALIBRATION_STUDY_PHASE)
        with self.assertRaisesRegex(ValueError, "calibration phase"):
            analyze_confirmatory((calibration,), design=_design())

        with self.assertRaisesRegex(ValueError, "calibration phase"):
            analyze_confirmatory(
                (row,), design=_design(study_phase=CALIBRATION_STUDY_PHASE)
            )

        wrong_run = replace(row, protocol_run_id="another-run")
        with self.assertRaisesRegex(ValueError, "protocol_run_id mismatch"):
            analyze_confirmatory((wrong_run,), design=_design())

        wrong_digest = replace(row, protocol_manifest_digest="b" * 64)
        with self.assertRaisesRegex(
            ValueError, "protocol_manifest_digest mismatch"
        ):
            analyze_confirmatory((wrong_digest,), design=_design())

    def test_strict_observation_mapping_loader_rejects_schema_drift_and_calibration(self) -> None:
        row = _panel()[0]
        record = row.to_dict()
        self.assertEqual(ConfirmatoryObservation.from_mapping(record), row)

        missing = dict(record)
        missing.pop("category")
        with self.assertRaisesRegex(ValueError, "missing=.*category"):
            ConfirmatoryObservation.from_mapping(missing)

        extra = {**record, "unexpected": True}
        with self.assertRaisesRegex(ValueError, "extra=.*unexpected"):
            ConfirmatoryObservation.from_mapping(extra)

        calibration = {**record, "study_phase": CALIBRATION_STUDY_PHASE}
        with self.assertRaisesRegex(ValueError, "calibration records"):
            ConfirmatoryObservation.from_mapping(calibration)

        with self.assertRaises(TypeError):
            ConfirmatoryObservation.from_mapping([])  # type: ignore[arg-type]

    def test_exact_24_active_canonical_strata_are_required_per_target(self) -> None:
        for target in FROZEN_TARGET_FAMILIES:
            strata = canonical_active_fine_strata(target)
            self.assertEqual(len(strata), 24)
            self.assertTrue(all("dose=active" in value for value in strata))
        cell = _cells()[0]
        expected = canonical_active_fine_strata(cell.target_family)
        with self.assertRaises(ValueError):
            CellStrataRequirement(cell, expected[:-1])
        with self.assertRaises(ValueError):
            CellStrataRequirement(
                cell,
                tuple(value.replace("dose=active", "dose=zero_dose") for value in expected),
            )
        with self.assertRaises(ValueError):
            CellStrataRequirement(cell, ("arbitrary",) * 24)

    def test_positive_and_reverse_observed_reallocation_are_explicit(self) -> None:
        positive = analyze_confirmatory(
            _panel({cell: "positive" for cell in _cells()}), design=_design()
        )
        self.assertEqual(
            positive.positive_headline.status,
            "positive_observed_reallocation_established",
        )
        self.assertEqual(positive.reverse_headline.status, "not_established")
        self.assertIn("observed follow-up disposition", positive.positive_headline.claim)
        self.assertIn("self-contingent", positive.positive_headline.claim)
        reverse = analyze_confirmatory(
            _panel({cell: "negative" for cell in _cells()}), design=_design()
        )
        self.assertEqual(
            reverse.reverse_headline.status,
            "reverse_observed_reallocation_established",
        )
        self.assertEqual(reverse.positive_headline.status, "not_established")

    def test_zero_standard_error_can_never_establish_a_claim(self) -> None:
        result = analyze_confirmatory(_panel(), design=_design())
        self.assertEqual(result.positive_headline.status, "not_established")
        self.assertEqual(result.reverse_headline.status, "not_established")
        self.assertEqual(result.equivalence_headline.status, "not_established")
        for cell in result.cells.values():
            for category in CATEGORIES:
                component = cell.categories[category]
                self.assertFalse(component.inference_valid)
                self.assertIn("zero empirical", component.guard_reason or "")

    def test_variable_null_can_establish_observable_equivalence(self) -> None:
        result = analyze_confirmatory(
            _panel(
                {cell: "equivalent_variable" for cell in _cells()},
                n_blocks=16,
            ),
            design=_design(),
        )
        self.assertEqual(result.equivalence_headline.status, "equivalence_established")
        for cell in result.cells.values():
            self.assertTrue(all(value.inference_valid for value in cell.categories.values()))

    def test_cancellation_and_one_cell_effect_cannot_rescue_headline(self) -> None:
        positive, negative = _cells()[:2]
        cancellation = analyze_confirmatory(
            _panel({positive: "positive", negative: "negative"}), design=_design()
        )
        self.assertAlmostEqual(cancellation.pooled_secondary.categories["H"].estimate, 0.0)
        self.assertEqual(cancellation.positive_headline.status, "not_established")
        one = analyze_confirmatory(_panel({_cells()[0]: "positive"}), design=_design())
        self.assertGreater(one.pooled_secondary.categories["H"].estimate, 0.0)
        self.assertEqual(one.positive_headline.status, "not_established")
        self.assertEqual(len(one.positive_headline.passing_cells), 1)

    def test_equal_weights_ignore_unequal_retained_block_counts(self) -> None:
        focus = _cells()[0]
        focus_fines = canonical_active_fine_strata(focus.target_family)
        counts = {
            (cell, fine): (8 if cell == focus and fine == focus_fines[1] else 4)
            for cell in _cells()
            for fine in canonical_active_fine_strata(cell.target_family)
        }
        rows: list[ConfirmatoryObservation] = []
        for cell in _cells():
            for fine in canonical_active_fine_strata(cell.target_family):
                count = counts[(cell, fine)]
                kind = "positive" if cell == focus and fine == focus_fines[0] else "zero"
                for index in range(count):
                    rows.extend(_block(cell, fine, index, _pattern(kind, index, count)))
        result = analyze_confirmatory(rows, design=_design()).cells[focus.cell_id]
        self.assertAlmostEqual(result.categories["H"].estimate, 0.875 / 24)
        self.assertEqual(result.equal_fine_stratum_weight, 1 / 24)
        self.assertEqual(result.blocks_by_fine_stratum[focus_fines[1]], 8)

    def test_strict_point05_boundary_is_nonpassing(self) -> None:
        result = analyze_confirmatory(
            _panel({cell: "boundary" for cell in _cells()}, n_blocks=20),
            design=_design(),
        )
        for cell in result.cells.values():
            self.assertAlmostEqual(cell.categories["H"].estimate, 0.05)
            self.assertAlmostEqual(cell.categories["L"].estimate, -0.05)
        self.assertEqual(result.positive_headline.status, "not_established")
        self.assertEqual(result.equivalence_headline.status, "not_established")

    def test_canonical_assignment_provenance_is_recomputed_and_structural(self) -> None:
        rows = list(_panel())
        forged = rows.copy()
        forged[0] = replace(forged[0], canonical_block_fingerprint="0" * 64)
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            analyze_confirmatory(forged, design=_design())

        block_id = rows[0].block_id
        indices = [index for index, row in enumerate(rows) if row.block_id == block_id]
        noncanonical = rows.copy()
        noncanonical[0] = replace(noncanonical[0], baseline_choice="H")
        assignments = tuple(
            (
                noncanonical[index].session_id,
                noncanonical[index].baseline_choice,
                noncanonical[index].arm,
                noncanonical[index].received_schedule,
                noncanonical[index].donor_session_id,
            )
            for index in indices
        )
        digest = canonical_block_fingerprint(
            block_id,
            noncanonical[indices[0]].model_snapshot,
            noncanonical[indices[0]].target_family,
            noncanonical[indices[0]].fine_stratum,
            assignments,
        )
        for index in indices:
            noncanonical[index] = replace(
                noncanonical[index], canonical_block_fingerprint=digest
            )
        with self.assertRaisesRegex(ValueError, "4L/4H"):
            analyze_confirmatory(noncanonical, design=_design())

        aliased_table = rows.copy()
        self_indices = indices[:4]
        yoke_indices = indices[4:]
        for yoke_index, self_index in zip(yoke_indices, self_indices):
            donor = aliased_table[self_index]
            aliased_table[yoke_index] = replace(
                aliased_table[yoke_index],
                donor_session_id=donor.session_id,
                received_schedule=donor.baseline_choice,
            )
        assignments = tuple(
            (
                aliased_table[index].session_id,
                aliased_table[index].baseline_choice,
                aliased_table[index].arm,
                aliased_table[index].received_schedule,
                aliased_table[index].donor_session_id,
            )
            for index in indices
        )
        digest = canonical_block_fingerprint(
            block_id,
            aliased_table[indices[0]].model_snapshot,
            aliased_table[indices[0]].target_family,
            aliased_table[indices[0]].fine_stratum,
            assignments,
        )
        for index in indices:
            aliased_table[index] = replace(
                aliased_table[index], canonical_block_fingerprint=digest
            )
        with self.assertRaisesRegex(ValueError, "one observation in each"):
            analyze_confirmatory(aliased_table, design=_design())

        relabeled = rows.copy()
        new_model = _cells()[2].model_snapshot
        for index in indices:
            relabeled[index] = replace(relabeled[index], model_snapshot=new_model)
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            analyze_confirmatory(relabeled, design=_design())

    def test_duplicate_session_malformed_block_and_missing_stratum_are_rejected(self) -> None:
        rows = list(_panel())
        duplicate = rows.copy()
        duplicate[-1] = replace(duplicate[-1], session_id=duplicate[0].session_id)
        with self.assertRaisesRegex(ValueError, "globally unique"):
            analyze_confirmatory(duplicate, design=_design())
        with self.assertRaisesRegex(ValueError, "exactly 8"):
            analyze_confirmatory(rows[:-1], design=_design())
        missing_fine = canonical_active_fine_strata(_cells()[0].target_family)[0]
        missing = [
            row for row in rows
            if not (row.macro_cell == _cells()[0] and row.fine_stratum == missing_fine)
        ]
        with self.assertRaisesRegex(ValueError, "coverage is incomplete"):
            analyze_confirmatory(missing, design=_design())

    def test_simultaneous_metadata_distinguishes_pointwise_and_familywise_levels(self) -> None:
        result = analyze_confirmatory(
            _panel({cell: "positive" for cell in _cells()}), design=_design()
        )
        interval = next(iter(result.cells.values())).categories["H"].simultaneous_interval
        self.assertAlmostEqual(interval.confidence_level, 1 - 0.05 / 12)
        self.assertEqual(interval.familywise_confidence_level, 0.95)
        self.assertEqual(interval.family_size, 12)
        self.assertIn("Bonferroni", interval.coverage_scope)
        decoded = json.loads(result.to_json(sort_keys=True))
        self.assertFalse(decoded["binary_can_gate"] if "binary_can_gate" in decoded else False)


if __name__ == "__main__":
    unittest.main()
