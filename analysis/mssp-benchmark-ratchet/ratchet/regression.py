"""Covariate-adjusted estimates (section 5.3; robustness item 1 of 5.5): robust Bayesian linear regression."""

import numpy as np
import pandas as pd
import pymc as pm

from ratchet import decision


def _design(frame: pd.DataFrame, column: str, adjusted: bool) -> tuple[np.ndarray, dict[str, np.ndarray], float, float, int]:
    cols = [column, "cohort", "grp"] + (["basic", "basic_level", "enhanced", "log_n_ab_2020"] if adjusted else [])
    data = frame.dropna(subset=[column] + (["log_n_ab_2020"] if adjusted else []))[cols].copy()
    if adjusted:
        data = data[data.enhanced.astype(bool) | data.basic_level.notna()]
    y = data[column].astype(float).to_numpy()
    mean, sd = float(y.mean()), float(y.std())
    x = {"early": (data.grp == "early").astype(float).to_numpy(), "cohort_2020": (data.cohort == "2020-01").astype(float).to_numpy()}
    if adjusted:
        # PY2021 track/level: BASIC A-B is the reference.
        x["basic_c_e"] = (data.basic.astype(bool) & data.basic_level.isin(["C", "D", "E"])).astype(float).to_numpy()
        x["enhanced"] = data.enhanced.astype(bool).astype(float).to_numpy()
        v = data.log_n_ab_2020.astype(float).to_numpy()
        x["log_n_ab_2020"] = (v - v.mean()) / v.std()
    return (y - mean) / sd, x, mean, sd, int(len(frame) - len(data))


def build_model(y: np.ndarray, x: dict[str, np.ndarray]) -> pm.Model:
    """Student-t errors; Normal(0, 1) intercept and coefficients; Exponential(1) scale; Gamma(2, 0.1) degrees of freedom."""
    with pm.Model() as model:
        mu = pm.Normal("intercept", 0, 1)
        for name, value in x.items():
            mu = mu + pm.Normal(f"b_{name}", 0, 1) * value
        pm.StudentT("y", nu=pm.Gamma("nu", alpha=2, beta=0.1), mu=mu, sigma=pm.Exponential("sigma", 1), observed=y)
    return model


def adjusted_difference(frame: pd.DataFrame, column: str, seed: int, adjusted: bool = False, full=decision.FULL, retry=decision.RETRY, cores: int = 4) -> dict:
    """Early-renewer coefficient for one variable, early renewers and stayers only, in SD units and in the variable's units."""
    compared = frame[frame.grp.isin(["early", "stayer"])]
    y, x, mean, sd, excluded = _design(compared, column, adjusted)
    model = build_model(y, x)
    names = [f"b_{n}" for n in x]
    idata = decision.fit(model, full, seed, cores)
    checks = decision.convergence(idata, names)
    attempts = 1
    if not checks["converged"]:
        idata, attempts = decision.fit(model, retry, seed + 1, cores), 2
        checks = decision.convergence(idata, names)
    b = np.asarray(idata["posterior"]["b_early"]).ravel()
    lo, hi = float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))
    return {
        "variable": column,
        "covariates": list(x),
        "n": int(y.size),
        "excluded": excluded,
        "b_early_sd_units": {"mean": float(b.mean()), "eti95": [lo, hi]},
        "b_early_units": {"mean": float(b.mean() * sd), "eti95": [lo * sd, hi * sd]},
        "convergence": {**checks, "attempts": attempts},
    }
