"""Power and precision (section 6), computed after validation and before any confirmatory estimate."""

import numpy as np
import pandas as pd
from scipy import optimize

from ratchet import decision, resample

Z = 2.80  # 1.96 + 0.84: two-sided alpha 0.05, 80% power


def mde(sd: float, n_early: int, n_stayer: int) -> float:
    return float(Z * sd * np.sqrt(1 / n_early + 1 / n_stayer))


def sav_rate_sd(res: pd.DataFrame) -> float:
    """Mean of the yearly cross-ACO SDs of the savings rate, PY2016-PY2018."""
    return float(res[res.py.between(2016, 2018)].groupby("py").sav_rate.std().mean())


def simulated_power(sd: float, shift: float, early: np.ndarray, cohort: np.ndarray, n_datasets: int, n_perm: int, seed: int) -> float:
    """Share of normal datasets with the given shift in which the stratified permutation test gives p < 0.05."""
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_datasets):
        y = rng.normal(0, sd, early.size) + shift * early
        null = resample.permutation_null(y, early, cohort, n_perm, rng)
        hits += resample.p_value(resample.difference(y, early, cohort), null) < 0.05
    return hits / n_datasets


def h3_precision(design: decision.Design, n_datasets: int, seed: int, coefficient: float = 0.5, settings: decision.Settings = decision.REDUCED, workers: int = 1) -> dict:
    """For each core predictor: outcomes simulated with that coefficient = 0.5 and the others 0, intercept matching the
    observed early-renewal share; share of datasets whose 95% credible interval excludes zero in the predicted direction."""
    rng = np.random.default_rng([seed, 6])
    share = design.y.mean()
    out = {}
    for k, predictor in enumerate(decision.CORE):
        if predictor not in design.predictors:
            continue
        x = (design.own_obs - design.own_center) / design.own_scale if predictor == "own" else design.x[predictor]
        a = optimize.brentq(lambda a, x=x: np.mean(1 / (1 + np.exp(-(a + coefficient * x)))) - share, -20, 20)
        ys = rng.binomial(1, 1 / (1 + np.exp(-(a + coefficient * x))), size=(n_datasets, x.size))
        seeds = np.random.SeedSequence([seed, 6, k]).generate_state(n_datasets)
        intervals = _interval_refits(design, ys, seeds, predictor, settings, workers)
        lo, hi = intervals[:, 0], intervals[:, 1]
        detected = lo > 0 if decision.PREDICTED_SIGN[predictor] > 0 else hi < 0
        out[predictor] = {"coefficient": coefficient, "detection_share": float(detected.mean()), "median_width": float(np.median(hi - lo)), "n_datasets": n_datasets}
    return out


def _interval_refits(design, ys, seeds, predictor, settings, workers) -> np.ndarray:
    results = decision.refit_many(design, ys, seeds, settings, workers, quantiles=True)
    return np.array([q[f"b_{predictor}"] for q, _ in results])
