"""Group comparisons (sections 5.1, 5.2): Bayesian bootstrap posterior and stratified permutation significance.

The estimand is the within-cohort difference in means, early renewers minus stayers, averaged over cohorts with weights
proportional to each cohort's number of early renewers. Under the Bayesian bootstrap (Rubin 1981) its posterior mean
equals the observed difference, so the permutation test of the posterior mean shuffles labels and recomputes that
difference directly.
"""

import numpy as np


def _cells(early: np.ndarray, cohort: np.ndarray):
    for c in np.unique(cohort):
        in_c = cohort == c
        yield c, in_c & early, in_c & ~early


def cohort_weights(early: np.ndarray, cohort: np.ndarray) -> dict:
    n_early = early.sum()
    return {c: e.sum() / n_early for c, e, _ in _cells(early, cohort)}


def difference(y: np.ndarray, early: np.ndarray, cohort: np.ndarray, stat=np.mean) -> float:
    w = cohort_weights(early, cohort)
    return float(sum(w[c] * (stat(y[e]) - stat(y[s])) for c, e, s in _cells(early, cohort) if w[c] > 0))


def bayesian_bootstrap(y: np.ndarray, early: np.ndarray, cohort: np.ndarray, n_draws: int, rng: np.random.Generator, median: bool = False) -> np.ndarray:
    """Posterior draws of the weighted difference: Dirichlet(1, ..., 1) weights within each cohort-by-group cell."""
    w = cohort_weights(early, cohort)
    total = np.zeros(n_draws)
    for c, e, s in _cells(early, cohort):
        if w[c] == 0:
            continue
        cell_stats = []
        for members in (e, s):
            values = y[members]
            g = rng.standard_gamma(1.0, size=(n_draws, values.size))
            weights = g / g.sum(1, keepdims=True)
            if median:
                order = np.argsort(values)
                cum = np.cumsum(weights[:, order], axis=1)
                cell_stats.append(values[order][(cum < 0.5).sum(1)])
            else:
                cell_stats.append(weights @ values)
        total += w[c] * (cell_stats[0] - cell_stats[1])
    return total


def permutation_null(y: np.ndarray, early: np.ndarray, cohort: np.ndarray, n_perm: int, rng: np.random.Generator, stat=np.mean) -> np.ndarray:
    """Null distribution of `difference` with early-renewer labels shuffled within cohort."""
    null = np.empty(n_perm)
    labels = early.copy()
    groups = [np.flatnonzero(cohort == c) for c in np.unique(cohort)]
    for i in range(n_perm):
        for idx in groups:
            labels[idx] = rng.permutation(early[idx])
        null[i] = difference(y, labels, cohort, stat)
    return null


def p_value(observed: float, null: np.ndarray) -> float:
    """Two-sided resampling p-value, (1 + #{|null| >= |observed|}) / (1 + n) (section 5)."""
    tol = 1e-12 * max(1.0, abs(observed))
    return float((1 + np.sum(np.abs(null) >= abs(observed) - tol)) / (1 + null.size))


def compare(y, early, cohort, n_resamples: int, seed: int, median: bool = False) -> dict:
    """Section 5.1 for one variable: drops missing values (counted), then posterior summary and permutation p."""
    y, early, cohort = np.asarray(y, float), np.asarray(early, bool), np.asarray(cohort)
    keep = ~np.isnan(y)
    excluded = {"early": int((~keep & early).sum()), "stayer": int((~keep & ~early).sum())}
    y, early, cohort = y[keep], early[keep], cohort[keep]
    rng = np.random.default_rng(seed)
    stat = np.median if median else np.mean
    draws = bayesian_bootstrap(y, early, cohort, n_resamples, rng, median=median)
    observed = difference(y, early, cohort, stat)
    null = permutation_null(y, early, cohort, n_resamples, rng, stat)
    return {
        "n_early": int(early.sum()),
        "n_stayer": int((~early).sum()),
        "excluded": excluded,
        "observed": observed,
        "posterior_mean": float(draws.mean()),
        "eti95": [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))],
        "p_positive": float((draws > 0).mean()),
        "p_value": p_value(observed, null),
        "n_resamples": n_resamples,
        "seed": seed,
    }
