"""H3: Bayesian decision model for BASIC-track ACOs (section 5.4) and its resampling tests.

Core predictors carry predicted directions and are tested by direct simulation under the reduced model (a parametric
bootstrap): fit the model without predictor k, simulate early-renewal outcomes from its posterior, refit the full model
to each, and compare coefficient k's posterior mean with its value on the real outcomes. The label shuffle across the
whole model is reported as an overall test. Refits reuse one compiled model per process (pm.Data + pm.set_data).
"""

import logging
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm
from firthmodels import FirthLogisticRegression

from ratchet.resample import p_value

CORE = ("pull", "own", "basic_high")
ADJUSTMENT = ("cohort_2020", "log_n_ab_2020", "high_revenue", "prospective", "later_agreement")
CONTINUOUS = ("pull", "own", "log_n_ab_2020")
PREDICTED_SIGN = {"pull": 1, "own": 1, "basic_high": 1}

logging.getLogger("pymc").setLevel(logging.ERROR)


@dataclass(frozen=True)
class Settings:
    chains: int
    tune: int
    draws: int
    target_accept: float


FULL = Settings(4, 2000, 2000, 0.95)
RETRY = Settings(4, 2000, 4000, 0.99)
REDUCED = Settings(2, 1000, 1000, 0.95)
RHAT_MAX, ESS_MIN = 1.01, 400


@dataclass
class Design:
    """Model inputs: outcome, cohort, centered/scaled predictors, and the own-spending component with its error SD."""

    y: np.ndarray
    cohort: np.ndarray
    x: dict[str, np.ndarray]
    predictors: tuple[str, ...]
    own_obs: np.ndarray | None = None
    own_center: float = 0.0
    own_scale: float = 1.0
    sigma_v: float | None = None
    excluded: dict = field(default_factory=dict)


def make_design(frame: pd.DataFrame, sigma_v: float | None, include_own: bool = True, exclude: tuple[str, ...] = (), extra: tuple[str, ...] = ()) -> Design:
    """BASIC-track early renewers and stayers with every predictor present (section 5.4). Continuous predictors are
    centered and divided by 2 SD; binary predictors are centered (Gelman 2008). sigma_v=None uses own spending as
    observed (no measurement-error layer). `exclude` drops predictors (e.g. cohort in a one-cohort sample); `extra`
    adds binary columns of `frame` as further adjustment predictors (e.g. census region indicators)."""
    predictors = tuple(p for p in CORE + ADJUSTMENT + extra if (include_own or p != "own") and p not in exclude)
    sample = frame[frame.basic.astype(bool) & frame.grp.isin(["early", "stayer"])].copy()
    sample["cohort_2020"] = (sample.cohort == "2020-01").astype(float)
    needed = [p for p in predictors]
    complete = sample.dropna(subset=needed)
    excluded = (sample.loc[~sample.index.isin(complete.index), "grp"].value_counts().to_dict()) if len(complete) < len(sample) else {}
    x = {}
    for p in predictors:
        if p == "own":
            continue
        v = complete[p].astype(float).to_numpy()
        x[p] = (v - v.mean()) / (2 * v.std()) if p in CONTINUOUS else v - v.mean()
    own = complete.own.astype(float).to_numpy() if include_own else None
    return Design(
        y=(complete.grp == "early").astype(int).to_numpy(),
        cohort=complete.cohort.to_numpy(),
        x=x,
        predictors=predictors,
        own_obs=own,
        own_center=float(own.mean()) if include_own else 0.0,
        own_scale=float(2 * own.std()) if include_own else 1.0,
        sigma_v=sigma_v if include_own and sigma_v and sigma_v > 0 else None,
        excluded=excluded,
    )


def build_model(design: Design, drop: str | None = None, prior: str = "normal", keep_eta: bool = False) -> pm.Model:
    """Logistic regression with Normal(0, 1) (or Student-t(3, 0, 2.5)) coefficient priors and a Normal(-2.2, 1) intercept."""
    n = design.y.size
    with pm.Model() as model:
        y = pm.Data("y", design.y)
        # Centered predictors: the intercept is the log-odds at average values; prior centered at a 10% share.
        eta = pm.Normal("intercept", -2.2, 1)
        for name in design.predictors:
            if name == drop:
                continue
            b = pm.Normal(f"b_{name}", 0, 1) if prior == "normal" else pm.StudentT(f"b_{name}", nu=3, mu=0, sigma=2.5)
            if name == "own" and design.sigma_v is not None:
                # Latent true values, non-centered: observed = true + error, error ~ Normal(0, sigma_v).
                mu, tau = pm.Normal("own_mu", 0, 10), pm.HalfNormal("own_tau", 10)
                own_true = mu + tau * pm.Normal("own_z", 0, 1, shape=n)
                pm.Normal("own_obs", own_true, design.sigma_v, observed=design.own_obs)
                value = (own_true - design.own_center) / design.own_scale
            elif name == "own":
                value = (design.own_obs - design.own_center) / design.own_scale
            else:
                value = design.x[name]
            eta = eta + b * value
        if keep_eta:
            eta = pm.Deterministic("eta", eta)
        pm.Bernoulli("renew", logit_p=eta, observed=y)
    return model


