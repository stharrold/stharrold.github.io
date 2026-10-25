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


@pytest.mark.parametrize("column", ["new_bnchmk", "gain", "own", "regional_comp", "pull", "pull_unadjusted", "w", "step"])
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


def test_suppression_rules(built):
    """Section 3: hidden values are filled by the fallback rules and flagged; unknown shares exclude the ACO."""
    _, truth, m = built
    row = m.set_index("aco_id")
    for aco in truth.imputed_ids:
        assert not np.isnan(row.loc[aco, "gain_sql"]) and row.loc[aco, "imputed_sql"]
    assert np.isnan(row.loc[truth.unrecoverable, "gain_sql"]) and np.isnan(row.loc[truth.unrecoverable, "pull_sql"])
    assert not np.isnan(row.loc[truth.zero_share, "gain_sql"]) and not row.loc[truth.zero_share, "imputed_sql"]
    assert (m.imputed_sql.fillna(False) == m.imputed_np).all()


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


def test_step1_check_matches_when_cms_values_equal_ours(built):
    con, _, _ = built
    v = con.sql("select * from validation").df()
    np.testing.assert_allclose(v.rebased_cms, v.rebased_approximate, rtol=1e-6)
    assert build.scalar(con, "select count(*) from cms_by where by1 < 0 or by2 < 0 or by3 < 0") == 0  # early renewers' rows never loaded


def test_step1_error_recovered_and_used_for_model(tmp_path):
    from ratchet import validate

    synthetic.generate(tmp_path, seed=2, by_noise=0.03, hist_noise=0.02)
    result = validate.validate(build.connect(tmp_path, stage="full").sql("select * from validation").df())
    assert result["sigma_v_model_source"] == "step-1 check"
    assert 0.3 < result["sigma_v_model"] < 4.0 and result["sigma_v_model"] == result["step1"]["sigma_own"]


def test_risk_adjustment_changes_pull(built):
    """Regional spending is adjusted to the ACO's case mix (425.601(a)(8)(i)(C)), so pull differs from the unadjusted value."""
    _, _, m = built
    ok = m.pull_sql.notna()
    assert np.mean(np.abs(m.pull_sql[ok] - m.pull_unadjusted_sql[ok])) > 1.0


def test_date_macro_accepts_both_formats():
    import duckdb

    con = duckdb.connect()
    con.execute((build.config.SQL_DIR / "00_macros.sql").read_text())
    got = con.sql("select mdy('7/1/2019'), mdy('1/1/2019 0:00'), mdy('2022-01-01'), mdy('*')").fetchall()[0]
    assert [str(d) for d in got[:3]] == ["2019-07-01", "2019-01-01", "2022-01-01"] and got[3] is None


def test_by2_by3_variant_matches_numpy(tmp_path):
    """Robustness item 6: benchmark years 2020-2021 only."""
    truth = synthetic.generate(tmp_path, seed=1)
    frame = build.connect(tmp_path, stage="full", by_first=2020).sql("select aco_id, own, gain from expected_gain").df()
    m = frame.merge(truth.acos[["aco_id", "own_by23", "gain_by23"]], on="aco_id")
    assert (m.own.isna() == m.own_by23.isna()).all()
    np.testing.assert_allclose(m.own[m.own.notna()], m.own_by23[m.own.notna()], rtol=1e-6, atol=1e-3)
    np.testing.assert_allclose(m.gain[m.gain.notna()], m.gain_by23[m.gain.notna()], rtol=1e-6, atol=1e-3)


def test_census_region_and_balance(built):
    con, truth, _ = built
    frame = con.sql("select aco_id, census_region, share_85plus_2020, share_female_2020 from analysis").df()
    m = frame.merge(truth.acos[["aco_id", "census_region"]], on="aco_id", suffixes=("", "_np"))
    assert (m.census_region == m.census_region_np).all()
    assert frame.share_85plus_2020.between(0, 1).all() and frame.share_female_2020.between(0.4, 0.7).all()


def test_spending_by_agreement_year(tmp_path):
    truth = synthetic.generate(tmp_path, seed=1)
    table = build.connect(tmp_path, stage="full", descriptive=True).sql("select * from spending_by_agreement_year").df()
    acos = truth.acos
    early20 = ((acos.kind == "base20") & (acos.grp == "early")).sum()
    row = table[(table.start_year == 2020) & (table.agreement_year == 1) & table.early_renewer_from_2020]
    assert int(row.n_acos.iloc[0]) == early20
    # 2020 stayers reach agreement year 5 (PY2024); scheduled benchmark years are agreement years 3-5.
    stay = table[(table.start_year == 2020) & ~table.early_renewer_from_2020].set_index("agreement_year")
    assert int(stay.loc[5, "n_acos"]) == ((acos.kind == "base20") & (acos.grp == "stayer")).sum()
    assert set(table.loc[table.scheduled_benchmark_year, "agreement_year"]) == {3, 4, 5}
    # Early renewers out of 2020 agreements appear in their 2022 agreement too, still labeled.
    assert int(table[(table.start_year == 2022) & table.early_renewer_from_2020 & (table.agreement_year == 1)].n_acos.iloc[0]) == early20
