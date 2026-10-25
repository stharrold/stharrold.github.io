"""H4: effect of early renewal on per-capita spending, difference-in-differences (sections 4.5, 5.7, 5.8).

The confirmatory estimate collapses the panel to one change per ACO (post-period mean minus pre-period mean of log
spending) and compares early renewers with not-yet-renewed ACOs with the 5.1 estimator: Bayesian bootstrap posterior,
stratified permutation significance. The pre-trend check applies the same test to the PY2020-PY2021 change.
"""

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from ratchet import resample

PRE, POST = (2020, 2021), (2022, 2023, 2024)


def deltas(panel: pd.DataFrame, outcome: str = "y", balanced: bool = False) -> pd.DataFrame:
    """One row per ACO: Delta (post mean - pre mean over included years) and Delta_pre (PY2021 - PY2020)."""
    inc = panel[(panel.status == "included") & panel[outcome].notna()]
    wide = inc.pivot_table(index=["aco_id", "grp", "cohort"], columns="py", values=outcome).reset_index()
    for year in PRE + POST:
        if year not in wide:
            wide[year] = np.nan
    wide = wide[wide[2020].notna() & wide[2021].notna()]
    post = wide[list(POST)]
    if balanced:
        wide, post = wide[post.notna().all(axis=1)], post[post.notna().all(axis=1)]
    wide = wide.assign(delta=post.mean(axis=1) - wide[list(PRE)].mean(axis=1), delta_pre=wide[2021] - wide[2020], y_2021=wide[2021], n_post=post.notna().sum(axis=1))
    return wide[wide.n_post > 0].reset_index(drop=True)


def estimate(d: pd.DataFrame, column: str, n: int, seed: int) -> dict:
    out = resample.compare(d[column].to_numpy(), (d.grp == "early").to_numpy(), d.cohort.to_numpy(), n, seed)
    out["percent"] = {"posterior_mean": float(100 * np.expm1(out["posterior_mean"])), "eti95": [float(100 * np.expm1(v)) for v in out["eti95"]]}
    return out


def attrition(panel: pd.DataFrame) -> list[dict]:
    return panel.groupby(["grp", "py", "status"]).size().rename("n").reset_index().to_dict(orient="records")


def _ps_covariates(d: pd.DataFrame, frame: pd.DataFrame) -> pd.DataFrame:
    x = d.merge(frame[["aco_id", "log_n_ab_2020", "basic", "basic_level", "enhanced"]], on="aco_id", how="left")
    x = x.assign(
        cohort_2020=(x.cohort == "2020-01").astype(float),
        basic_c_e=(x.basic.astype(bool) & x.basic_level.isin(["C", "D", "E"])).astype(float),
        enhanced_f=x.enhanced.astype(bool).astype(float),
    )
    return x.dropna(subset=["log_n_ab_2020", "y_2021", "delta_pre"])


def _ps_estimate(x: pd.DataFrame, treated: np.ndarray) -> tuple[float, float]:
    cov = sm.add_constant(x[["cohort_2020", "y_2021", "delta_pre", "log_n_ab_2020", "basic_c_e", "enhanced_f"]].to_numpy(float))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p = sm.Logit(treated.astype(float), cov).fit(disp=0, maxiter=200).predict(cov)
    w = p / (1 - p)
    control = ~treated
    est = x.delta.to_numpy()[treated].mean() - np.average(x.delta.to_numpy()[control], weights=w[control])
    return float(est), float(w[control].max())


def ps_weighted(d: pd.DataFrame, frame: pd.DataFrame, n: int, seed: int) -> dict:
    """Propensity-score-weighted DiD (5.8 robustness 3): ATT weights p/(1-p) for comparison ACOs; stratified
    permutation p with the propensity model refit on each shuffle."""
    x = _ps_covariates(d, frame)
    treated = (x.grp == "early").to_numpy()
    observed, max_w = _ps_estimate(x, treated)
    rng = np.random.default_rng([seed, 41])
    groups = [np.flatnonzero(x.cohort.to_numpy() == c) for c in np.unique(x.cohort)]
    null, failed = np.empty(n), 0
    for i in range(n):
        lab = treated.copy()
        for idx in groups:
            lab[idx] = rng.permutation(treated[idx])
        try:
            null[i] = _ps_estimate(x, lab)[0]
        except Exception:  # a shuffle whose propensity model fails is counted as not extreme, and reported
            null[i], failed = 0.0, failed + 1
    return {
        "estimate": observed,
        "percent": float(100 * np.expm1(observed)),
        "p_value": resample.p_value(observed, null),
        "max_weight": max_w,
        "n": int(len(x)),
        "n_resamples": n,
        "failed_refits": failed,
    }


