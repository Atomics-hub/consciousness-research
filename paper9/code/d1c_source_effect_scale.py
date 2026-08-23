"""Source-only canonical Mi1 decoder-effect scale for D1C checkpoints 010--012."""

from __future__ import annotations

import gc
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
from work.d1b_source_ensemble import DT, decode_chunked, motion_dataset  # noqa: E402


MODEL_IDS = ("010", "011", "012")
CELLS = ((0, 0), (90, 1), (180, 0), (270, 1))
FRAME = 25
DELTA = 0.01


def execute(network, initial, full_input, mask, perturb: bool):
    network.dynamics = PPNeuronIGRSynapses(activation={"type": "relu"})
    network.clear_state_hooks()
    state = clone_state(initial)
    counter = {"frame": 0}
    if perturb:
        def impulse(current):
            if counter["frame"] == FRAME:
                activity = current.nodes.activity.clone()
                activity[..., mask] += DELTA
                current.nodes.activity = activity
            counter["frame"] += 1
            return current
        network.register_state_hook(impulse)
    with torch.no_grad():
        output = network.forward(full_input, DT, state=state, as_states=False)
    network.clear_state_hooks()
    return output


def run() -> dict:
    started = time.perf_counter()
    dataset = motion_dataset()
    table = dataset.arg_df.reset_index(drop=True)
    rows = [table.index[(table["angle"] == a) & (table["intensity"] == i)].item() for a, i in CELLS]
    movie = torch.stack([dataset[row] for row in rows])[:, :, None, :]
    records = []
    per_sample_rms = []
    for model_id in MODEL_IDS:
        view = flyvis.NetworkView(flyvis.results_dir / f"flow/0000/{model_id}")
        network = view.init_network()
        types = np.asarray(network.connectome.nodes.type[:]).astype(str)
        mask = torch.as_tensor(types == "Mi1")
        network.dynamics = PPNeuronIGRSynapses(activation={"type": "relu"})
        initial = network.steady_state(1.0, DT, movie.shape[0])
        full_input = prepare_input(network, movie)
        decoder_map = view.init_decoder()
        decoder = decoder_map["flow"] if isinstance(decoder_map, dict) else decoder_map
        base = execute(network, initial, full_input, mask, False)
        perturbed = execute(network, initial, full_input, mask, True)
        decoded_base = decode_chunked(decoder, base)
        decoded_perturbed = decode_chunked(decoder, perturbed)
        effect = decoded_perturbed - decoded_base
        sample_rms = torch.sqrt(torch.mean(effect**2, dim=(1, 2, 3))).cpu().numpy()
        per_sample_rms.extend(float(value) for value in sample_rms)
        records.append({
            "model_id": model_id,
            "source_decoder_effect_rms": float(torch.sqrt(torch.mean(effect**2))),
            "per_cell_decoder_effect_rms": {
                f"{a}:{i}": float(value) for (a, i), value in zip(CELLS, sample_rms)
            },
            "finite": bool(torch.isfinite(effect).all()),
        })
        del network, view, base, perturbed, decoded_base, decoded_perturbed, effect
        gc.collect()
    floor = float(np.quantile(np.asarray(per_sample_rms), 0.10))
    gates = {
        "all_finite": all(row["finite"] for row in records),
        "positive_floor": floor > 0,
        "three_source_checkpoints": len(records) == 3,
    }
    result = {
        "schema_version": "0.1.0",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "boundary": "source-only canonical Mi1 impulse decoder-effect scale; no candidate exposure",
        "frozen_design": {
            "models": list(MODEL_IDS), "cells": [list(cell) for cell in CELLS],
            "frame": FRAME, "delta": DELTA, "dt": DT,
        },
        "records": records,
        "denominator_floor_q10_per_sample_decoder_effect_rms": floor,
        "all_per_sample_rms": per_sample_rms,
        "gates": gates,
        "runtime": {
            "seconds": time.perf_counter() - started,
            "max_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "device": str(flyvis.device),
        },
    }
    output = DATA_ROOT / "d1c_source_effect_scale.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    result["integrity_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "status": result["status"],
        "floor": result["denominator_floor_q10_per_sample_decoder_effect_rms"],
        "records": result["records"],
        "gates": result["gates"],
        "runtime": result["runtime"],
        "integrity_sha256": result["integrity_sha256"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
