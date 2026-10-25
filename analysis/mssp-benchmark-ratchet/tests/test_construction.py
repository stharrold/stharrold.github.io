"""Section 4.3 in SQL against an independent numpy implementation, on synthetic data."""

import numpy as np
import pytest

from ratchet import build, synthetic


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    data_dir = tmp_path_factory.mktemp("synthetic")
    truth = synthetic.generate(data_dir, seed=1)
    con = build.connect(data_dir, stage="full")
    merged = con.sql("select * from expected_gain").df().merge(truth.acos, on="aco_id", suffixes=("_sql", "_np"))
    return con, truth, merged


@pytest.mark.parametrize("column", ["new_bnchmk", "gain", "own", "regional_comp", "pull", "w", "step"])
def test_sql_matches_numpy(built, column):
    _, _, m = built
    sql, ref = m[f"{column}_sql"].astype(float), m[f"{column}_np"].astype(float)
    assert (sql.isna() == ref.isna()).all()
    # Written CSV values are rounded, so allow small absolute differences (percentage points or dollars).
    np.testing.assert_allclose(sql[ref.notna()], ref[ref.notna()], rtol=1e-6, atol=1e-3)


def test_components_add_to_gain(built):
    _, _, m = built
    ok = m.gain_sql.notna()
    np.testing.assert_allclose((m.own_sql + m.regional_comp_sql)[ok], m.gain_sql[ok], atol=1e-9)


def test_regional_component_identity_before_caps(built):
    """Regional component = w x pull - w x own when no cap binds (section 1.3)."""
    _, _, m = built
    free = m.gain_sql.notna() & ~m.any_cap
    assert free.sum() > 50
    np.testing.assert_allclose(m.regional_comp_sql[free], (m.w_sql * (m.pull_sql - m.own_sql))[free], atol=1e-6)


def test_missing_rules(built):
    _, truth, m = built
    row = m.set_index("aco_id")
    assert np.isnan(row.loc[truth.excluded_suppressed, "gain_sql"])  # positive share, suppressed spending
    assert not np.isnan(row.loc[truth.excluded_suppressed, "pull_sql"])  # pull does not use own spending
    assert not np.isnan(row.loc[truth.zero_share, "gain_sql"])  # zero share: suppressed spending is irrelevant


def test_early_renewers_never_loaded_from_py2022(built):
    con, truth, _ = built
    ids = ", ".join(f"'{i}'" for i in truth.early_ids)
    assert build.scalar(con, f"select count(*) from raw_results_2022 where trim(aco_id) in ({ids})") == 0
    assert build.scalar(con, "select count(*) from res where py = 2022 and hist_bnchmk < 0") == 0


def test_groups_and_validation_sample(built):
    con, truth, _ = built
    counts = dict(con.sql("select grp, count(*) from groups group by grp").fetchall())
    assert counts == truth.acos.grp.value_counts().to_dict()
    assert build.scalar(con, "select count(*) from validation_sample") == (truth.acos.kind == "valid").sum()
    assert build.scalar(con, "select count(*) from validation_sample where aco_id like 'R%'") == 0


def test_analysis_frame(built):
    con, truth, _ = built
    frame = con.sql("select * from analysis").df()
    assert len(frame) == truth.acos.grp.notna().sum()
    assert frame.sav_rate_2021.notna().all()  # PY2021 spells Sav_Rate
    assert build.scalar(con, "select count(*) from res where py between 2016 and 2018 and aco_id is null") == 0  # ACO_Num years
