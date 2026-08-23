"""Checkpoint-008 D1B twelve-direction global and fixed-decoder holdout."""

from __future__ import annotations

import argparse
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
from work.connectome_substitution_gate.flyvis_mixed_dynamics_smoke import topology_digest  # noqa: E402
from work.d1_exploratory_calibration import (  # noqa: E402
    MaskedTimescale,
    balanced_mask,
    clone_state,
    normalized_rms,
    prepare_input,
)
from work.d1_two_state_candidate import MaskedTwoState, candidate_initial  # noqa: E402
from work.d1b_local_calibration import (  # noqa: E402
    ALPHA,
    ALPHA_CENTER,
    BETA,
    MaskedShunt,
    WRONG_GAMMA,
    stratified_metrics,
)
from work.d1b_source_ensemble import (  # noqa: E402
    ANGLES,
    CELL_TYPES,
    DT,
    decode_chunked,
    motion_dataset,
)


MODEL_ID = "008"
FRACTIONS = (0.25, 0.5, 1.0)


def execute(network, dynamics, mask, initial, full_input) -> torch.Tensor:
    dynamics.set_mask(mask)
    network.dynamics = dynamics
    state = candidate_initial(network, initial) if isinstance(dynamics, MaskedTwoState) else clone_state(initial)
    with torch.no_grad():
        return network.forward(full_input, DT, state=state, as_states=False)


def decoder_metrics(candidate: torch.Tensor, source: torch.Tensor, dataset, margin: float) -> dict:
    difference = candidate - source
    flat_candidate = candidate.reshape(-1)
    flat_source = source.reshape(-1)
    cosine = float(
        torch.dot(flat_candidate, flat_source)
        / (torch.linalg.vector_norm(flat_candidate) * torch.linalg.vector_norm(flat_source) + 1e-12)
    )
    table = dataset.arg_df.reset_index(drop=True)
    by_direction = {}
    for intensity in (0, 1):
        for angle in ANGLES:
            row = table.index[(table["intensity"] == intensity) & (table["angle"] == angle)].to_numpy()
            by_direction[f"{angle}:{intensity}"] = normalized_rms(candidate[row], source[row])
    nrmse = normalized_rms(candidate, source)
    return {
        "nrmse": nrmse,
        "cosine": float(np.clip(cosine, -1.0, 1.0)),
        "max_abs_error": float(torch.max(torch.abs(difference))),
        "by_direction_nrmse": by_direction,
        "passes": bool(nrmse <= margin),
        "target_endpoint": "not available for synthetic MovingEdge; preservation uses frozen source-decoder output",
    }


def tuning_metrics(candidate: torch.Tensor, source: torch.Tensor, dataset, central_index: int) -> dict:
    table = dataset.arg_df.reset_index(drop=True)
    result = {}
    for intensity in (0, 1):
        source_curve = []
        candidate_curve = []
        for angle in ANGLES:
            row = table.index[(table["intensity"] == intensity) & (table["angle"] == angle)].item()
            source_curve.append(float(torch.max(source[row, :, central_index])))
            candidate_curve.append(float(torch.max(candidate[row, :, central_index])))
        source_array = np.asarray(source_curve)
        candidate_array = np.asarray(candidate_curve)
        source_centered = source_array - source_array.mean()
        candidate_centered = candidate_array - candidate_array.mean()
        cosine = float(
            np.dot(source_centered, candidate_centered)
            / (np.linalg.norm(source_centered) * np.linalg.norm(candidate_centered) + 1e-12)
        )
        source_pref = int(ANGLES[int(np.argmax(source_array))])
        candidate_pref = int(ANGLES[int(np.argmax(candidate_array))])
        shift = abs(candidate_pref - source_pref) % 360
        shift = min(shift, 360 - shift)
        angles_rad = np.radians(np.asarray(ANGLES))
        source_vector = np.sum(source_centered * np.exp(1j * angles_rad))
        candidate_vector = np.sum(candidate_centered * np.exp(1j * angles_rad))
        result[str(intensity)] = {
            "source_curve": source_curve,
            "candidate_curve": candidate_curve,
            "curve_cosine": float(np.clip(cosine, -1.0, 1.0)),
            "source_preferred_direction": source_pref,
            "candidate_preferred_direction": candidate_pref,
            "preferred_direction_shift_degrees": int(shift),
            "source_tuning_vector_magnitude": float(abs(source_vector)),
            "candidate_tuning_vector_magnitude": float(abs(candidate_vector)),
            "tuning_vector_magnitude_change": float(abs(candidate_vector) - abs(source_vector)),
        }
    return result


