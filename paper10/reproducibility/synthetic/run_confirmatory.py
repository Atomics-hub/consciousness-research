"""Execute the frozen Paper 10 synthetic confirmatory packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import intervention_coverage as ic


ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "confirmatory_spec.json"
RESULT_PATH = ROOT / "confirmatory_result.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_packet(packet: dict, exact_tolerance: float, causal_threshold: float) -> dict:
    rng = np.random.default_rng(int(packet["seed"]))
    count = int(packet["test_trajectories"])
    horizon = int(packet["horizon"])
    decay = float(packet["decay"])
    input_bound = float(packet["input_bound"])
    amplitude = float(packet["bump_amplitude"])
    search_grid = int(packet["search_grid"])

    inputs = rng.uniform(-input_bound, input_bound, size=(count, horizon))
    tested_pairs = ic.collect_source_state_input_pairs(inputs, decay)
    center, clearance = ic.find_reachable_unseen_center(tested_pairs, input_bound, search_grid)
    support_radius = 0.9 * clearance
    bump = ic.cone_bump(center, support_radius, amplitude)

    battery_max = 0.0
    for trajectory in inputs:
        source = ic.source_rollout(trajectory, decay)
        candidate = ic.candidate_rollout(trajectory, decay, bump)
        battery_max = max(battery_max, float(np.max(np.abs(source - candidate))))

    unseen = np.zeros(horizon)
    unseen[0] = center[0]
    unseen[1] = center[1]
    source_unseen = ic.source_rollout(unseen, decay)
    candidate_unseen = ic.candidate_rollout(unseen, decay, bump)
    unseen_max = float(np.max(np.abs(source_unseen - candidate_unseen)))

    state_limit = input_bound / (1.0 - abs(decay))
    state_axis = np.linspace(-state_limit, state_limit, search_grid)
    input_axis = np.linspace(-input_bound, input_bound, search_grid)
    domain = np.asarray([(state, value) for state in state_axis for value in input_axis])
    fill_distance, fill_witness = ic.approximate_fill_distance(tested_pairs, domain)
    lipschitz = amplitude / support_radius
    bound = battery_max + lipschitz * fill_distance

    battery_pass = battery_max <= exact_tolerance
    unseen_pass = unseen_max >= causal_threshold
    certificate_rejects = bound > 0.01
    return {
        "packet_id": packet["packet_id"],
        "seed": packet["seed"],
        "tested_trajectories": count,
        "tested_state_input_pairs": int(tested_pairs.shape[0]),
        "center": center.tolist(),
        "clearance": clearance,
        "support_radius": support_radius,
        "battery_max_output_discrepancy": battery_max,
        "unseen_max_output_discrepancy": unseen_max,
        "approximate_fill_distance": fill_distance,
        "fill_distance_witness": fill_witness.tolist(),
        "lipschitz_certificate_upper_bound": bound,
        "battery_pass": bool(battery_pass),
        "unseen_pass": bool(unseen_pass),
        "certificate_rejects": bool(certificate_rejects),
        "packet_pass": bool(battery_pass and unseen_pass and certificate_rejects),
    }


def run_coverage_replication(cfg: dict, seed: int) -> dict:
    dimension = int(cfg["dimension"])
    q = int(cfg["grid_points_per_axis"])
    budget = q**dimension
    evaluation = ic.cartesian_grid(
        0.0, 1.0, int(cfg["evaluation_grid_points_per_axis"]), dimension
    )
    regular = ic.cartesian_grid(0.0, 1.0, q, dimension)
    regular_fill, _ = ic.approximate_fill_distance(regular, evaluation)
    rng = np.random.default_rng(int(seed))
    random_fills = []
    for _ in range(int(cfg["random_repetitions_per_seed"])):
        samples = rng.uniform(0.0, 1.0, size=(budget, dimension))
        fill, _ = ic.approximate_fill_distance(samples, evaluation)
        random_fills.append(fill)
    median_random = float(np.median(random_fills))
    ratio = regular_fill / median_random
    threshold = float(cfg["maximum_regular_to_median_random_ratio"])
    return {
        "seed": seed,
        "budget": budget,
        "regular_fill_distance_approx": regular_fill,
        "median_random_fill_distance_approx": median_random,
        "regular_to_median_random_ratio": ratio,
        "threshold": threshold,
        "passes": bool(ratio <= threshold),
    }


def run() -> dict:
    spec = json.loads(SPEC_PATH.read_text())
    exact = float(spec["exact_tolerance"])
    causal = float(spec["causal_discrepancy_threshold"])
    packets = [run_packet(packet, exact, causal) for packet in spec["packets"]]
    coverage_cfg = spec["coverage_replications"]
    coverage = [
        run_coverage_replication(coverage_cfg, int(seed)) for seed in coverage_cfg["seeds"]
    ]
    primary_pass = all(packet["packet_pass"] for packet in packets)
    secondary_pass = all(row["passes"] for row in coverage)
    result = {
        "schema_version": "1.0",
        "status": "confirmatory_synthetic_result",
        "confirmatory_spec_sha256": sha256_file(SPEC_PATH),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "packets": packets,
        "coverage_replications": coverage,
        "primary_conjunctive_gate_passes": bool(primary_pass),
        "secondary_conjunctive_gate_passes": bool(secondary_pass),
        "all_confirmatory_gates_pass": bool(primary_pass and secondary_pass),
        "independence_note": spec["independence_note"],
        "claim_ceiling": "Deterministic implementation transport only; the analytic proof, not repeated seeded fixtures, supports the general statement.",
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