def twfe(panel: pd.DataFrame, outcome: str = "y") -> dict:
    """Conventional comparison (5.7): two-way fixed effects with ACO and cohort-by-year effects, ACO-clustered SEs; the
    pooled early x post coefficient and an event study (PY2021 reference)."""
    inc = panel[(panel.status == "included") & panel[outcome].notna()].copy()
    inc["early"] = (inc.grp == "early").astype(float)
    inc["treat_post"] = inc.early * inc.post.astype(float)
    # Cohort-by-year effects with PY2020 as each cohort's reference: with ACO effects, a full set would be collinear.
    year_terms = []
    for c in sorted(inc.cohort.unique()):
        for year in (2021, 2022, 2023, 2024):
            name = f"cy_{c.replace('-', '_')}_{year}"
            inc[name] = ((inc.cohort == c) & (inc.py == year)).astype(float)
            year_terms.append(name)
    fixed = " + ".join(["C(aco_id)"] + year_terms)
    out = {"n_obs": int(len(inc)), "n_acos": int(inc.aco_id.nunique())}
    groups = pd.factorize(inc.aco_id)[0]
    pooled = smf.ols(f"{outcome} ~ treat_post + {fixed}", data=inc).fit(cov_type="cluster", cov_kwds={"groups": groups})
    lo, hi = pooled.conf_int().loc["treat_post"]
    out["pooled"] = {"estimate": float(pooled.params["treat_post"]), "ci95": [float(lo), float(hi)], "p_value": float(pooled.pvalues["treat_post"])}
    terms = []
    for year in (2020, 2022, 2023, 2024):
        inc[f"e_{year}"] = inc.early * (inc.py == year).astype(float)
        terms.append(f"e_{year}")
    event = smf.ols(f"{outcome} ~ {' + '.join(terms)} + {fixed}", data=inc).fit(cov_type="cluster", cov_kwds={"groups": groups})
    ci = event.conf_int()
    out["event_study"] = {
        t[2:]: {"estimate": float(event.params[t]), "ci95": [float(ci.loc[t, 0]), float(ci.loc[t, 1])], "p_value": float(event.pvalues[t])} for t in terms
    }
    return out


def run_all(panel: pd.DataFrame, frame: pd.DataFrame, n: int, seed: int) -> dict:
    d = deltas(panel)
    out = {
        "sample": {"early": int((d.grp == "early").sum()), "comparison": int((d.grp == "stayer").sum())},
        "attrition": attrition(panel),
        "H4": estimate(d, "delta", n, seed),
        "pre_trend_check": estimate(d, "delta_pre", n, seed),
    }
    out["H4"]["interpretable_as_effect"] = out["pre_trend_check"]["p_value"] >= 0.05
    out["robustness"] = {
        "1_risk_adjusted": estimate(deltas(panel, "y_risk"), "delta", n, seed),
        "2_balanced": estimate(deltas(panel, balanced=True), "delta", n, seed),
        "3_propensity_weighted": ps_weighted(d, frame, n, seed),
        "4_cohort_2020": estimate(d[d.cohort == "2020-01"], "delta", n, seed),
    }
    out["conventional"] = {"twfe": twfe(panel), "twfe_risk_adjusted": twfe(panel, "y_risk")}
    return out


def mde_inputs(did_pre: pd.DataFrame) -> dict:
    """Section 6: SD of Delta_pre among compared ACOs with both pre-period years (pre-period data only)."""
    d = did_pre.dropna(subset=["y_2020", "y_2021"])
    change = d.y_2021 - d.y_2020
    return {"sd_delta_pre": float(change.std()), "n_early": int((d.grp == "early").sum()), "n_comparison": int((d.grp == "stayer").sum())}
