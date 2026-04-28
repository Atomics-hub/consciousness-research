from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PairedResult:
    metric: str
    condition_a: str
    condition_b: str
    mean_a: float
    mean_b: float
    mean_diff: float
    median_diff: float
    ci_low: float
    ci_high: float
    cohen_dz: float
    p_value: float
    n_pairs: int


def paired_differences(a, b) -> np.ndarray:
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    if a_arr.shape != b_arr.shape:
        raise ValueError("Paired arrays must have the same shape.")
    return a_arr - b_arr


def paired_bootstrap_ci(
    a,
    b,
    n_bootstrap: int = 10000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    diffs = paired_differences(a, b)
    if len(diffs) == 0:
        return 0.0, 0.0

    rng = np.random.default_rng(seed)
    means = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        sample = rng.choice(diffs, size=len(diffs), replace=True)
        means[i] = float(np.mean(sample))

    alpha = (1.0 - ci) / 2.0
    return (
        float(np.quantile(means, alpha)),
        float(np.quantile(means, 1.0 - alpha)),
    )


def paired_cohen_dz(a, b) -> float:
    diffs = paired_differences(a, b)
    if len(diffs) < 2:
        return 0.0
    sd = float(np.std(diffs, ddof=1))
    if sd < 1e-12:
        return 0.0
    return float(np.mean(diffs) / sd)


def sign_flip_pvalue(a, b, n_permutations: int = 10000, seed: int = 42) -> float:
    diffs = paired_differences(a, b)
    if len(diffs) == 0:
        return 1.0

    observed = abs(float(np.mean(diffs)))
    if observed < 1e-12:
        return 1.0

    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_permutations):
        signs = rng.choice((-1.0, 1.0), size=len(diffs), replace=True)
        if abs(float(np.mean(diffs * signs))) >= observed:
            count += 1
    return float((count + 1) / (n_permutations + 1))


def compare_paired(
    metric: str,
    condition_a: str,
    condition_b: str,
    values_a,
    values_b,
    bootstrap_seed: int = 42,
    permutation_seed: int = 43,
) -> PairedResult:
    a_arr = np.asarray(values_a, dtype=float)
    b_arr = np.asarray(values_b, dtype=float)
    diffs = paired_differences(a_arr, b_arr)
    ci_low, ci_high = paired_bootstrap_ci(
        a_arr,
        b_arr,
        seed=bootstrap_seed,
    )
    return PairedResult(
        metric=metric,
        condition_a=condition_a,
        condition_b=condition_b,
        mean_a=float(np.mean(a_arr)),
        mean_b=float(np.mean(b_arr)),
        mean_diff=float(np.mean(diffs)),
        median_diff=float(np.median(diffs)),
        ci_low=ci_low,
        ci_high=ci_high,
        cohen_dz=paired_cohen_dz(a_arr, b_arr),
        p_value=sign_flip_pvalue(a_arr, b_arr, seed=permutation_seed),
        n_pairs=int(len(diffs)),
    )


def holm_bonferroni(p_values, alpha: float = 0.05) -> list[bool]:
    p_arr = np.asarray(p_values, dtype=float)
    order = np.argsort(p_arr)
    significant = np.zeros(len(p_arr), dtype=bool)

    for rank, idx in enumerate(order):
        threshold = alpha / (len(p_arr) - rank)
        if p_arr[idx] <= threshold:
            significant[idx] = True
        else:
            break

    return [bool(x) for x in significant]
