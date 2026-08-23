"""Checkpoint-012 local-error matching of Mi1 timescale and shunt candidates."""

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
from work.d1b_local_calibration import ALPHA, stratified_metrics  # noqa: E402
from work.d1b_source_ensemble import DT, motion_dataset  # noqa: E402


MODEL_ID = "012"
MARGIN = 0.01
GAMMA_GRID = (0.01, 0.025, 0.05, 0.075, 0.1)
MATCH_RATIO = (0.8, 1.25)


def run() -> dict:
    started = time.perf_counter()
    prerequisite = json.loads((DATA_ROOT / "d1c_source_effect_scale.json").read_text())
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
    mask = torch.as_tensor(types == "Mi1")
    network.dynamics = PPNeuronIGRSynapses(activation={"type": "relu"})
    initial = network.steady_state(1.0, DT, movie.shape[0])
    full_input = prepare_input(network, movie)
    with torch.no_grad():
        source = network.forward(full_input, DT, state=clone_state(initial), as_states=False)
    previous = torch.cat([initial.nodes.activity[:, None], source[:, :-1]], dim=1)
    velocity = (source - previous) / DT
    activity_array = previous[..., mask].cpu().numpy()
    velocity_array = velocity[..., mask].cpu().numpy()
    timescale = stratified_metrics(
        "timescale", activity_array, velocity_array, ALPHA, intensity_rows, MARGIN
    )
    grid = []
    for gamma in GAMMA_GRID:
        result = stratified_metrics(
            "shunt", activity_array, velocity_array, gamma, intensity_rows, MARGIN
        )
        ratio = result["aggregate"]["nrmse"] / (timescale["aggregate"]["nrmse"] + 1e-12)
        grid.append({"gamma": gamma, "ratio_to_timescale": ratio, "result": result})
    eligible = [
        row for row in grid
        if row["result"]["passes"] and MATCH_RATIO[0] <= row["ratio_to_timescale"] <= MATCH_RATIO[1]
    ]
    selected = min(eligible, key=lambda row: abs(np.log(row["ratio_to_timescale"]))) if eligible else None
    gates = {
        "source_effect_scale_pass": prerequisite["status"] == "PASS",
        "source_finite": bool(torch.isfinite(source).all()),
        "timescale_passes": timescale["passes"],
        "matched_shunt_exists": selected is not None,
    }
    result = {
        "schema_version": "0.1.0",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "boundary": "checkpoint-012 Mi1 local-only error matching; no global or causal candidate outcome",
        "frozen_design": {
            "model": MODEL_ID, "margin": MARGIN, "timescale_alpha": ALPHA,
            "gamma_grid": list(GAMMA_GRID), "match_ratio": list(MATCH_RATIO),
        },
        "timescale": timescale,
        "shunt_grid": grid,
        "selected_shunt": selected,
        "gates": gates,
        "runtime": {
            "seconds": time.perf_counter() - started,
            "max_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "device": str(flyvis.device),
        },
    }
    output = DATA_ROOT / "d1c_matched_calibration.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    result["integrity_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "status": result["status"], "timescale": result["timescale"],
        "selected_shunt": result["selected_shunt"], "gates": result["gates"],
        "runtime": result["runtime"], "integrity_sha256": result["integrity_sha256"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
