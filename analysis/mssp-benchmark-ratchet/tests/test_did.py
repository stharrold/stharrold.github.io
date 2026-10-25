"""H4 (difference-in-differences) and the conventional comparisons on synthetic data with a planted effect."""

import numpy as np
import pytest

from ratchet import build, conventional, did, synthetic


def _build(tmp_path, effect):
    truth = synthetic.generate(tmp_path, seed=3, did_effect=effect)
    con = build.connect(tmp_path, stage="full", descriptive=True)
    return truth, con, con.sql("select * from did_panel").df(), con.sql("select * from analysis").df()


@pytest.fixture(scope="module")
def planted(tmp_path_factory):
    return _build(tmp_path_factory.mktemp("planted"), -0.04)


def test_status_follows_later_renewals_and_exits(planted):
    truth, _, panel, _ = planted
    st = panel.set_index(["aco_id", "py"]).status
    a = truth.acos.set_index("aco_id")
    for aco in a.index[(a.grp == "stayer") & (a.later == "renew2023")]:
        assert st[(aco, 2022)] == "included" and st[(aco, 2023)] == "later renewal" and st[(aco, 2024)] == "later renewal"
    for aco in a.index[(a.grp == "stayer") & (a.later == "leave2024")]:
        assert st[(aco, 2023)] == "included" and st[(aco, 2024)] == "absent"
    for aco in a.index[(a.grp == "early") & (a.later == "renew2024")]:
        assert st[(aco, 2023)] == "included" and st[(aco, 2024)] == "later renewal"


def test_deltas_use_included_years_only(planted):
    _, _, panel, _ = planted
    d = did.deltas(panel)
    inc = panel[panel.status == "included"].pivot_table(index="aco_id", columns="py", values="y")
    row = d.iloc[0]
    expected = inc.loc[row.aco_id, [2022, 2023, 2024]].mean() - inc.loc[row.aco_id, [2020, 2021]].mean()
    assert row.delta == pytest.approx(expected)
    assert did.deltas(panel, balanced=True).n_post.eq(3).all()


def test_planted_effect_recovered_and_twfe_agrees(planted):
    _, _, panel, frame = planted
    d = did.deltas(panel)
    h4 = did.estimate(d, "delta", 500, 1)
    assert abs(h4["observed"] - (-0.04)) < 0.015 and h4["p_value"] < 0.01
    twfe = did.twfe(panel)["pooled"]
    assert abs(twfe["estimate"] - h4["observed"]) < 0.01 and twfe["ci95"][1] < 0
    ps = did.ps_weighted(d, frame, 200, 2)
    assert ps["estimate"] < 0 and ps["failed_refits"] == 0


def test_no_effect_gives_no_signal(tmp_path):
    _, _, panel, _ = _build(tmp_path, 0.0)
    h4 = did.estimate(did.deltas(panel), "delta", 500, 1)
    assert abs(h4["observed"]) < 0.015


def test_conventional_group_and_logit(planted):
    _, _, _, frame = planted
    w = conventional.welch(frame, "pull")
    o = conventional.ols_hc2(frame, "pull")
    assert w["ci95"][0] > 0 and o["ci95"][0] > 0  # the generator plants higher pull for early renewers
    assert conventional.ols_hc2(frame, "pull", adjusted=True)["covariates"][-1] == "log_n_ab_2020"
    logit = conventional.logit_ml(frame, include_own=True)
    assert "pull" in logit["coefficients"] and logit["coefficients"]["pull"]["odds_ratio"] > 1
    assert np.isfinite(logit["coefficients"]["own"]["p_value"])


def test_pre_trend_equivalence_and_trend_adjustment(planted):
    _, _, panel, frame = planted
    d = did.deltas(panel)
    full = d[d.n_post == 3]
    assert np.allclose(full.c, 2.5)
    np.testing.assert_allclose(d.delta_trend_adjusted, d.delta - d.c * d.delta_pre)
    out = did.run_all(panel, frame, 200, 1)
    eq = out["pre_trend_check"]["equivalence"]
    assert eq["holds"] == (eq["scaled_bound"] < eq["abs_h4"]) and out["H4"]["interpretable_as_effect"] == eq["holds"]
    assert "5_trend_adjusted" in out["robustness"]
