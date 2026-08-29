"""Synthetic fixtures for the Paper 10 intervention-coverage barrier.

The script is deterministic given the frozen JSON specification.  It avoids
biological-model outcomes and writes a machine-readable exploratory result.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Callable

import numpy as np


ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "frozen_spec.json"
RESULT_PATH = ROOT / "g0d_result.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def cartesian_grid(low: float, high: float, points_per_axis: int, dimension: int) -> np.ndarray:
    axis = np.linspace(low, high, points_per_axis, dtype=float)
    return np.asarray(list(itertools.product(axis, repeat=dimension)), dtype=float)


def distance_to_set(points: np.ndarray, samples: np.ndarray, chunk_size: int = 4096) -> np.ndarray:
    """Minimum l-infinity distance from each point to a finite sample set."""

    points = np.atleast_2d(np.asarray(points, dtype=float))
    samples = np.atleast_2d(np.asarray(samples, dtype=float))
    if samples.shape[0] == 0:
        raise ValueError("samples must be nonempty")
    distances: list[np.ndarray] = []
    for start in range(0, points.shape[0], chunk_size):
        chunk = points[start : start + chunk_size]
        pairwise = np.max(np.abs(chunk[:, None, :] - samples[None, :, :]), axis=2)
        distances.append(pairwise.min(axis=1))
    return np.concatenate(distances)


def approximate_fill_distance(samples: np.ndarray, domain_grid: np.ndarray) -> tuple[float, np.ndarray]:
    distances = distance_to_set(domain_grid, samples)
    index = int(np.argmax(distances))
    return float(distances[index]), domain_grid[index].copy()


def source_rollout(inputs: np.ndarray, decay: float) -> np.ndarray:
    inputs = np.asarray(inputs, dtype=float)
    states = np.zeros(inputs.shape[0] + 1, dtype=float)
    for time, value in enumerate(inputs):
        states[time + 1] = decay * states[time] + value
    return states


def candidate_rollout(
    inputs: np.ndarray,
    decay: float,
    bump: Callable[[float, float], float] | None = None,
) -> np.ndarray:
    inputs = np.asarray(inputs, dtype=float)
    states = np.zeros(inputs.shape[0] + 1, dtype=float)
    for time, value in enumerate(inputs):
        residual = 0.0 if bump is None else float(bump(states[time], float(value)))
        states[time + 1] = decay * states[time] + value + residual
    return states


def collect_source_state_input_pairs(inputs: np.ndarray, decay: float) -> np.ndarray:
    pairs = []
    for trajectory in np.asarray(inputs, dtype=float):
        states = source_rollout(trajectory, decay)
        pairs.extend((states[t], trajectory[t]) for t in range(trajectory.shape[0]))
    return np.asarray(pairs, dtype=float)


def find_reachable_unseen_center(
    tested_pairs: np.ndarray,
    input_bound: float,
    points_per_axis: int,
) -> tuple[np.ndarray, float]:
    """Find a point reachable after one lead-in input and far from tested pairs.

    For a proposed center (x*, u*), the lead-in input x* reaches x* from zero.
    The lead-in pair (0, x*) is included in the clearance calculation so the
    candidate remains identical until it arrives at the unseen center.
    """

    grid = cartesian_grid(-input_bound, input_bound, points_per_axis, 2)
    best_center = None
    best_clearance = -np.inf
    for start in range(0, grid.shape[0], 2048):
        chunk = grid[start : start + 2048]
        tested_clearance = distance_to_set(chunk, tested_pairs)
        lead_clearance = np.maximum(np.abs(chunk[:, 0]), np.abs(chunk[:, 1] - chunk[:, 0]))
        clearance = np.minimum(tested_clearance, lead_clearance)
        local_index = int(np.argmax(clearance))
        if clearance[local_index] > best_clearance:
            best_clearance = float(clearance[local_index])
            best_center = chunk[local_index].copy()
    if best_center is None or best_clearance <= 0:
        raise RuntimeError("failed to find an unseen reachable center")
    return best_center, best_clearance


def cone_bump(center: np.ndarray, support_radius: float, amplitude: float) -> Callable[[float, float], float]:
    center = np.asarray(center, dtype=float)

    def bump(state: float, value: float) -> float:
        distance = max(abs(state - center[0]), abs(value - center[1]))
        return amplitude * max(0.0, 1.0 - distance / support_radius)

    return bump


def markov_parameters(a: np.ndarray, b: np.ndarray, c: np.ndarray, count: int) -> np.ndarray:
    state = np.asarray(b, dtype=float)
    values = []
    for _ in range(count):
        values.append(float(np.asarray(c) @ state))
        state = np.asarray(a, dtype=float) @ state
    return np.asarray(values)


def linear_controls() -> dict:
    a = np.asarray([[0.72, 0.25], [0.0, 0.41]])
    b = np.asarray([1.0, -0.35])
    c = np.asarray([0.8, 0.3])
    transform = np.asarray([[1.2, 0.4], [-0.2, 0.9]])
    transform_inv = np.linalg.inv(transform)
    a_candidate = transform @ a @ transform_inv
    b_candidate = transform @ b
    c_candidate = c @ transform_inv
    source_markov = markov_parameters(a, b, c, 16)
    candidate_markov = markov_parameters(a_candidate, b_candidate, c_candidate, 16)

    matched_horizon = 8
    shift_a = np.zeros((matched_horizon + 1, matched_horizon + 1))
    for index in range(matched_horizon):
        shift_a[index + 1, index] = 1.0
    shift_b = np.zeros(matched_horizon + 1)
    shift_b[0] = 1.0
    shift_c = np.zeros(matched_horizon + 1)
    shift_c[-1] = 1.0
    delayed = markov_parameters(shift_a, shift_b, shift_c, matched_horizon + 2)

    return {
        "similarity_realization_max_abs_markov_error": float(np.max(np.abs(source_markov - candidate_markov))),
        "delayed_mismatch_matched_markov_count": matched_horizon,
        "delayed_mismatch_first_nonzero_index": int(np.flatnonzero(np.abs(delayed) > 0)[0]),
        "delayed_mismatch_markov_parameters": delayed.tolist(),
    }


def coverage_control(spec: dict) -> dict:
    cfg = spec["coverage_comparison"]
    dimension = int(cfg["dimension"])
    q = int(cfg["regular_grid_points_per_axis"])
    n = q**dimension
    evaluation_grid = cartesian_grid(0.0, 1.0, int(cfg["evaluation_grid_points_per_axis"]), dimension)
    regular = cartesian_grid(0.0, 1.0, q, dimension)
    regular_fill, regular_witness = approximate_fill_distance(regular, evaluation_grid)

    rng = np.random.default_rng(int(cfg["seed"]))
    random_fills = []
    for _ in range(int(cfg["random_repetitions"])):
        random_samples = rng.uniform(0.0, 1.0, size=(n, dimension))
        fill, _ = approximate_fill_distance(random_samples, evaluation_grid)
        random_fills.append(fill)
    random_fills_array = np.asarray(random_fills)
    median_random = float(np.median(random_fills_array))
    ratio = regular_fill / median_random
    threshold = float(cfg["success_ratio_regular_to_median_random"])

    return {
        "dimension": dimension,
        "budget": n,
        "regular_fill_distance_approx": regular_fill,
        "regular_witness": regular_witness.tolist(),
        "random_fill_distance_median_approx": median_random,
        "random_fill_distance_q05_q95_approx": np.quantile(random_fills_array, [0.05, 0.95]).tolist(),
        "regular_to_median_random_ratio": ratio,
        "required_ratio": threshold,
        "passes": bool(ratio <= threshold),
    }


def stateful_counterexample(spec: dict) -> dict:
    cfg = spec["stateful_counterexample"]
    rng = np.random.default_rng(int(cfg["seed"]))
    n = int(cfg["number_of_test_trajectories"])
    horizon = int(cfg["horizon"])
    decay = float(cfg["source_decay"])
    input_bound = float(cfg["input_bound"])
    amplitude = float(cfg["bump_amplitude"])
    tested_inputs = rng.uniform(-input_bound, input_bound, size=(n, horizon))
    tested_pairs = collect_source_state_input_pairs(tested_inputs, decay)
    center, clearance = find_reachable_unseen_center(
        tested_pairs, input_bound, int(cfg["search_grid_points_per_axis"])
    )
    support_radius = 0.9 * clearance
    bump = cone_bump(center, support_radius, amplitude)

    battery_max = 0.0
    for trajectory in tested_inputs:
        source = source_rollout(trajectory, decay)
        candidate = candidate_rollout(trajectory, decay, bump)
        battery_max = max(battery_max, float(np.max(np.abs(source - candidate))))

    unseen_inputs = np.zeros(horizon)
    unseen_inputs[0] = center[0]
    unseen_inputs[1] = center[1]
    unseen_source = source_rollout(unseen_inputs, decay)
    unseen_candidate = candidate_rollout(unseen_inputs, decay, bump)
    unseen_divergence = float(np.max(np.abs(unseen_source - unseen_candidate)))

    state_limit = input_bound / (1.0 - abs(decay))
    declared_domain = cartesian_grid(
        -state_limit,
        state_limit,
        int(cfg["search_grid_points_per_axis"]),
        1,
    )
    input_axis = np.linspace(-input_bound, input_bound, int(cfg["search_grid_points_per_axis"]))
    domain = np.asarray(
        [(state[0], value) for state in declared_domain for value in input_axis], dtype=float
    )
    fill_distance, fill_witness = approximate_fill_distance(tested_pairs, domain)
    bump_lipschitz = amplitude / support_radius
    certificate_bound = battery_max + bump_lipschitz * fill_distance
    threshold = float(spec["tolerances"]["causal_equivalence"])

    return {
        "tested_trajectories": n,
        "tested_state_input_pairs": int(tested_pairs.shape[0]),
        "center": center.tolist(),
        "clearance_from_tests_and_lead_in": clearance,
        "support_radius": support_radius,
        "bump_amplitude": amplitude,
        "bump_lipschitz_constant": bump_lipschitz,
        "battery_max_output_discrepancy": battery_max,
        "unseen_intervention": unseen_inputs.tolist(),
        "unseen_max_output_divergence": unseen_divergence,
        "approximate_declared_domain_fill_distance": fill_distance,
        "fill_distance_witness": fill_witness.tolist(),
        "lipschitz_certificate_upper_bound": certificate_bound,
        "equivalence_threshold": threshold,
        "certificate_passes": bool(certificate_bound <= threshold),
        "battery_indistinguishable": bool(battery_max <= float(spec["tolerances"]["exact"])),
        "unseen_witness_passes_minimum": bool(
            unseen_divergence >= float(cfg["minimum_unseen_output_divergence"])
        ),
    }


def sham_controls(spec: dict) -> dict:
    exact_tolerance = float(spec["tolerances"]["exact"])
    rng = np.random.default_rng(779)
    trajectories = rng.uniform(-0.1, 0.1, size=(128, 10))

    exact_error = 0.0
    hidden_output_error = 0.0
    wrong_interface_error = 0.0
    unreachable_output_error = 0.0
    for inputs in trajectories:
        source = source_rollout(inputs, 0.5)
        exact = candidate_rollout(inputs, 0.5, None)
        exact_error = max(exact_error, float(np.max(np.abs(source - exact))))

        # A hidden candidate coordinate can change arbitrarily while the visible
        # state and interface remain identical and independent of that coordinate.
        hidden = np.cumsum(np.square(inputs) + 1.0)
        del hidden
        hidden_output = candidate_rollout(inputs, 0.5, None)
        hidden_output_error = max(hidden_output_error, float(np.max(np.abs(source - hidden_output))))

        wrong_output = exact + 0.1
        wrong_interface_error = max(wrong_interface_error, float(np.max(np.abs(source - wrong_output))))

        unreachable_bump = cone_bump(np.asarray([0.8, 0.0]), 0.05, 0.2)
        unreachable = candidate_rollout(inputs, 0.5, unreachable_bump)
        unreachable_output_error = max(
            unreachable_output_error, float(np.max(np.abs(source - unreachable)))
        )

    cfg = spec["non_normal_control"]
    a = np.asarray([[float(cfg["decay"]), float(cfg["off_diagonal_gain"])], [0.0, float(cfg["decay"])]])
    state = np.asarray([0.0, float(cfg["local_impulse"])])
    outputs = []
    for _ in range(int(cfg["horizon"])):
        outputs.append(abs(float(state[0])))
        state = a @ state
    amplification = max(outputs) / float(cfg["local_impulse"])

    return {
        "exact_replacement_max_output_error": exact_error,
        "exact_replacement_passes": bool(exact_error <= exact_tolerance),
        "hidden_unobservable_max_output_error": hidden_output_error,
        "hidden_unobservable_passes": bool(hidden_output_error <= exact_tolerance),
        "unreachable_mismatch_max_output_error": unreachable_output_error,
        "unreachable_mismatch_passes": bool(unreachable_output_error <= exact_tolerance),
        "wrong_interface_max_output_error": wrong_interface_error,
        "wrong_interface_fails_as_required": bool(wrong_interface_error > exact_tolerance),
        "non_normal_amplification_ratio": amplification,
        "non_normal_passes": bool(amplification >= float(cfg["minimum_amplification_ratio"])),
    }


def dimensional_burden() -> list[dict]:
    lipschitz = 1.0
    epsilon = 0.05
    rows = []
    for dimension in (1, 2, 4, 8, 12):
        necessary = int(np.ceil((lipschitz / (2.0 * epsilon)) ** dimension))
        rows.append(
            {
                "dimension": dimension,
                "lipschitz_constant": lipschitz,
                "target_uniform_error": epsilon,
                "necessary_evaluation_lower_bound_unit_cube": necessary,
            }
        )
    return rows


def run() -> dict:
    spec = json.loads(SPEC_PATH.read_text())
    linear = linear_controls()
    coverage = coverage_control(spec)
    stateful = stateful_counterexample(spec)
    shams = sham_controls(spec)

    all_gates = [
        linear["similarity_realization_max_abs_markov_error"] <= spec["tolerances"]["exact"],
        linear["delayed_mismatch_first_nonzero_index"] == linear["delayed_mismatch_matched_markov_count"],
        coverage["passes"],
        stateful["battery_indistinguishable"],
        stateful["unseen_witness_passes_minimum"],
        not stateful["certificate_passes"],
        shams["exact_replacement_passes"],
        shams["hidden_unobservable_passes"],
        shams["unreachable_mismatch_passes"],
        shams["wrong_interface_fails_as_required"],
        shams["non_normal_passes"],
    ]
    result = {
        "schema_version": "1.0",
        "status": "exploratory_synthetic_result",
        "frozen_spec_sha256": sha256_file(SPEC_PATH),
        "linear_controls": linear,
        "coverage_comparison": coverage,
        "stateful_piecewise_linear_counterexample": stateful,
        "sham_controls": shams,
        "dimensional_burden": dimensional_burden(),
        "all_frozen_gates_pass": bool(all(all_gates)),
        "claim_ceiling": "Synthetic constructibility and an assumption audit only; no neural, biological, consciousness, identity, survival, or replaceability inference.",
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
