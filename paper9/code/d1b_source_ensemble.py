"""Freeze D1B source variability and practical-equivalence margins.

This script exposes checkpoints 005--007 only to the source dynamics.  It does
not instantiate or evaluate any substitute family.
"""

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
from flyvis.datasets.moving_bar import MovingEdge  # noqa: E402
from flyvis.network.dynamics import PPNeuronIGRSynapses  # noqa: E402
from work.d1_exploratory_calibration import clone_state, prepare_input  # noqa: E402


DT = 0.02
MODEL_IDS = ("005", "006", "007")
CELL_TYPES = ("T4a", "T5a", "Mi1")
ANGLES = tuple(range(0, 360, 30))
INTENSITIES = (0, 1)
AUTHORED_CEILING = 0.01
FRACTION_OF_SOURCE_VARIABILITY = 0.25
EXACT_LOCAL_FLOOR = 0.0  # D1A exact source-equation shams were bit-exact.
EXACT_RESPONSE_FLOOR = 0.0
EXACT_DECODER_FLOOR = 0.0


def motion_dataset() -> MovingEdge:
    return MovingEdge(
        offsets=[-10, 11],
        intensities=list(INTENSITIES),
        speeds=[19],
        height=80,
        post_pad_mode="continue",
        t_pre=0.5,
        t_post=0.5,
        dt=DT,
        angles=list(ANGLES),
    )


