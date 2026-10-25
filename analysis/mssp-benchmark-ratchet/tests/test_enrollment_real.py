"""Groups and phase-in steps from the real enrollment files (already seen before registration; section 3)."""

import pytest

from ratchet import build, config

pytestmark = pytest.mark.skipif(not config.DEFAULT_DATA_DIR.exists(), reason="real snapshot not in cache")


@pytest.fixture(scope="module")
def con():
    return build.connect(stage="enrollment")


def test_groups_match_section_3(con):
    counts = dict(con.sql("select cohort || ' ' || grp, count(*) from groups group by all").fetchall())
    assert counts == {"2019-07 early": 11, "2020-01 early": 18, "2019-07 stayer": 159, "2020-01 stayer": 118, "2019-07 leaver": 19, "2020-01 leaver": 9}


def test_validation_sample_matches_section_4_4(con):
    assert build.scalar(con, "select count(*) from validation_sample") == 111
    overlap = build.scalar(con, "select count(*) from validation_sample join groups using (aco_id)")
    assert overlap == 0


def test_every_constructed_aco_has_a_phase_in_step(con):
    assert build.scalar(con, "select count(*) from phase_in where step is null") == 0
    # A 2022 reset is at least the second regionally adjusted benchmark for the 2019-07 and 2020-01 cohorts.
    assert build.scalar(con, "select min(step) from phase_in join base using (aco_id)") == 2