def coefficient_names(design: Design, drop: str | None = None) -> list[str]:
    return [f"b_{p}" for p in design.predictors if p != drop]


def fit(model: pm.Model, settings: Settings, seed: int, cores: int = 1):
    with model:
        return pm.sample(
            draws=settings.draws,
            tune=settings.tune,
            chains=settings.chains,
            cores=cores,
            target_accept=settings.target_accept,
            random_seed=int(seed),
            progressbar=False,
            compute_convergence_checks=False,
        )


def convergence(idata, names: list[str]) -> dict:
    """R-hat <= 1.01, bulk and tail ESS >= 400 for every coefficient, and no divergent transitions."""
    summ = az.summary(idata, var_names=names + ["intercept"])
    divergent = int(idata["sample_stats"]["diverging"].sum())
    ok = bool((summ.r_hat <= RHAT_MAX).all() and (summ.ess_bulk >= ESS_MIN).all() and (summ.ess_tail >= ESS_MIN).all() and divergent == 0)
    return {
        "converged": ok,
        "max_rhat": float(summ.r_hat.max()),
        "min_ess_bulk": float(summ.ess_bulk.min()),
        "min_ess_tail": float(summ.ess_tail.min()),
        "divergent": divergent,
    }


def coefficient_summary(idata, names: list[str]) -> dict:
    post = idata["posterior"]
    out = {}
    for name in names:
        v = np.asarray(post[name]).ravel()
        out[name] = {"mean": float(v.mean()), "eti95": [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))], "p_positive": float((v > 0).mean())}
    return out


def fit_checked(design: Design, seed: int, prior: str = "normal", full: Settings = FULL, retry: Settings = RETRY, cores: int = 4) -> tuple:
    """Full-settings fit; one rerun with more draws and target acceptance 0.99 if the checks fail (section 5.4)."""
    model = build_model(design, prior=prior, keep_eta=True)
    names = coefficient_names(design)
    idata = fit(model, full, seed, cores)
    checks = convergence(idata, names)
    attempts = 1
    if not checks["converged"]:
        idata = fit(model, retry, seed + 1, cores)
        checks, attempts = convergence(idata, names), 2
    return idata, {**checks, "attempts": attempts}


# Refits: one compiled model per worker process.
_WORKER: dict = {}


def _init_worker(design: Design, reduced: Settings, quantiles: bool = False) -> None:
    logging.getLogger("pymc").setLevel(logging.ERROR)
    _WORKER.update(model=build_model(design), names=coefficient_names(design), reduced=reduced, quantiles=quantiles)


def _refit(task: tuple) -> tuple:
    y, seed = task
    with _WORKER["model"]:
        pm.set_data({"y": y})
    idata = fit(_WORKER["model"], _WORKER["reduced"], seed)
    post = {n: np.asarray(idata["posterior"][n]).ravel() for n in _WORKER["names"]}
    if _WORKER["quantiles"]:
        stats = {n: (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))) for n, v in post.items()}
    else:
        stats = {n: float(v.mean()) for n, v in post.items()}
    return stats, convergence(idata, _WORKER["names"])["converged"]