def standardized_rmse(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    b = np.asarray(b, dtype=np.float64).reshape(-1)
    a = a - a.mean()
    b = b - b.mean()
    a = a / (np.sqrt(np.mean(a * a)) + 1e-12)
    b = b / (np.sqrt(np.mean(b * b)) + 1e-12)
    return float(np.sqrt(np.mean((a - b) ** 2)))


def decode_chunked(decoder, activity: torch.Tensor, chunk: int = 2) -> torch.Tensor:
    decoder.eval()
    for parameter in decoder.parameters():
        parameter.requires_grad_(False)
    outputs = []
    with torch.no_grad():
        for start in range(0, activity.shape[0], chunk):
            outputs.append(decoder(activity[start : start + chunk]).cpu())
    return torch.cat(outputs, dim=0)


def source_record(model_id: str, movie: torch.Tensor) -> dict:
    view = flyvis.NetworkView(flyvis.results_dir / f"flow/0000/{model_id}")
    network = view.init_network()
    types = np.asarray(network.connectome.nodes.type[:]).astype(str)
    u = np.asarray(network.connectome.nodes.u[:])
    v = np.asarray(network.connectome.nodes.v[:])
    central = {}
    masks = {}
    for cell_type in CELL_TYPES:
        indices = np.flatnonzero((types == cell_type) & (u == 0) & (v == 0))
        if len(indices) != 1:
            raise RuntimeError(f"expected one central {cell_type}, found {len(indices)}")
        central[cell_type] = int(indices[0])
        masks[cell_type] = torch.as_tensor(types == cell_type)

    network.dynamics = PPNeuronIGRSynapses(activation={"type": "relu"})
    initial = network.steady_state(1.0, DT, movie.shape[0])
    full_input = prepare_input(network, movie)
    with torch.no_grad():
        activity = network.forward(
            full_input, DT, state=clone_state(initial), as_states=False
        )

    previous = torch.cat([initial.nodes.activity[:, None], activity[:, :-1]], dim=1)
    velocity = (activity - previous) / DT
    decoder_map = view.init_decoder()
    decoder = decoder_map["flow"] if isinstance(decoder_map, dict) else decoder_map
    decoded = decode_chunked(decoder, activity)
    record = {
        "model_id": model_id,
        "central": {
            cell_type: activity[..., index].detach().cpu().numpy()
            for cell_type, index in central.items()
        },
        "velocity": {
            cell_type: velocity[..., masks[cell_type]].detach().cpu().numpy()
            for cell_type in CELL_TYPES
        },
        "decoded": decoded.numpy(),
        "activity_finite": bool(torch.isfinite(activity).all()),
        "decoder_finite": bool(torch.isfinite(decoded).all()),
        "decoder_parameters": int(sum(p.numel() for p in decoder.parameters())),
        "node_counts": {
            cell_type: int(masks[cell_type].sum()) for cell_type in CELL_TYPES
        },
    }
    del network, view, activity, velocity, decoded, initial, full_input, decoder
    gc.collect()
    return record


def pairwise_distribution(records: list[dict], key: str) -> list[dict]:
    rows = []
    for left_index in range(len(records)):
        for right_index in range(left_index + 1, len(records)):
            left = records[left_index]
            right = records[right_index]
            for sample in range(left[key].shape[0]):
                rows.append({
                    "left": left["model_id"],
                    "right": right["model_id"],
                    "sample": sample,
                    "srmse": standardized_rmse(left[key][sample], right[key][sample]),
                })
    return rows


def block_pairwise_distribution(records: list[dict], key: str) -> list[dict]:
    rows = []
    for left_index in range(len(records)):
        for right_index in range(left_index + 1, len(records)):
            left = records[left_index]
            right = records[right_index]
            for cell_type in CELL_TYPES:
                for sample in range(left[key][cell_type].shape[0]):
                    rows.append({
                        "left": left["model_id"],
                        "right": right["model_id"],
                        "cell_type": cell_type,
                        "sample": sample,
                        "srmse": standardized_rmse(
                            left[key][cell_type][sample],
                            right[key][cell_type][sample],
                        ),
                    })
    return rows


def margin(rows: list[dict], exact_floor: float) -> dict:
    values = np.asarray([row["srmse"] for row in rows], dtype=float)
    q10 = float(np.quantile(values, 0.10))
    grounded = FRACTION_OF_SOURCE_VARIABILITY * q10
    numerical_floor = 10.0 * exact_floor
    selected = max(numerical_floor, min(AUTHORED_CEILING, grounded))
    return {
        "n": int(values.size),
        "q10_source_srmse": q10,
        "quarter_q10": grounded,
        "authored_ceiling": AUTHORED_CEILING,
        "ten_x_exact_floor": numerical_floor,
        "selected_margin": selected,
        "min": float(values.min()),
        "median": float(np.median(values)),
        "max": float(values.max()),
    }


def run() -> dict:
    started = time.perf_counter()
    dataset = motion_dataset()
    movie = torch.stack([dataset[index] for index in range(len(dataset))])[:, :, None, :]
    records = []
    for model_id in MODEL_IDS:
        records.append(source_record(model_id, movie))

    response_rows = block_pairwise_distribution(records, "central")
    velocity_rows = block_pairwise_distribution(records, "velocity")
    decoder_rows = pairwise_distribution(records, "decoded")
    margins = {
        "local_derivative": margin(velocity_rows, EXACT_LOCAL_FLOOR),
        "block_response": margin(response_rows, EXACT_RESPONSE_FLOOR),
        "decoder": margin(decoder_rows, EXACT_DECODER_FLOOR),
    }
    gates = {
        "all_source_finite": all(
            record["activity_finite"] and record["decoder_finite"]
            for record in records
        ),
        "expected_node_counts": all(
            all(record["node_counts"][cell_type] == 721 for cell_type in CELL_TYPES)
            for record in records
        ),
        "fixed_decoder_architecture": all(
            record["decoder_parameters"] == 7427 for record in records
        ),
        "positive_margins": all(
            value["selected_margin"] > 0 for value in margins.values()
        ),
        "margins_not_relaxed": all(
            value["selected_margin"] <= AUTHORED_CEILING for value in margins.values()
        ),
    }
    result = {
        "schema_version": "0.1.0",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "boundary": (
            "source-only checkpoints 005--007; source-model variation is model "
            "uncertainty, not biological repeatability or independent evidence"
        ),
        "frozen_design": {
            "models": list(MODEL_IDS),
            "cell_types": list(CELL_TYPES),
            "angles": list(ANGLES),
            "intensities": list(INTENSITIES),
            "samples": len(dataset),
            "frames": int(movie.shape[1]),
            "dt": DT,
            "authored_ceiling": AUTHORED_CEILING,
            "fraction_of_q10": FRACTION_OF_SOURCE_VARIABILITY,
        },
        "margins": margins,
        "source_records": [{
            key: value for key, value in record.items()
            if key not in {"central", "velocity", "decoded"}
        } for record in records],
        "pairwise_summaries": {
            "response": response_rows,
            "velocity": velocity_rows,
            "decoder": decoder_rows,
        },
        "gates": gates,
        "runtime": {
            "seconds": time.perf_counter() - started,
            "max_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "device": str(flyvis.device),
        },
    }
    output = DATA_ROOT / "d1b_source_ensemble.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    result["integrity_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "status": result["status"],
        "margins": result["margins"],
        "gates": result["gates"],
        "runtime": result["runtime"],
        "integrity_sha256": result["integrity_sha256"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
