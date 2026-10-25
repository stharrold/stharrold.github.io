import numpy as np
import pandas as pd

from ratchet import resample, validate


def _data(rng, shift=0.0, n=(11, 159, 18, 118)):
    cohort = np.repeat(["2019-07", "2019-07", "2020-01", "2020-01"], n)
    early = np.repeat([True, False, True, False], n)
    y = rng.normal(0, 1, cohort.size) + shift * early + 0.5 * (cohort == "2020-01")
    return y, early, cohort


def test_difference_weights_cohorts_by_early_renewers():
    y = np.array([3.0, 1.0, 1.0, 10.0, 4.0, 4.0])
    early = np.array([True, False, False, True, False, False])
    cohort = np.array(["a", "a", "a", "b", "b", "b"])
    # Each cohort has one early renewer: weights 1/2, 1/2; differences 2 and 6.
    assert resample.difference(y, early, cohort) == 4.0


def test_bootstrap_posterior_mean_equals_observed_difference():
    rng = np.random.default_rng(0)
    y, early, cohort = _data(rng, shift=0.3)
    draws = resample.bayesian_bootstrap(y, early, cohort, 20_000, rng)
    se = draws.std() / np.sqrt(draws.size)
    assert abs(draws.mean() - resample.difference(y, early, cohort)) < 4 * se


def test_p_value_counts_ties_and_adds_one():
    assert resample.p_value(1.0, np.array([0.5, -1.0, 2.0, 0.1])) == 3 / 5


def test_permutation_p_roughly_uniform_under_null():
    rng = np.random.default_rng(1)
    ps = []
    for _ in range(200):
        y, early, cohort = _data(rng)
        ps.append(resample.p_value(resample.difference(y, early, cohort), resample.permutation_null(y, early, cohort, 199, rng)))
    assert 0.01 <= np.mean(np.array(ps) < 0.05) <= 0.10
    assert 0.40 <= np.mean(ps) <= 0.60


def test_compare_detects_planted_difference_and_counts_missing():
    rng = np.random.default_rng(2)
    y, early, cohort = _data(rng, shift=1.0)
    y[0] = np.nan
    out = resample.compare(y, early, cohort, n_resamples=2_000, seed=3)
    assert out["p_value"] < 0.01 and out["eti95"][0] > 0
    assert out["excluded"] == {"early": 1, "stayer": 0}


def test_median_variant_runs():
    rng = np.random.default_rng(4)
    y, early, cohort = _data(rng, shift=1.0)
    out = resample.compare(y, early, cohort, n_resamples=500, seed=5, median=True)
    assert out["eti95"][0] < out["observed"] < out["eti95"][1]


def _validation_frame(rng, factor=1.0, noise=0.0, n=111):
    approx = rng.normal(11_000, 1_200, n)
    actual = factor * approx * np.exp(rng.normal(0, noise, n)) if noise else factor * approx
    return pd.DataFrame({"approximate": approx, "actual": actual, "step": rng.choice([1, 2], n)})


def test_exact_approximation_passes_without_calibration():
    out = validate.validate(_validation_frame(np.random.default_rng(0)))
    assert out["passed"] and not out["calibrated"]
    assert out["overall"]["spearman"] == 1.0 and abs(out["overall"]["slope"] - 1) < 1e-9 and out["sigma_v"] < 1e-9


def test_out_of_range_slope_is_calibrated():
    frame = _validation_frame(np.random.default_rng(1), factor=1.2)
    frame["actual"] = frame.actual - 0.2 * frame.approximate.mean()  # keep percentage errors small
    out = validate.validate(frame)
    assert out["passed"] and out["calibrated"] and out["sigma_v"] < 1e-6


def test_noisy_approximation_fails():
    out = validate.validate(_validation_frame(np.random.default_rng(2), noise=0.2))
    assert not out["passed"]


def test_calibration_keeps_components_adding_up():
    frame = pd.DataFrame({"rebased_w": [10_000.0, 12_000.0], "adjustment_w": [300.0, -200.0], "current_bnchmk": [10_500.0, 11_500.0], "pull": [1.0, 2.0]})
    out = validate.apply_calibration(frame, {"calibration": {"intercept": 150.0, "slope": 0.95}})
    np.testing.assert_allclose(out.gain, 100 * (150 + 0.95 * (frame.rebased_w + frame.adjustment_w) - frame.current_bnchmk) / frame.current_bnchmk)
    assert (out.pull == frame.pull).all()