def refit_many(design: Design, ys: np.ndarray, seeds: np.ndarray, reduced: Settings = REDUCED, workers: int = 1, quantiles: bool = False) -> list[tuple]:
    """Refit the full model to each outcome vector with reduced settings; returns (posterior means, or 95% interval
    bounds if `quantiles`, and whether the refit converged) per refit. Every refit is returned, converged or not."""
    tasks = list(zip(ys, seeds, strict=True))
    if workers == 1:
        _init_worker(design, reduced, quantiles)
        return [_refit(t) for t in tasks]
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(design, reduced, quantiles)) as pool:
        return list(pool.map(_refit, tasks, chunksize=max(1, len(tasks) // (4 * workers))))


def _observed_means(design: Design, seed: int, reduced: Settings) -> dict:
    """Posterior means on the real outcomes, computed with the same reduced settings as the refits (section 5.4)."""
    _init_worker(design, reduced)
    return _refit((design.y, seed))[0]


def _decision(observed: float, p: float, predictor: str) -> str:
    if p >= 0.05:
        return "undetermined"
    return "supported" if np.sign(observed) == PREDICTED_SIGN[predictor] else "contradicted"


def direct_simulation_test(design: Design, predictor: str, n_sims: int, seed: int, full: Settings = FULL, reduced: Settings = REDUCED, workers: int = 1) -> dict:
    """Significance of one core predictor under the reduced model without it (section 5.4, steps 1-3)."""
    k = CORE.index(predictor)
    reduced_model = build_model(design, drop=predictor, keep_eta=True)
    idata_r = fit(reduced_model, full, seed, cores=min(full.chains, max(workers, 1)))
    reduced_checks = convergence(idata_r, coefficient_names(design, drop=predictor))
    eta = np.asarray(idata_r["posterior"]["eta"]).reshape(-1, design.y.size)
    rng = np.random.default_rng([seed, k])
    picks = rng.integers(0, eta.shape[0], n_sims)
    ys = rng.binomial(1, 1 / (1 + np.exp(-eta[picks]))).astype(int)
    seeds = np.random.SeedSequence([seed, k, 1]).generate_state(n_sims)
    observed = _observed_means(design, seed, reduced)[f"b_{predictor}"]
    refits = refit_many(design, ys, seeds, reduced, workers)
    null = np.array([m[f"b_{predictor}"] for m, _ in refits])
    p = p_value(observed, null)
    return {
        "predictor": predictor,
        "observed_reduced_settings": observed,
        "p_value": p,
        "decision": _decision(observed, p, predictor),
        "n_sims": n_sims,
        "share_refits_not_converged": float(np.mean([not ok for _, ok in refits])),
        "reduced_model_convergence": reduced_checks,
        "seed": seed,
    }


def overall_test(design: Design, n_shuffles: int, seed: int, reduced: Settings = REDUCED, workers: int = 1) -> dict:
    """Reported only: labels shuffled within cohort; statistic = largest |posterior mean| among the core coefficients."""
    core = [f"b_{p}" for p in CORE if p in design.predictors]
    rng = np.random.default_rng([seed, 99])
    groups = [np.flatnonzero(design.cohort == c) for c in np.unique(design.cohort)]
    ys = np.empty((n_shuffles, design.y.size), dtype=int)
    for i in range(n_shuffles):
        ys[i] = design.y
        for idx in groups:
            ys[i, idx] = rng.permutation(design.y[idx])
    seeds = np.random.SeedSequence([seed, 99, 1]).generate_state(n_shuffles)
    observed = max(abs(v) for n, v in _observed_means(design, seed, reduced).items() if n in core)
    refits = refit_many(design, ys, seeds, reduced, workers)
    null = np.array([max(abs(m[n]) for n in core) for m, _ in refits])
    return {"statistic": "max |posterior mean| of core coefficients", "observed": observed, "p_value": p_value(observed, null), "n_shuffles": n_shuffles}


def predictive_checks(design: Design, idata, seed: int) -> dict:
    """Prior predictive early-renewal share; posterior predictive count and decile calibration."""
    model = build_model(design, keep_eta=True)
    with model:
        prior = pm.sample_prior_predictive(draws=4000, random_seed=seed)
    prior_share = np.asarray(prior["prior_predictive"]["renew"]).reshape(-1, design.y.size).mean(1)
    eta = np.asarray(idata["posterior"]["eta"]).reshape(-1, design.y.size)
    prob = 1 / (1 + np.exp(-eta))
    rng = np.random.default_rng(seed)
    counts = rng.binomial(1, prob).sum(1)
    p_mean = prob.mean(0)
    deciles = pd.qcut(p_mean, 10, labels=False, duplicates="drop")
    table = pd.DataFrame({"decile": deciles, "predicted": p_mean, "observed": design.y}).groupby("decile").mean()
    return {
        "prior_share_quantiles": {q: float(np.quantile(prior_share, q)) for q in (0.025, 0.5, 0.975)},
        "observed_count": int(design.y.sum()),
        "replicated_count_eti95": [float(np.quantile(counts, 0.025)), float(np.quantile(counts, 0.975))],
        "deciles": table.reset_index().to_dict(orient="records"),
    }


def firth_fallback(frame: pd.DataFrame, n_sims: int, seed: int) -> dict:
    """Section 5.5 item 5: Firth logistic regression, core predictors + cohort, own spending as observed; each core
    coefficient tested by direct simulation from the reduced Firth fit."""
    design = make_design(frame, sigma_v=None)
    cols = list(CORE) + ["cohort_2020"]

    def matrix(drop=None):
        names = [c for c in cols if c != drop]
        own = (design.own_obs - design.own_center) / design.own_scale
        return names, np.column_stack([own if c == "own" else design.x[c] for c in names])

    names, design_matrix = matrix()
    model = FirthLogisticRegression().fit(design_matrix, design.y)
    ci = model.conf_int(method="pl")
    out = {"coefficients": {n: {"estimate": float(b), "pl95": [float(ci[i, 0]), float(ci[i, 1])]} for i, (n, b) in enumerate(zip(names, model.coef_, strict=True))}}
    rng = np.random.default_rng([seed, 7])
    for k, predictor in enumerate(CORE):
        _, reduced_matrix = matrix(drop=predictor)
        p_hat = FirthLogisticRegression().fit(reduced_matrix, design.y).predict_proba(reduced_matrix)[:, 1]
        null = np.array([FirthLogisticRegression().fit(design_matrix, rng.binomial(1, p_hat)).coef_[k] for _ in range(n_sims)])
        observed = float(model.coef_[k])
        p = p_value(observed, null)
        out["coefficients"][predictor].update(p_value=p, decision=_decision(observed, p, predictor))
    out["n_sims"] = n_sims
    return out