def global_metrics(candidate, source, block_mask, replacement_mask, response_margin, dataset, central_index):
    block_nrmse = normalized_rms(candidate[..., block_mask], source[..., block_mask])
    return {
        "replacement_nodes": int(replacement_mask.sum()),
        "all_node_nrmse": normalized_rms(candidate, source),
        "block_nrmse": block_nrmse,
        "unreplaced_nrmse": normalized_rms(candidate[..., ~replacement_mask], source[..., ~replacement_mask]),
        "max_abs_error": float(torch.max(torch.abs(candidate - source))),
        "terminal_max_abs_error": float(torch.max(torch.abs(candidate[:, -1] - source[:, -1]))),
        "finite": bool(torch.isfinite(candidate).all()),
        "ordinary_passes": bool(block_nrmse <= response_margin),
        "tuning": tuning_metrics(candidate, source, dataset, central_index),
    }


def run(model_id: str = MODEL_ID, output_filename: str = "d1b_global_holdout.json") -> dict:
    started = time.perf_counter()
    margins_record = json.loads((DATA_ROOT / "d1b_source_ensemble.json").read_text())
    calibration = json.loads((DATA_ROOT / "d1b_local_calibration.json").read_text())
    local_margin = float(margins_record["margins"]["local_derivative"]["selected_margin"])
    response_margin = float(margins_record["margins"]["block_response"]["selected_margin"])
    decoder_margin = float(margins_record["margins"]["decoder"]["selected_margin"])
    selected_gamma = float(calibration["selected_shunt"]["gamma"])

    dataset = motion_dataset()
    table = dataset.arg_df.reset_index(drop=True)
    intensity_rows = {
        str(intensity): table.index[table["intensity"] == intensity].to_numpy()
        for intensity in (0, 1)
    }
    movie = torch.stack([dataset[index] for index in range(len(dataset))])[:, :, None, :]
    view = flyvis.NetworkView(flyvis.results_dir / f"flow/0000/{model_id}")
    network = view.init_network()
    topology_before = topology_digest(network)
    types = np.asarray(network.connectome.nodes.type[:]).astype(str)
    u = np.asarray(network.connectome.nodes.u[:])
    v = np.asarray(network.connectome.nodes.v[:])
    masks = {cell_type: torch.as_tensor(types == cell_type) for cell_type in CELL_TYPES}
    central = {
        cell_type: int(np.flatnonzero((types == cell_type) & (u == 0) & (v == 0)).item())
        for cell_type in CELL_TYPES
    }

    network.dynamics = PPNeuronIGRSynapses(activation={"type": "relu"})
    initial = network.steady_state(1.0, DT, movie.shape[0])
    full_input = prepare_input(network, movie)
    with torch.no_grad():
        source = network.forward(full_input, DT, state=clone_state(initial), as_states=False)
    previous = torch.cat([initial.nodes.activity[:, None], source[:, :-1]], dim=1)
    velocity = (source - previous) / DT
    decoder_map = view.init_decoder()
    decoder = decoder_map["flow"] if isinstance(decoder_map, dict) else decoder_map
    source_decoded = decode_chunked(decoder, source)

    family_specs = {
        "timescale": (lambda: MaskedTimescale(mode="adaptive", alpha=ALPHA, center=ALPHA_CENTER), ALPHA),
        "two_state": (lambda: MaskedTwoState(beta=BETA), BETA),
        "shunt": (lambda: MaskedShunt(gamma=selected_gamma), selected_gamma),
    }
    local = {}
    outcomes = {}
    exact = {}
    wrong = {}
    for cell_type in CELL_TYPES:
        block_mask = masks[cell_type]
        activity_array = previous[..., block_mask].cpu().numpy()
        velocity_array = velocity[..., block_mask].cpu().numpy()
        local[cell_type] = {}
        outcomes[cell_type] = {}
        for family, (factory, value) in family_specs.items():
            local_result = stratified_metrics(
                family, activity_array, velocity_array, value, intensity_rows, local_margin
            )
            local[cell_type][family] = local_result
            outcomes[cell_type][family] = []
            if not local_result["passes"]:
                outcomes[cell_type][family].append({"classification": "G0", "reason": "checkpoint-008 local gate failed"})
                continue
            indices = np.flatnonzero(types == cell_type)
            for fraction in FRACTIONS:
                replacement_mask = balanced_mask(network, indices, fraction)
                candidate = execute(network, factory(), replacement_mask, initial, full_input)
                decoded = decode_chunked(decoder, candidate)
                ordinary = global_metrics(
                    candidate, source, block_mask, replacement_mask, response_margin, dataset, central[cell_type]
                )
                decoded_result = decoder_metrics(decoded, source_decoded, dataset, decoder_margin)
                classification = "G1" if ordinary["ordinary_passes"] and decoded_result["passes"] else "G2"
                outcomes[cell_type][family].append({
                    "fraction": fraction,
                    "classification": classification,
                    "ordinary": ordinary,
                    "decoder": decoded_result,
                })
                del candidate, decoded
                gc.collect()

        full_mask = balanced_mask(network, np.flatnonzero(types == cell_type), 1.0)
        exact_activity = execute(
            network,
            MaskedTimescale(mode="adaptive", alpha=0.0, center=ALPHA_CENTER),
            full_mask,
            initial,
            full_input,
        )
        exact_decoded = decode_chunked(decoder, exact_activity)
        exact[cell_type] = {
            "ordinary": global_metrics(exact_activity, source, block_mask, full_mask, response_margin, dataset, central[cell_type]),
            "decoder": decoder_metrics(exact_decoded, source_decoded, dataset, decoder_margin),
        }
        wrong_activity = execute(network, MaskedShunt(gamma=WRONG_GAMMA), full_mask, initial, full_input)
        wrong_decoded = decode_chunked(decoder, wrong_activity)
        wrong[cell_type] = {
            "local": stratified_metrics("shunt", activity_array, velocity_array, WRONG_GAMMA, intensity_rows, local_margin),
            "ordinary": global_metrics(wrong_activity, source, block_mask, full_mask, response_margin, dataset, central[cell_type]),
            "decoder": decoder_metrics(wrong_decoded, source_decoded, dataset, decoder_margin),
        }
        del exact_activity, exact_decoded, wrong_activity, wrong_decoded
        gc.collect()

    topology_after = topology_digest(network)
    exact_zero = all(
        row["ordinary"]["max_abs_error"] == 0.0 and row["decoder"]["max_abs_error"] == 0.0
        for row in exact.values()
    )
    gates = {
        "prerequisite_source_margin_pass": margins_record["status"] == "PASS",
        "prerequisite_local_calibration_pass": calibration["status"] == "PASS",
        "source_and_decoder_finite": bool(torch.isfinite(source).all() and torch.isfinite(source_decoded).all()),
        "exact_shams_zero": exact_zero,
        "wrong_controls_locally_rejected": all(not row["local"]["passes"] for row in wrong.values()),
        "topology_unchanged": topology_before == topology_after,
    }
    classifications = [
        row["classification"]
        for block in outcomes.values()
        for family in block.values()
        for row in family
    ]
    result = {
        "schema_version": "0.1.0",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "boundary": f"checkpoint-{model_id} exploratory twelve-direction global/decoder holdout; no causal endpoint or biological claim",
        "frozen_design": {
            "model": model_id,
            "cell_types": list(CELL_TYPES),
            "fractions": list(FRACTIONS),
            "angles": list(ANGLES),
            "intensities": [0, 1],
            "local_margin": local_margin,
            "response_margin": response_margin,
            "decoder_margin": decoder_margin,
            "selected_gamma": selected_gamma,
        },
        "local": local,
        "outcomes": outcomes,
        "exact": exact,
        "wrong": wrong,
        "classification_counts": {name: classifications.count(name) for name in ("G0", "G1", "G2")},
        "gates": gates,
        "runtime": {
            "seconds": time.perf_counter() - started,
            "max_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "device": str(flyvis.device),
        },
    }
    output = DATA_ROOT / output_filename
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    result["integrity_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", default=MODEL_ID)
    parser.add_argument("--output-filename", default="d1b_global_holdout.json")
    args = parser.parse_args()
    result = run(args.model_id, args.output_filename)
    print(json.dumps({
        "status": result["status"],
        "classification_counts": result["classification_counts"],
        "local_passes": {
            block: {family: row["passes"] for family, row in families.items()}
            for block, families in result["local"].items()
        },
        "gates": result["gates"],
        "runtime": result["runtime"],
        "integrity_sha256": result["integrity_sha256"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
