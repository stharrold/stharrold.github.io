"""Validation of the benchmark approximation (section 4.4) and its use downstream."""

import numpy as np
import pandas as pd
from scipy import stats

SPEARMAN_MIN, MAPE_MAX, SLOPE_RANGE = 0.80, 5.0, (0.9, 1.1)
STEP1_MIN_N = 30  # below this, the model uses the whole-benchmark error SD (section 4.4)


def _metrics(approximate: np.ndarray, actual: np.ndarray) -> dict:
    slope, intercept = np.polyfit(approximate, actual, 1)
    return {
        "n": int(approximate.size),
        "spearman": float(stats.spearmanr(approximate, actual).statistic),
        "median_abs_pct_error": float(np.median(np.abs(100 * (approximate - actual) / actual))),
        "slope": float(slope),
        "intercept": float(intercept),
    }


def validate(frame: pd.DataFrame) -> dict:
    """`frame` is the `validation` table: approximate, actual, step, and for the step-1 check rebased_approximate and
    rebased_cms. Rows missing a needed value are dropped from that check and counted."""
    ok = frame.dropna(subset=["approximate", "actual"])
    overall = _metrics(ok.approximate.to_numpy(), ok.actual.to_numpy())
    by_step = {int(s): _metrics(g.approximate.to_numpy(), g.actual.to_numpy()) for s, g in ok.groupby("step") if len(g) >= 3}
    passed = overall["spearman"] >= SPEARMAN_MIN and overall["median_abs_pct_error"] <= MAPE_MAX
    calibrate = passed and not (SLOPE_RANGE[0] <= overall["slope"] <= SLOPE_RANGE[1])
    a, b = (overall["intercept"], overall["slope"]) if calibrate else (0.0, 1.0)
    approx_cal = a + b * ok.approximate.to_numpy()
    sigma_v = float(np.std(100 * (approx_cal - ok.actual.to_numpy()) / ok.actual.to_numpy(), ddof=1))
    # Step-1 check: own-spending part against CMS's benchmark-year spending, after the same calibration.
    # Error in percentage points of the current benchmark, the scale of the own-spending component.
    s1 = frame.dropna(subset=["rebased_approximate", "rebased_cms", "current_bnchmk"]) if "rebased_cms" in frame else frame.iloc[:0]
    step1 = None
    if len(s1) >= 3:
        reb_cal = a + b * s1.rebased_approximate.to_numpy()
        step1 = _metrics(s1.rebased_approximate.to_numpy(), s1.rebased_cms.to_numpy())
        step1["sigma_own"] = float(np.std(100 * (reb_cal - s1.rebased_cms.to_numpy()) / s1.current_bnchmk.to_numpy(), ddof=1))
    use_step1 = step1 is not None and step1["n"] >= STEP1_MIN_N
    return {
        "excluded": int(len(frame) - len(ok)),
        "overall": overall,
        "by_step": by_step,
        "passed": bool(passed),
        "calibrated": bool(calibrate),
        "calibration": {"intercept": a, "slope": b},
        "sigma_v": sigma_v,
        "step1": step1,
        "step1_excluded": int(len(frame) - len(s1)),
        "sigma_v_model": step1["sigma_own"] if use_step1 else sigma_v,
        "sigma_v_model_source": "step-1 check" if use_step1 else "whole-benchmark check",
    }


def apply_calibration(frame: pd.DataFrame, result: dict) -> pd.DataFrame:
    """Recompute gain and components after calibration: the intercept goes to the own-spending part, and both parts
    are scaled by the slope, so own + regional component = gain still holds. Regional pull is unchanged."""
    a, b = result["calibration"]["intercept"], result["calibration"]["slope"]
    out = frame.copy()
    rebased, adjustment, current = out.rebased_w, out.adjustment_w, out.current_bnchmk
    out["own"] = 100 * (a + b * rebased - current) / current
    out["regional_comp"] = 100 * b * adjustment / current
    out["gain"] = out.own + out.regional_comp
    return out
