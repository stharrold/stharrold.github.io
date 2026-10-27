"""H3 plumbing on a made-up analysis frame with a planted effect, using tiny sampler settings (not the registered ones)."""

import numpy as np
import pandas as pd
import pytest

from ratchet import decision

TINY = decision.Settings(chains=2, tune=300, draws=300, target_accept=0.9)


@pytest.fixture(scope="module")
def frame():
    rng = np.random.default_rng(0)
    n = 300
    pull = rng.normal(0, 4, n)
    own = rng.normal(0, 3, n)
    logit = -2.4 + 0.5 * pull + 0.2 * own
    early = rng.random(n) < 1 / (1 + np.exp(-logit))
    return pd.DataFrame(
        {
            "grp": np.where(early, "early", np.where(rng.random(n) < 0.05, "leaver", "stayer")),
            "cohort": rng.choice(["2019-07", "2020-01"], n),
            "basic": rng.random(n) < 0.85,
            "basic_high": rng.random(n) < 0.4,
            "pull": pull,
            "own": np.where(np.arange(n) == 5, np.nan, own),
            "log_n_ab_2020": rng.normal(9.5, 0.6, n),
            "high_revenue": rng.random(n) < 0.35,
            "prospective": rng.random(n) < 0.4,
            "later_agreement": rng.random(n) < 0.7,
        }
    )


def test_design_scaling_and_sample(frame):
    d = decision.make_design(frame, sigma_v=2.0)
    expected = frame[frame.basic & frame.grp.isin(["early", "stayer"]) & frame.own.notna()]
    assert d.y.size == len(expected) and d.y.sum() == (expected.grp == "early").sum()
    np.testing.assert_allclose([d.x["pull"].mean(), d.x["pull"].std()], [0, 0.5], atol=1e-12)
    np.testing.assert_allclose(d.x["high_revenue"].mean(), 0, atol=1e-12)
    assert "own" not in d.x and d.sigma_v == 2.0
    assert sum(d.excluded.values()) == (frame.basic & frame.grp.isin(["early", "stayer"]) & frame.own.isna()).sum()


def test_fit_recovers_planted_direction(frame):
    d = decision.make_design(frame, sigma_v=2.0)
    idata, checks = decision.fit_checked(d, seed=1, full=TINY, retry=TINY, cores=1)
    summary = decision.coefficient_summary(idata, decision.coefficient_names(d))
    assert summary["b_pull"]["eti95"][0] > 0
    assert set(checks) >= {"converged", "max_rhat", "divergent", "attempts"}
    checks_pp = decision.predictive_checks(d, idata, seed=2)
    assert checks_pp["replicated_count_eti95"][0] <= checks_pp["observed_count"] <= checks_pp["replicated_count_eti95"][1]


def test_models_without_measurement_error_and_with_t_prior_build(frame):
    d = decision.make_design(frame, sigma_v=None)
    assert d.sigma_v is None
    names = {v.name for v in decision.build_model(d, prior="t").free_RVs}
    assert "own_z" not in names and "b_own" in names
    assert "b_own" not in {v.name for v in decision.build_model(decision.make_design(frame, 2.0), drop="own").free_RVs}


def test_direct_simulation_and_overall_tests_run(frame):
    d = decision.make_design(frame, sigma_v=2.0)
    out = decision.direct_simulation_test(d, "basic_high", n_sims=3, seed=3, full=TINY, reduced=TINY)
    assert 0 < out["p_value"] <= 1 and out["decision"] in ("supported", "contradicted", "undetermined")
    overall = decision.overall_test(d, n_shuffles=3, seed=4, reduced=TINY)
    assert overall["observed"] > 0 and 0 < overall["p_value"] <= 1


def test_parallel_refits_match_sequential(frame):
    d = decision.make_design(frame, sigma_v=None)
    ys = np.tile(d.y, (2, 1))
    seeds = np.array([11, 12])
    seq = decision.refit_many(d, ys, seeds, TINY, workers=1)
    par = decision.refit_many(d, ys, seeds, TINY, workers=2)
    for (a, _), (b, _) in zip(seq, par, strict=True):
        assert a["b_pull"] == pytest.approx(b["b_pull"], rel=1e-12)


def test_firth_fallback(frame):
    out = decision.firth_fallback(frame, n_sims=30, seed=5)
    assert out["coefficients"]["pull"]["estimate"] > 0 and "p_value" in out["coefficients"]["own"]
