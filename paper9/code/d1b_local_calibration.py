"""Checkpoint-007 local-only calibration for the frozen D1B families."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "work/flyvis-data"
os.environ["FLYVIS_ROOT_DIR"] = str(DATA_ROOT)
os.environ.setdefault("MPLCONFIGDIR", "/tmp/paper9-mpl")
sys.path.insert(0, str(ROOT))

import flyvis  # noqa: E402
from flyvis.network.dynamics import PPNeuronIGRSynapses  # noqa: E402
from work.d1_exploratory_calibration import clone_state, prepare_input  # noqa: E402
from work.d1b_source_ensemble import (  # noqa: E402
    CELL_TYPES,
    DT,
    motion_dataset,
)


MODEL_ID = "007"
ALPHA = 0.01
ALPHA_CENTER = 0.020631499588489532
BETA = 0.25
TAU = 0.1
THETA = 0.0
SCALE = 1.0
E_REV = 1.0
GAMMA_GRID = (0.0001, 0.00025, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1)
WRONG_GAMMA = 1.0


class MaskedShunt(PPNeuronIGRSynapses):
    """Add a shared conductance-shaped shunt term on a selected node mask."""

    def __init__(self, gamma: float, activation=None):
        super().__init__(activation=dict(activation or {"type": "relu"}))
        self.gamma = float(gamma)
        self.mask: torch.Tensor | None = None

    def set_mask(self, mask: torch.Tensor) -> None:
        self.mask = mask.to(dtype=torch.bool)

    def write_state_velocity(self, vel, state, params, target_sum, x_t, **kwargs):
        super().write_state_velocity(vel, state, params, target_sum, x_t=x_t, **kwargs)
        if self.mask is None:
            raise RuntimeError("set_mask must be called")
        mask = self.mask.to(vel.nodes.activity.device)
        activity = state.nodes.activity
        term = self.gamma * torch.sigmoid((activity - THETA) / SCALE) * (E_REV - activity)
        vel.nodes.activity = vel.nodes.activity + torch.where(
            mask, term, torch.zeros_like(term)
        )


def basic_metrics(error: np.ndarray, source_velocity: np.ndarray, margin: float) -> dict:
    rms_source = float(np.sqrt(np.mean(source_velocity**2)))
    p99_source = float(np.quantile(np.abs(source_velocity), 0.99))
    nrmse = float(np.sqrt(np.mean(error**2)) / (rms_source + 1e-12))
    p99_ratio = float(np.quantile(np.abs(error), 0.99) / (p99_source + 1e-12))
    return {
        "nrmse": nrmse,
        "p99_abs_error_ratio": p99_ratio,
        "max_abs_error": float(np.max(np.abs(error))),
        "passes": bool(nrmse <= margin and p99_ratio <= margin),
    }


def family_error(family: str, activity: np.ndarray, source_velocity: np.ndarray, value: float) -> np.ndarray:
    if family == "timescale":
        return source_velocity * value * np.tanh(activity - ALPHA_CENTER)
    if family == "shunt":
        return value / (1.0 + np.exp(-(activity - THETA) / SCALE)) * (E_REV - activity)
    if family == "two_state":
        adaptation = activity[:, 0].copy()
        errors = []
        for frame in range(activity.shape[1]):
            current = activity[:, frame]
            errors.append(value * (adaptation - current))
            adaptation = adaptation + DT * (current - adaptation) / TAU
        return np.stack(errors, axis=1)
    raise ValueError(family)


def stratified_metrics(
    family: str,
    activity: np.ndarray,
    velocity: np.ndarray,
    value: float,
    intensity_rows: dict[str, np.ndarray],
    margin: float,
) -> dict:
    error = family_error(family, activity, velocity, value)
    aggregate = basic_metrics(error, velocity, margin)
    by_intensity = {}
    for name, rows in intensity_rows.items():
        by_intensity[name] = basic_metrics(error[rows], velocity[rows], margin)
    return {
        "aggregate": aggregate,
        "by_intensity": by_intensity,
        "passes": bool(aggregate["passes"] and all(row["passes"] for row in by_intensity.values())),
    }


def run() -> dict:
    started = time.perf_counter()
    margin_result = json.loads((DATA_ROOT / "d1b_source_ensemble.json").read_text())
    local_margin = float(margin_result["margins"]["local_derivative"]["selected_margin"])
    dataset = motion_dataset()
    table = dataset.arg_df.reset_index(drop=True)
    intensity_rows = {
        str(intensity): table.index[table["intensity"] == intensity].to_numpy()
        for intensity in (0, 1)
    }
    movie = torch.stack([dataset[index] for index in range(len(dataset))])[:, :, None, :]
    view = flyvis.NetworkView(flyvis.results_dir / f"flow/0000/{MODEL_ID}")
    network = view.init_network()
    types = np.asarray(network.connectome.nodes.type[:]).astype(str)
    network.dynamics = PPNeuronIGRSynapses(activation={"type": "relu"})
    initial = network.steady_state(1.0, DT, movie.shape[0])
    full_input = prepare_input(network, movie)
    with torch.no_grad():
        source = network.forward(full_input, DT, state=clone_state(initial), as_states=False)
    previous = torch.cat([initial.nodes.activity[:, None], source[:, :-1]], dim=1)
    velocity = (source - previous) / DT

    arrays = {}
    for cell_type in CELL_TYPES:
        mask = torch.as_tensor(types == cell_type)
        arrays[cell_type] = (
            previous[..., mask].cpu().numpy(),
            velocity[..., mask].cpu().numpy(),
        )

    frozen = {"timescale": {}, "two_state": {}}
    for cell_type, (activity, source_velocity) in arrays.items():
        frozen["timescale"][cell_type] = stratified_metrics(
            "timescale", activity, source_velocity, ALPHA, intensity_rows, local_margin
        )
        frozen["two_state"][cell_type] = stratified_metrics(
            "two_state", activity, source_velocity, BETA, intensity_rows, local_margin
        )

    shunt_grid = []
    for gamma in GAMMA_GRID:
        blocks = {
            cell_type: stratified_metrics(
                "shunt", activity, source_velocity, gamma, intensity_rows, local_margin
            )
            for cell_type, (activity, source_velocity) in arrays.items()
        }
        shunt_grid.append({
            "gamma": gamma,
            "blocks": blocks,
            "passes_all_blocks": all(row["passes"] for row in blocks.values()),
        })
    passing = [row for row in shunt_grid if row["passes_all_blocks"]]
    selected = passing[-1] if passing else None
    informative = bool(
        selected is not None
        and any(
            row["aggregate"]["nrmse"] >= 0.25 * local_margin
            for row in selected["blocks"].values()
        )
    )
    wrong = {
        cell_type: stratified_metrics(
            "shunt", activity, source_velocity, WRONG_GAMMA, intensity_rows, local_margin
        )
        for cell_type, (activity, source_velocity) in arrays.items()
    }
    gates = {
        "source_margin_file_passed": margin_result["status"] == "PASS",
        "source_finite": bool(torch.isfinite(source).all()),
        "shunt_has_passing_value": selected is not None,
        "shunt_not_identity_by_epsilon": informative,
        "wrong_shunt_rejected_every_block": all(not row["passes"] for row in wrong.values()),
    }
    result = {
        "schema_version": "0.1.0",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "boundary": "checkpoint-007 local clamped-trajectory calibration only; no global candidate outcomes",
        "frozen_design": {
            "model": MODEL_ID,
            "cell_types": list(CELL_TYPES),
            "local_margin": local_margin,
            "timescale_alpha": ALPHA,
            "two_state_beta": BETA,
            "two_state_tau": TAU,
            "shunt": {"theta": THETA, "scale": SCALE, "E_rev": E_REV, "gamma_grid": list(GAMMA_GRID)},
            "wrong_gamma": WRONG_GAMMA,
        },
        "capacity_ledger": {
            "timescale": {"extra_state_per_node": 0, "shared_fixed_coefficients": 1, "trainable_per_node": 0},
            "two_state": {"extra_state_per_node": 1, "shared_fixed_coefficients": 2, "trainable_per_node": 0},
            "shunt": {"extra_state_per_node": 0, "shared_frozen_coefficients": 4, "calibrated_coefficients": ["gamma"], "trainable_per_node": 0},
        },
        "frozen_families": frozen,
        "shunt_grid": shunt_grid,
        "selected_shunt": selected,
        "wrong_shunt": wrong,
        "gates": gates,
        "runtime": {
            "seconds": time.perf_counter() - started,
            "max_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "device": str(flyvis.device),
        },
    }
    output = DATA_ROOT / "d1b_local_calibration.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    result["integrity_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    return result


if __name__ == "__main__":
    result = run()
    compact = {
        "status": result["status"],
        "selected_shunt": result["selected_shunt"],
        "frozen_family_passes": {
            family: {block: row["passes"] for block, row in blocks.items()}
            for family, blocks in result["frozen_families"].items()
        },
        "gates": result["gates"],
        "runtime": result["runtime"],
        "integrity_sha256": result["integrity_sha256"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
