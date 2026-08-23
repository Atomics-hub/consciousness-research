"""Checkpoint-009 D1B block-impulse and frozen-decoder effect holdout."""

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
from flyvis.datasets.moving_bar import MovingEdge  # noqa: E402
from flyvis.network.dynamics import PPNeuronIGRSynapses  # noqa: E402
from work.connectome_substitution_gate.flyvis_mixed_dynamics_smoke import topology_digest  # noqa: E402
from work.d1_exploratory_calibration import MaskedTimescale, clone_state, normalized_rms, prepare_input  # noqa: E402
from work.d1_two_state_candidate import MaskedTwoState, candidate_initial  # noqa: E402
from work.d1b_local_calibration import ALPHA, ALPHA_CENTER, BETA, MaskedShunt  # noqa: E402
from work.d1b_source_ensemble import CELL_TYPES, DT, decode_chunked, motion_dataset  # noqa: E402


MODEL_ID = "009"
PERTURBATION_FRAME = 25
PERTURBATION_DELTA = 0.01
PERTURBATION_CELLS = ((0, 0), (90, 1), (180, 0), (270, 1))


def run_system(network, dynamics, initial, full_input, mask, perturb: bool, dt: float, perturbation_frame: int):
    if hasattr(dynamics, "set_mask"):
        dynamics.set_mask(mask)
    network.dynamics = dynamics
    network.clear_state_hooks()
    state = candidate_initial(network, initial) if isinstance(dynamics, MaskedTwoState) else clone_state(initial)
    counter = {"frame": 0}
    if perturb:
        def impulse(current_state):
            if counter["frame"] == perturbation_frame:
                activity = current_state.nodes.activity.clone()
                activity[..., mask] += PERTURBATION_DELTA
                current_state.nodes.activity = activity
            counter["frame"] += 1
            return current_state
        network.register_state_hook(impulse)
    with torch.no_grad():
        result = network.forward(full_input, dt, state=state, as_states=False)
    network.clear_state_hooks()
    return result


def effect_metrics(candidate: torch.Tensor, source: torch.Tensor, block_mask: torch.Tensor, margin: float) -> dict:
    difference = candidate - source
    left = candidate.reshape(-1)
    right = source.reshape(-1)
    cosine = float(
        torch.dot(left, right)
        / (torch.linalg.vector_norm(left) * torch.linalg.vector_norm(right) + 1e-12)
    )
    active = torch.abs(source) > 1e-9
    sign_agreement = float(
        (torch.sign(candidate[active]) == torch.sign(source[active])).float().mean()
    ) if bool(active.any()) else float("nan")
    nrmse = normalized_rms(candidate, source)
    return {
        "effect_nrmse": nrmse,
        "block_effect_nrmse": normalized_rms(candidate[..., block_mask], source[..., block_mask]),
        "effect_cosine": float(np.clip(cosine, -1.0, 1.0)),
        "effect_sign_agreement_nonzero_source": sign_agreement,
        "source_effect_rms": float(torch.sqrt(torch.mean(source**2))),
        "candidate_effect_rms": float(torch.sqrt(torch.mean(candidate**2))),
        "max_abs_effect_error": float(torch.max(torch.abs(difference))),
        "passes": bool(nrmse <= margin),
    }


def factory(family: str, gamma: float):
    if family == "timescale":
        return MaskedTimescale(mode="adaptive", alpha=ALPHA, center=ALPHA_CENTER)
    if family == "two_state":
        return MaskedTwoState(beta=BETA)
    if family == "shunt":
        return MaskedShunt(gamma=gamma)
    raise ValueError(family)


