"""Robustness analyses (section 5.5). Reported as estimates; they do not change the section 7 decisions.

Group comparisons use the Bayesian bootstrap and stratified permutation test of 5.1; H3 variants report posterior
summaries of the 5.4 model without the direct-simulation test (run only for 5.4 itself and the Firth model, item 5).
"""

import pandas as pd

from ratchet import decision, regression, resample

GROUP_VARIABLES = {"H1": "sav_rate_2020", "H2a": "own", "H2b": "pull"}


def _compared(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[frame.grp.isin(["early", "stayer"])]


def compare(frame: pd.DataFrame, column: str, n: int, seed: int, median: bool = False) -> dict:
    c = _compared(frame)
    return resample.compare(c[column].to_numpy(), (c.grp == "early").to_numpy(), c.cohort.to_numpy(), n, seed, median=median)


def h3_posterior(frame: pd.DataFrame, sigma_v: float | None, include_own: bool, settings: dict, seed: int, **design_kwargs) -> dict:
    """Posterior summary of the 5.4 model on a variant frame or design (full settings, same checks and rerun)."""
    design = decision.make_design(frame, sigma_v if include_own else None, include_own=include_own, **design_kwargs)
    idata, checks = decision.fit_checked(design, seed, full=settings["full"], retry=settings["retry"], cores=min(4, settings["workers"]))
    names = decision.coefficient_names(design)
    return {
        "sample": {"n": int(design.y.size), "early": int(design.y.sum()), "excluded": design.excluded},
        "convergence": checks,
        "posterior": decision.coefficient_summary(idata, names),
    }


def run_all(frame: pd.DataFrame, frame_by23: pd.DataFrame, validation: dict, settings: dict, seed: int) -> dict:
    n = settings["n_resamples"]
    passed = validation["passed"]
    sigma_v = validation["sigma_v_model"] if passed else None
    out: dict = {}

    # 1. Covariate-adjusted regressions (5.3 plus PY2021 track/level and log N_AB).
    out["1_adjusted_regressions"] = {
        label: {
            "unadjusted_5_3": regression.adjusted_difference(
                frame, col, seed, adjusted=False, full=settings["full"], retry=settings["retry"], cores=min(4, settings["workers"])
            ),
            "adjusted": regression.adjusted_difference(
                frame, col, seed + 1, adjusted=True, full=settings["full"], retry=settings["retry"], cores=min(4, settings["workers"])
            ),
        }
        for label, col in GROUP_VARIABLES.items()
    }
    # 2. Differences in medians.
    out["2_medians"] = {label: compare(frame, col, n, seed, median=True) for label, col in GROUP_VARIABLES.items()}
    # 3. 2020-01-01 cohort only.
    cohort20 = frame[frame.cohort == "2020-01"]
    out["3_cohort_2020"] = {label: compare(cohort20, col, n, seed) for label, col in GROUP_VARIABLES.items()}
    out["3_cohort_2020"]["H3"] = h3_posterior(cohort20, sigma_v, passed, settings, seed, exclude=("cohort_2020",))
    # 4. H1 for the PY2021 savings rate.
    out["4_h1_py2021"] = compare(frame, "sav_rate_2021", n, seed)
    # 5. Firth logistic regression with direct-simulation tests.
    out["5_firth"] = decision.firth_fallback(frame, n, seed)
    # 6. Benchmark years 2020-2021 only (main validation's calibration and sigma_v).
    out["6_by2_by3"] = {"H2a": compare(frame_by23, "own", n, seed), "H3": h3_posterior(frame_by23, sigma_v, passed, settings, seed)}
    # 7. H3 without the measurement-error layer.
    out["7_no_measurement_error"] = h3_posterior(frame, None, passed, settings, seed)
    # 8. Complete cases (no ACOs imputed under section 3).
    complete = frame[~frame.imputed.fillna(False).astype(bool)]
    out["8_complete_cases"] = {label: compare(complete, col, n, seed) for label, col in (("H2a", "own"), ("gain", "gain"), ("regional_comp", "regional_comp"))}
    out["8_complete_cases"]["H3"] = h3_posterior(complete, sigma_v, passed, settings, seed)
    # 9. Regional pull without risk standardization or case-mix adjustment.
    unadjusted = frame.assign(pull=frame.pull_unadjusted)
    out["9_unadjusted_pull"] = {"H2b": compare(unadjusted, "pull", n, seed), "H3": h3_posterior(unadjusted, sigma_v, passed, settings, seed)}
    return out
