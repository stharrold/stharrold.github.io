"""Sections 5.3, 5.5 and 5.6 helpers on made-up frames, with tiny sampler settings (not the registered ones)."""

import json

import numpy as np
import pandas as pd
import pytest

from ratchet import decision, exploratory, regression, run

TINY = decision.Settings(chains=2, tune=300, draws=300, target_accept=0.9)


@pytest.fixture(scope="module")
def frame():
    rng = np.random.default_rng(0)
    n = 300
    grp = rng.choice(["early", "stayer", "leaver"], n, p=[0.15, 0.77, 0.08])
    basic = rng.random(n) < 0.85
    return pd.DataFrame(
        {
            "aco_id": [f"A{i}" for i in range(n)],
            "grp": grp,
            "cohort": rng.choice(["2019-07", "2020-01"], n),
            "basic": basic,
            "basic_level": np.where(basic, rng.choice(list("ABCDE"), n), None),
            "enhanced": ~basic,
            "enhanced_2022": np.where(grp == "leaver", None, rng.random(n) < 0.3),
            "log_n_ab_2020": rng.normal(9.5, 0.6, n),
            "pull": rng.normal(0, 4, n) + 3.0 * (grp == "early"),
            "own": rng.normal(0, 3, n),
            "regional_comp": rng.normal(0, 1, n),
            "sav_rate_2020": rng.normal(2, 4, n),
            "census_region": rng.choice(["Midwest", "South", "West", None], n, p=[0.3, 0.4, 0.25, 0.05]),
        }
    )


def test_regression_recovers_planted_shift(frame):
    out = regression.adjusted_difference(frame, "pull", seed=1, adjusted=True, full=TINY, retry=TINY, cores=1)
    lo, hi = out["b_early_units"]["eti95"]
    assert lo < 3.0 < hi and lo > 0
    assert out["covariates"] == ["early", "cohort_2020", "basic_c_e", "enhanced", "log_n_ab_2020"]
    assert out["n"] == frame.grp.isin(["early", "stayer"]).sum()


def test_region_indicators_use_a_reference(frame):
    with_region, names = exploratory.region_indicators(frame)
    # No Northeast ACOs here, so the first region present (Midwest) is the reference.
    assert names == ("region_south", "region_west") and with_region.census_region.notna().all()


def test_enhanced_early_renewers_and_who_renewed(frame):
    rows = exploratory.enhanced_early_renewers(frame)
    assert len(rows) == ((frame.grp == "early") & frame.enhanced).sum()
    assert all(0 <= r["pull"]["stayer_percentile"] <= 100 for r in rows)
    counts = exploratory.who_renewed(frame)
    assert sum(r["n"] for r in counts) == len(frame)


def test_exploratory_refuses_before_confirm_without_loading_data(tmp_path):
    for name in ("validation.json", "power.json"):
        (tmp_path / name).write_text(json.dumps({}))
    # The data directory does not exist: the prerequisite check must fail first, before any file is read.
    with pytest.raises(SystemExit, match="confirm.json is missing"):
        run.main(["exploratory", "--data-dir", str(tmp_path / "no-data"), "--out-dir", str(tmp_path)])
