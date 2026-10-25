"""Conventional (frequentist) estimates side by side (section 5.7). Reported only; they do not change any decision."""

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from ratchet import decision

GROUP_VARIABLES = {"H1": "sav_rate_2020", "H2a": "own", "H2b": "pull"}


def _compared(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[frame.grp.isin(["early", "stayer"])]


def welch(frame: pd.DataFrame, column: str) -> dict:
    """Welch two-sample t-test, early renewers minus stayers (unstratified)."""
    c = _compared(frame).dropna(subset=[column])
    early, stay = c.loc[c.grp == "early", column].astype(float), c.loc[c.grp == "stayer", column].astype(float)
    res = stats.ttest_ind(early, stay, equal_var=False)
    ci = res.confidence_interval(0.95)
    return {
        "difference": float(early.mean() - stay.mean()),
        "ci95": [float(ci.low), float(ci.high)],
        "p_value": float(res.pvalue),
        "n_early": int(early.size),
        "n_stayer": int(stay.size),
    }


def ols_hc2(frame: pd.DataFrame, column: str, adjusted: bool = False) -> dict:
    """OLS of the variable on an early-renewer and a cohort indicator (plus PY2021 track/level and log size if adjusted),
    HC2 robust standard errors."""
    c = _compared(frame)
    cols = [column] + (["log_n_ab_2020"] if adjusted else [])
    c = c.dropna(subset=cols)
    if adjusted:
        c = c[c.enhanced.astype(bool) | c.basic_level.notna()]
    x = pd.DataFrame({"early": (c.grp == "early").astype(float), "cohort_2020": (c.cohort == "2020-01").astype(float)})
    if adjusted:
        x["basic_c_e"] = (c.basic.astype(bool) & c.basic_level.isin(["C", "D", "E"])).astype(float)
        x["enhanced"] = c.enhanced.astype(bool).astype(float)
        x["log_n_ab_2020"] = c.log_n_ab_2020.astype(float)
    fit = sm.OLS(c[column].astype(float).to_numpy(), sm.add_constant(x.to_numpy()), hasconst=True).fit(cov_type="HC2")
    i = 1  # the early-renewer coefficient follows the constant
    lo, hi = fit.conf_int(0.05)[i]
    return {"difference": float(fit.params[i]), "ci95": [float(lo), float(hi)], "p_value": float(fit.pvalues[i]), "n": int(fit.nobs), "covariates": list(x.columns)}


def logit_ml(frame: pd.DataFrame, include_own: bool) -> dict:
    """Maximum-likelihood logistic regression with the 5.4 predictors and scaling, own spending as observed; odds ratios
    per 2 SD or per category with Wald 95% intervals. With about 27 events it may fail to converge or separate."""
    design = decision.make_design(frame, sigma_v=None, include_own=include_own)
    names = list(design.predictors)
    x = np.column_stack([(design.own_obs - design.own_center) / design.own_scale if n == "own" else design.x[n] for n in names])
    out = {"sample": {"n": int(design.y.size), "early": int(design.y.sum()), "excluded": design.excluded}}
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fit = sm.Logit(design.y, sm.add_constant(x)).fit(disp=0, maxiter=200)
        out["converged"] = bool(fit.mle_retvals.get("converged", False))
        out["warnings"] = sorted({type(w.message).__name__ for w in caught})
    except Exception as exc:  # perfect separation or a singular matrix: reported, not fatal
        return {**out, "converged": False, "error": f"{type(exc).__name__}: {exc}"}
    ci = fit.conf_int(0.05)
    out["coefficients"] = {
        n: {
            "log_odds": float(fit.params[i + 1]),
            "odds_ratio": float(np.exp(fit.params[i + 1])),
            "or_ci95": [float(np.exp(ci[i + 1][0])), float(np.exp(ci[i + 1][1]))],
            "p_value": float(fit.pvalues[i + 1]),
        }
        for i, n in enumerate(names)
    }
    return out


def _verdict(estimate: float, p: float, sign: int = 1) -> str:
    if p >= 0.05:
        return "undetermined"
    return "supported" if np.sign(estimate) == sign else "contradicted"


def agreement(confirm: dict, conventional: dict) -> list[dict]:
    """Confirmatory verdict (section 7) next to the conventional one: OLS-HC2 for H2b and H2a, ML logistic for H3."""
    rows = []
    for label, key in (("H2b", "H2b_pull"), ("H2a", "H2a_own")):
        g = confirm["groups"][key]
        c = conventional[label]["ols_hc2"]
        rows.append({"claim": label, "confirmatory": _verdict(g["observed"], g["p_value"]), "conventional": _verdict(c["difference"], c["p_value"])})
    tests = confirm["h3"].get("tests") or {k: v for k, v in confirm["h3"].get("fallback_firth", {}).get("coefficients", {}).items() if "decision" in v}
    logit = conventional["H3_logit"].get("coefficients", {})
    for predictor in decision.CORE:
        if predictor in tests and predictor in logit:
            rows.append(
                {
                    "claim": f"H3 {predictor}",
                    "confirmatory": tests[predictor]["decision"],
                    "conventional": _verdict(logit[predictor]["log_odds"], logit[predictor]["p_value"], decision.PREDICTED_SIGN[predictor]),
                }
            )
    for r in rows:
        r["agree"] = r["confirmatory"] == r["conventional"]
    return rows


def run_all(frame: pd.DataFrame, confirm: dict, did: dict, validation: dict) -> dict:
    out = {
        label: {"welch": welch(frame, col), "ols_hc2": ols_hc2(frame, col), "ols_hc2_adjusted": ols_hc2(frame, col, adjusted=True)}
        for label, col in GROUP_VARIABLES.items()
    }
    out["H3_logit"] = logit_ml(frame, include_own=validation["passed"])
    rows = agreement(confirm, out)
    h4, twfe = did["H4"], did["conventional"]["twfe"]["pooled"]
    rows.append({"claim": "H4", "confirmatory": _verdict(h4["observed"], h4["p_value"]), "conventional": _verdict(twfe["estimate"], twfe["p_value"])})
    rows[-1]["agree"] = rows[-1]["confirmatory"] == rows[-1]["conventional"]
    out["agreement"] = rows
    return out
