"""The outcome lock, hash checks, and real column names (header rows only)."""

import shutil

import pytest

from ratchet import config, snapshot, synthetic

REAL = config.DEFAULT_DATA_DIR
needs_real = pytest.mark.skipif(not REAL.exists(), reason="real snapshot not in cache")


@needs_real
def test_real_enrollment_file_loads():
    assert snapshot.checked_path(REAL, config.ENROLLMENT_FILES["2021"]).exists()


@needs_real
@pytest.mark.parametrize("name", [*config.RESULTS_FILES.values(), *config.DESCRIPTIVE_RESULTS_FILES.values(), *config.COUNTY_FILES.values(), config.ASSIGNMENT_FILE])
def test_real_outcome_files_locked_before_registration(name, tmp_path):
    with pytest.raises(snapshot.OutcomeLockedError):
        snapshot.checked_path(REAL, name, registration=tmp_path / "REGISTRATION.md")


@needs_real
def test_modified_real_file_is_rejected(tmp_path):
    name = config.ENROLLMENT_FILES["2021"]
    shutil.copy(REAL / name, tmp_path / name)
    with open(tmp_path / name, "a") as fh:
        fh.write("\n")
    with pytest.raises(ValueError, match="does not match"):
        snapshot.checked_path(tmp_path, name)


def test_synthetic_outcome_files_load(tmp_path):
    synthetic.generate(tmp_path, seed=0, n_base=(20, 20), n_validation=10)
    assert snapshot.checked_path(tmp_path, config.RESULTS_FILES[2021], registration=tmp_path / "none").exists()


def _lower(columns):
    return {c.lower() for c in columns}


@needs_real
def test_real_headers_have_every_column_the_sql_reads():
    """Reads only the first row of each outcome file (column names, no values)."""
    groups = {
        "results": [config.RESULTS_FILES[y] for y in (2019, 2020, 2021, 2022)],
        "results_aco_num": [config.RESULTS_FILES[2016], config.RESULTS_FILES[2017]],
        "results_2018": [config.RESULTS_FILES[2018]],
        "results_2022_by": [config.RESULTS_FILES[2022]],
        "results_2023_2024": list(config.DESCRIPTIVE_RESULTS_FILES.values()),
        "enrollment_2021": [config.ENROLLMENT_FILES[k] for k in ("2021", "2022", "2023", "2024")],
        "county": list(config.COUNTY_FILES.values()),
        "assignment": [config.ASSIGNMENT_FILE],
    }
    for group, names in groups.items():
        for name in names:
            missing = _lower(synthetic.REQUIRED_COLUMNS[group]) - _lower(snapshot.read_header(REAL / name))
            assert not missing, f"{name} lacks {sorted(missing)}"