def run(
    dt: float = DT,
    output_filename: str = "d1b_causal_replication.json",
    model_id: str = MODEL_ID,
    replication_filename: str = "d1b_global_replication.json",
) -> dict:
    started = time.perf_counter()
    margins_record = json.loads((DATA_ROOT / "d1b_source_ensemble.json").read_text())
    calibration = json.loads((DATA_ROOT / "d1b_local_calibration.json").read_text())
    replication = json.loads((DATA_ROOT / replication_filename).read_text())
    response_margin = float(margins_record["margins"]["block_response"]["selected_margin"])
    decoder_margin = float(margins_record["margins"]["decoder"]["selected_margin"])
    gamma = float(calibration["selected_shunt"]["gamma"])

    dataset = motion_dataset() if dt == DT else MovingEdge(
        offsets=[-10, 11], intensities=[0, 1], speeds=[19], height=80,
        post_pad_mode="continue", t_pre=0.5, t_post=0.5, dt=dt,
        angles=list(range(0, 360, 30)),
    )
    table = dataset.arg_df.reset_index(drop=True)
    selected_rows = [
        table.index[(table["angle"] == angle) & (table["intensity"] == intensity)].item()
        for angle, intensity in PERTURBATION_CELLS
    ]
    movie = torch.stack([dataset[index] for index in selected_rows])[:, :, None, :]
    view = flyvis.NetworkView(flyvis.results_dir / f"flow/0000/{model_id}")
    network = view.init_network()
    topology_before = topology_digest(network)
    types = np.asarray(network.connectome.nodes.type[:]).astype(str)
    decoder_map = view.init_decoder()
    decoder = decoder_map["flow"] if isinstance(decoder_map, dict) else decoder_map

    perturbation_frame = int(round(PERTURBATION_FRAME * DT / dt))
    network.dynamics = PPNeuronIGRSynapses(activation={"type": "relu"})
    initial = network.steady_state(1.0, dt, movie.shape[0])
    full_input = prepare_input(network, movie)
    outcomes = {}
    exact = {}
    for cell_type in CELL_TYPES:
        mask = torch.as_tensor(types == cell_type)
        source_base = run_system(
            network, PPNeuronIGRSynapses(activation={"type": "relu"}), initial, full_input, mask, False, dt, perturbation_frame
        )
        source_perturbed = run_system(
            network, PPNeuronIGRSynapses(activation={"type": "relu"}), initial, full_input, mask, True, dt, perturbation_frame
        )
        source_effect = source_perturbed - source_base
        source_decoded_base = decode_chunked(decoder, source_base)
        source_decoded_perturbed = decode_chunked(decoder, source_perturbed)
        source_decoder_effect = source_decoded_perturbed - source_decoded_base

        exact_base = run_system(
            network, MaskedTimescale(mode="adaptive", alpha=0.0, center=ALPHA_CENTER), initial, full_input, mask, False, dt, perturbation_frame
        )
        exact_perturbed = run_system(
            network, MaskedTimescale(mode="adaptive", alpha=0.0, center=ALPHA_CENTER), initial, full_input, mask, True, dt, perturbation_frame
        )
        exact_decoder_base = decode_chunked(decoder, exact_base)
        exact_decoder_perturbed = decode_chunked(decoder, exact_perturbed)
        exact[cell_type] = {
            "ordinary_nrmse": normalized_rms(exact_base, source_base),
            "neural_effect": effect_metrics(exact_perturbed - exact_base, source_effect, mask, response_margin),
            "decoder_effect": effect_metrics(
                exact_decoder_perturbed - exact_decoder_base,
                source_decoder_effect,
                torch.ones(source_decoder_effect.shape[-1], dtype=torch.bool),
                decoder_margin,
            ),
        }

        outcomes[cell_type] = {}
        for family in ("timescale", "two_state", "shunt"):
            replicated_rows = replication["outcomes"][cell_type][family]
            eligible = bool(
                replicated_rows
                and replicated_rows[-1].get("fraction") == 1.0
                and replicated_rows[-1]["classification"] == "G1"
            )
            if not eligible:
                outcomes[cell_type][family] = {
                    "classification": "NOT_TESTED",
                    "reason": f"checkpoint-{model_id} full-replacement ordinary/decoder result was not G1",
                }
                continue
            candidate_base = run_system(network, factory(family, gamma), initial, full_input, mask, False, dt, perturbation_frame)
            candidate_perturbed = run_system(network, factory(family, gamma), initial, full_input, mask, True, dt, perturbation_frame)
            candidate_effect = candidate_perturbed - candidate_base
            candidate_decoded_base = decode_chunked(decoder, candidate_base)
            candidate_decoded_perturbed = decode_chunked(decoder, candidate_perturbed)
            candidate_decoder_effect = candidate_decoded_perturbed - candidate_decoded_base
            neural = effect_metrics(candidate_effect, source_effect, mask, response_margin)
            decoder_effect = effect_metrics(
                candidate_decoder_effect,
                source_decoder_effect,
                torch.ones(source_decoder_effect.shape[-1], dtype=torch.bool),
                decoder_margin,
            )
            classification = "G1" if neural["passes"] and decoder_effect["passes"] else "G3"
            outcomes[cell_type][family] = {
                "classification": classification,
                "ordinary_nrmse": normalized_rms(candidate_base, source_base),
                "neural_effect": neural,
                "decoder_effect": decoder_effect,
            }
            del candidate_base, candidate_perturbed, candidate_effect, candidate_decoded_base, candidate_decoded_perturbed
            gc.collect()
        del source_base, source_perturbed, source_effect, source_decoded_base, source_decoded_perturbed
        gc.collect()

    topology_after = topology_digest(network)
    exact_zero = all(
        row["ordinary_nrmse"] == 0.0
        and row["neural_effect"]["effect_nrmse"] == 0.0
        and row["decoder_effect"]["effect_nrmse"] == 0.0
        for row in exact.values()
    )
    tested = [
        row for families in outcomes.values() for row in families.values()
        if row["classification"] != "NOT_TESTED"
    ]
    gates = {
        "same_checkpoint_global_gate_pass": replication["status"] == "PASS",
        "at_least_one_eligible_candidate": bool(tested),
        "exact_shams_zero": exact_zero,
        "source_effects_nonzero": all(row["neural_effect"]["source_effect_rms"] > 0 for row in exact.values()),
        "topology_unchanged": topology_before == topology_after,
    }
    classifications = [row["classification"] for row in tested]
    result = {
        "schema_version": "0.1.0",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "boundary": f"checkpoint-{model_id} exploratory activity-impulse effect test; not a biological intervention",
        "frozen_design": {
            "model": model_id,
            "cells": [list(cell) for cell in PERTURBATION_CELLS],
            "frame": perturbation_frame,
            "time_seconds": perturbation_frame * dt,
            "delta": PERTURBATION_DELTA,
            "dt": dt,
            "neural_effect_margin": response_margin,
            "decoder_effect_margin": decoder_margin,
        },
        "exact": exact,
        "outcomes": outcomes,
        "classification_counts": {name: classifications.count(name) for name in ("G1", "G3")},
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
    parser.add_argument("--dt", type=float, default=DT)
    parser.add_argument("--output-filename", default="d1b_causal_replication.json")
    parser.add_argument("--model-id", default=MODEL_ID)
    parser.add_argument("--replication-filename", default="d1b_global_replication.json")
    args = parser.parse_args()
    result = run(args.dt, args.output_filename, args.model_id, args.replication_filename)
    print(json.dumps({
        "status": result["status"],
        "classification_counts": result["classification_counts"],
        "gates": result["gates"],
        "runtime": result["runtime"],
        "integrity_sha256": result["integrity_sha256"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
